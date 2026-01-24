from flask import Flask, render_template, request, redirect, url_for, session, flash
import utils
import os
from datetime import timedelta

application = Flask(__name__)
session_dir = os.path.join(os.getcwd(), "flask_session_data")
if not os.path.exists(session_dir):
    os.makedirs(session_dir)

application.config.update(
    SESSION_TYPE="filesystem",
    SESSION_FILE_DIR=session_dir,
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    SESSION_REFRESH_EACH_REQUEST=True,
    SESSION_COOKIE_SECURE=False
)
application.secret_key = 'super_secret_key'


@application.before_request
def save_last_visited_url():
    #Tracks the user's navigation history to allow 'Go Back' functionality.
    # List of endpoints to ignore for history tracking
    ignored_endpoints = ['static', 'go_back', 'log_out']
    if request.endpoint in ignored_endpoints:
        return

    # Initialize history if not present
    history = session.get('url_history', [])
    
    # Current URL
    current_url = request.url
    
    # Prevent saving the same page consecutively (e.g. refreshing)
    if not history or history[-1] != current_url:
        history.append(current_url)
        # Limit history size to prevent session bloat
        if len(history) > 20:
            history.pop(0)
        session['url_history'] = history

@application.route('/go_back')
def go_back():
    #Redirects the user to the previous page in their navigation history.
    history = session.get('url_history', [])
    if len(history) > 1:
        history.pop() # Current page
        session['url_history'] = history
        return redirect(history[-1])
    elif len(history) == 1:
        return redirect(history[0])
    return redirect('/')

@application.route('/log_out', methods=['POST','GET'])
def log_out():
    #Logs the user out by clearing the session and redirecting to home.
    session.clear()
    return redirect('/')

@application.route('/', methods=['POST','GET'])
def home_page():
    #Renders the homepage.
    #Handles flight search for customers and displays results.
    #If a manager is logged in, redirects to the manager homepage.
    if 'id' in session:
        return redirect('/manager_homepage')
    if request.method == 'POST':
        utils.update_db()
        flights = utils.get_flight("'Active'")
        for flight in flights:
            arrival_date, arrival_time, duration = utils.arrival(flight["fk_origin"], flight["fk_destination"], flight["departure_date"], flight["departure_time"])
            flight["arrival_date"] = str(arrival_date)
            flight["arrival_time"] = str(arrival_time)
            flight["duration"] = duration
        return render_template('customer_flights.html', flights = flights)
    else:
        # Reset history when visiting home page to prevent stuck Back button
        utils.clear_session()
        session['url_history'] = [request.url]
        with utils.db_cur() as cursor:
            cursor.execute("SELECT DISTINCT(origin) FROM route")
            session["origin"] = cursor.fetchall()
            cursor.execute("SELECT DISTINCT(destination) FROM route")
            session["destination"] = cursor.fetchall()
        return render_template('home_page.html', origin = session["origin"], destination = session["destination"])


@application.route('/seat_select', methods=['POST','GET'])
def seat_select():
    #Renders the seat selection page.
    #Initializes session data for the booking flow and fetches occupied seats.
    if 'id' in session:
        return redirect('/manager_homepage')
    
    # Clear previous seat selections to ensure fresh start
    session.pop('economy_seats', None)
    session.pop('business_seats', None)
    
    class_list_objs, session["departure_date"], session["departure_time"], session["plane_id"], session["origin"], session["destination"] = utils.seat_selection()
    arrival_date, arrival_time, duration = utils.arrival(session["origin"], session["destination"], session["departure_date"], session["departure_time"])
    session['arrival_date'] = str(arrival_date)
    session['arrival_time'] = str(arrival_time)
    session['duration'] = duration
    economy_occupied = class_list_objs[0].get_occupied(session["departure_date"], session["departure_time"])
    business_occupied = []
    if len(class_list_objs) == 2:
        business_occupied = class_list_objs[1].get_occupied(session["departure_date"], session["departure_time"])
    
    # Convert objects to dicts for serialization
    session["class_list"] = [vars(obj) for obj in class_list_objs]
    return render_template('seat_select.html', class_list = session["class_list"],
                           economy_occupied = economy_occupied,
                           business_occupied = business_occupied)

@application.route('/customer_summary', methods=['POST','GET'])
def customer_summary():
    #Displays the booking summary for customers.
    #Processes selected seats and calculates prices.
    #Requires login (via guest or existing customer).
    if 'id' in session:
        return redirect('/manager_homepage')
    
    # Ensure class_list contains dicts (fix for serialization error in legacy sessions)
    if 'class_list' in session and session['class_list'] and not isinstance(session['class_list'][0], dict):
        session['class_list'] = [vars(obj) for obj in session['class_list']]
    economy_choice = request.form.getlist('economy_choice')
    business_choice = request.form.getlist('business_choice')

    if economy_choice or business_choice:
        # If form data exists, parse it and update session
        economy_seats = []
        business_seats = []
        for seat in economy_choice:
            economy_seats.append(seat.split('|'))
        for seat in business_choice:
            business_seats.append(seat.split('|'))
        session['economy_seats'] = economy_seats
        session['business_seats'] = business_seats
    else:
        # If no form data, check if we already have seats in session (e.g. returning from login)
        economy_seats = session.get('economy_seats', [])
        business_seats = session.get('business_seats', [])
    
    error_msg = None
    if not economy_seats and not business_seats:
        error_msg = "Error: No seats selected."
    session['economy_price'], session['business_price'], session['total_price'] = utils.get_prices()
    
    if 'preview_order_id' not in session:
        session['preview_order_id'] = utils.generate_unique_order_id()

    if session.get('name') or session.get('email'):
        return render_template('customer_summary.html', order_id = session['preview_order_id'], economy_seats = economy_seats,
                               business_seats = business_seats,
                               plane_id = session['plane_id'],
                               departure_date = session['departure_date'],
                               departure_time = session['departure_time'],
                           origin = session['origin'],
                           destination = session['destination'],
                           error_msg = error_msg,
                           arrival_date = session['arrival_date'],
                           arrival_time = session['arrival_time'],
                           duration = session['duration'],
                           tickets = economy_seats + business_seats,
                           business_price = session['business_price'],
                           economy_price = session['economy_price'],
                           total_price = session['total_price'])
    else:
        return redirect('/guest_login')

@application.route('/guest_login', methods=['POST','GET'])
def guest_login():
    #Handles guest login during booking flow.
    #Captures or updates basic customer details in the database.
    if 'id' in session:
        return redirect('/manager_homepage')
    if request.method == 'POST':
        session['email'] = request.form.get('email')
        session['first_name'] = request.form.get('first_name').title()
        session['last_name'] = request.form.get('last_name').title()
        with utils.db_cur() as cursor:
            cursor.execute("SELECT * FROM customer WHERE email = %s", (session['email'],))
            customer = cursor.fetchone()
            if customer is None:
                cursor.execute("INSERT INTO customer (email, first_name, last_name) VALUES (%s, %s, %s)", (session['email'], session['first_name'], session['last_name']))
            else:
                cursor.execute("UPDATE customer SET first_name = %s, last_name = %s WHERE email = %s", (session['first_name'], session['last_name'], session['email']))
            return redirect('/customer_summary')
    if session.get('email'):
        return redirect('/customer_summary')
    return render_template('way_to_login.html')

@application.route('/add_flight', methods=['POST','GET'])
def add_flight():
    #Step 1 of flight creation for managers.
    #Allows selecting route and date/time, then shows available resources.
    if request.method == 'POST':
        utils.update_db()
        session["origin"] = request.form.get('origin')
        session["destination"] = request.form.get('destination')
        session["date"] = request.form.get('date')
        session["time"] = request.form.get('time')
        arrival_date, arrival_time, duration = utils.arrival(session["origin"], session["destination"], session["date"], session["time"])
        session["arrival_date"] = str(arrival_date)
        session["arrival_time"] = str(arrival_time)
        session["duration"] = duration
        available_pilots = utils.available_pilots(session["origin"], session["destination"], session["date"], session["time"])
        available_flight_attendants = utils.available_flight_attendants(session["origin"], session["destination"], session["date"], session["time"])
        available_plane =  utils.available_plane(session["origin"], session["destination"], session["date"], session["time"])
        return render_template('manager_assignments.html', available_flight_attendants = available_flight_attendants,
                               available_pilots = available_pilots, available_plane = available_plane, arrival_date = session["arrival_date"], arrival_time = session["arrival_time"], duration=session["duration"])
    else:
        with utils.db_cur() as cursor:
            cursor.execute("SELECT DISTINCT(origin) FROM route")
            origin = cursor.fetchall()
            cursor.execute("SELECT DISTINCT(destination) FROM route")
            destination = cursor.fetchall()
        return render_template('manager_flight.html', origin = origin, destination = destination)

@application.route('/manager_assignments', methods=['POST','GET'])
def manager_assignments():
    #Step 2 of flight creation.
    #Validates selected crew and plane against flight requirements.
    #Detects potential conflicts with other flights.
    error_msg = None 
    if request.method == 'POST':
        session["selected_pilot"] = request.form.getlist('selected_pilot')
        for i in range(len(session["selected_pilot"])):
            session["selected_pilot"][i] = session["selected_pilot"][i].split("|")
        session["selected_flight_attendant"] = request.form.getlist('selected_flight_attendant')
        for i in range(len(session["selected_flight_attendant"])):
            session["selected_flight_attendant"][i] = session["selected_flight_attendant"][i].split("|")
        session["plane"] = request.form.get('plane').split("|")
        if utils.is_long_flight(session["origin"], session["destination"]):
            if len(session["selected_pilot"]) != 3 or len(session["selected_flight_attendant"]) != 6:
                error_msg = "Error: Long flight must have 3 pilots and 6 flight attendants."
        else:
            if len(session["selected_pilot"]) != 2 or len(session["selected_flight_attendant"]) != 3:
                error_msg = "Error: Short flight must have 2 pilots and 3 flight attendants."
        
        if error_msg:
             available_pilots = utils.available_pilots(session["origin"], session["destination"], session["date"], session["time"])
             available_flight_attendants = utils.available_flight_attendants(session["origin"], session["destination"], session["date"], session["time"])
             available_plane =  utils.available_plane(session["origin"], session["destination"], session["date"], session["time"])
             return render_template('manager_assignments.html', available_flight_attendants = available_flight_attendants,
                                available_pilots = available_pilots, available_plane = available_plane, duration=session["duration"], error_msg=error_msg)

        affected_flights = []
        with utils.db_cur() as cursor:
             cursor.execute("""
                SELECT * FROM flight 
                WHERE fk_flight_plane_id = %s 
                AND status IN ('Active', 'Landed')
                AND (departure_date > %s OR (departure_date = %s AND departure_time >= %s))
                ORDER BY departure_date ASC, departure_time ASC
                LIMIT 1
            """, (session["plane"][0], session["date"], session["date"], session["time"]))
             next_flight = cursor.fetchone()
             if next_flight and next_flight['fk_origin'] != session["destination"]:
                  affected_flights.append(next_flight)

        return render_template('manager_summary.html',error_msg=error_msg, selected_pilots=session["selected_pilot"],
                                   selected_flight_attendants=session["selected_flight_attendant"], plane=session["plane"], 
                                   departure_date=session["date"], departure_time=session["time"], origin=session["origin"],
                                    destination=session["destination"], duration = session['duration'],
                                    arrival_date=session["arrival_date"], arrival_time=session["arrival_time"],
                                    affected_flights=affected_flights) 
    else:
        available_pilots = utils.available_pilots(session["origin"], session["destination"], session["date"], session["time"])
        available_flight_attendants = utils.available_flight_attendants(session["origin"], session["destination"], session["date"], session["time"])
        available_plane =  utils.available_plane(session["origin"], session["destination"], session["date"], session["time"])
        return render_template('manager_assignments.html', available_flight_attendants = available_flight_attendants,
                               available_pilots = available_pilots, available_plane = available_plane, duration=session["duration"])

@application.route('/manager_login', methods=['POST','GET'])
def manager_login():
    #Handles manager authentication.
    #Redirects to manager homepage on success.
    if request.method == 'POST':
        session["id"] = request.form.get('id')
        session["password"] = request.form.get('password')
        with utils.db_cur() as cursor:
            cursor.execute("SELECT * FROM manager WHERE id = %s AND password = %s", (session["id"], session["password"]))
            manager = cursor.fetchone()
            if manager:
                session["name"] = manager["first_name"] + " " + manager["last_name"]
                return redirect("/manager_homepage")
            else:
                return render_template('manager_login.html', error_msg="Invalid ID or password")
    else:
        return render_template('manager_login.html')

@application.route('/manager_homepage', methods=['POST','GET'])
def manager_homepage():
    #Renders the manager's dashboard.
    #Displays flight list with filtering and management options.
    if request.method == 'POST':
        utils.update_db()
        flights = utils.get_manager_flights()
        for flight in flights:
            arrival_date, arrival_time, duration = utils.arrival(flight["fk_origin"], flight["fk_destination"], flight["departure_date"], flight["departure_time"])
            flight["arrival_date"] = str(arrival_date)
            flight["arrival_time"] = str(arrival_time)
            flight["duration"] = duration
            flight['is_cancellable'] = utils.is_cancellable(flight['departure_date'], flight['departure_time'], flight['status'], 72)
        return render_template('manager_homepage.html', flights = flights, origin=session.get("origin"), destination=session.get("destination"))
    else:
        utils.clear_session()
        session['url_history'] = [request.url]
        with utils.db_cur() as cursor:
            cursor.execute("SELECT DISTINCT(origin) FROM route")
            session["origin"] = cursor.fetchall()
            cursor.execute("SELECT DISTINCT(destination) FROM route")
            session["destination"] = cursor.fetchall()
        return render_template('manager_homepage.html', origin=session["origin"], destination=session["destination"])

@application.route('/cancel_flight', methods=['POST'])
def cancel_flight():
    #Displays the confirmation page for flight cancellation.
    #Shows details of the flight and any affected future flights.
    session["selected_flight_key"] = request.form.get('selected_flight_key')
    plane_id, dep_date, dep_time = session["selected_flight_key"].split("|")
    
    with utils.db_cur() as cursor:
        cursor.execute("SELECT * FROM flight WHERE fk_flight_plane_id = %s AND departure_date = %s AND departure_time = %s", (plane_id, dep_date, dep_time))
        flight = cursor.fetchone()
        
        cursor.execute("""
            SELECT ac.id, ac.first_name, ac.last_name, ac.role 
            FROM air_crew_assignment aca
            JOIN air_crew ac ON aca.fk_air_crew_id = ac.id
            WHERE aca.fk_assignment_plane_id = %s 
            AND aca.fk_assignment_departure_time = %s 
            AND aca.fk_assignment_departure_date = %s
        """, (plane_id, dep_time, dep_date))
        assignments = cursor.fetchall()
        
        # Check for affected future flights (same plane, later time)
        cursor.execute("""
            SELECT * FROM flight 
            WHERE fk_flight_plane_id = %s 
            AND status = 'Active'
            AND (departure_date > %s OR (departure_date = %s AND departure_time > %s))
            ORDER BY departure_date ASC, departure_time ASC
        """, (plane_id, dep_date, dep_date, dep_time))
        affected_flights = cursor.fetchall()
        
        arrival_date, arrival_time, duration = utils.arrival(flight["fk_origin"], flight["fk_destination"], flight["departure_date"], flight["departure_time"])
        flight["arrival_date"] = arrival_date
        flight["arrival_time"] = arrival_time
        flight["duration"] = duration
        
    return render_template('cancel_flight.html', flight = flight, assignments = assignments, affected_flights=affected_flights)

@application.route('/confirm_cancel_flight', methods=['POST'])
def confirm_cancel_flight():
    #Executes the flight cancellation.
    #Updates statuses, refunds tickets (price=0), cancels orders, and releases crew.
    flight_key_parts = request.form.get('selected_flight_key').split("|")
    plane_id = flight_key_parts[0]
    date = flight_key_parts[1]
    time = flight_key_parts[2]
    
    with utils.db_cur() as cursor:
        # 1. Update flight status
        cursor.execute("UPDATE flight SET status = 'Cancelled' WHERE fk_flight_plane_id = %s AND departure_date = %s AND departure_time = %s", (plane_id, date, time))
        
        # 2. Update tickets price to 0
        cursor.execute("UPDATE ticket SET price = 0 WHERE fk_ticket_plane_id = %s AND fk_ticket_departure_date = %s AND fk_ticket_departure_time = %s", (plane_id, date, time))
        
        # 3. Update related orders status to 'Cancelled by manager'
        cursor.execute("""
            UPDATE `order`
            SET status = 'Cancelled by manager'
            WHERE order_id IN (
                SELECT fk_ticket_order_id
                FROM ticket
                WHERE fk_ticket_plane_id = %s AND fk_ticket_departure_date = %s AND fk_ticket_departure_time = %s
            )
        """, (plane_id, date, time))

        # 4. Delete crew assignments (releasing them)
        cursor.execute("DELETE FROM air_crew_assignment WHERE fk_assignment_plane_id = %s AND fk_assignment_departure_date = %s AND fk_assignment_departure_time = %s", (plane_id, date, time))
        
    flash("Flight successfully cancelled!", "success")
    return redirect("/manager_homepage")

@application.route('/add_employee', methods=['POST','GET'])
def add_employee():
    #Handles adding new crew members (pilots or flight attendants) to the system.
    if request.method == 'POST':
        id = request.form.get('id')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone_number = request.form.get('phone_number')
        house_number = request.form.get('house_number')
        city = request.form.get('city')
        street = request.form.get('street')
        long_flight_certificate = request.form.get('long_flight_certificate')
        role = request.form.get('role')
        with utils.db_cur() as cursor:
            cursor.execute("INSERT INTO air_crew (id, first_name, last_name, phone_number, hire_date, city, street, house_number, role, long_flight_certificate) VALUES (%s, %s, %s, %s, curdate(), %s, %s, %s, %s, %s)", (id, first_name, last_name, phone_number, city, street, house_number, role, long_flight_certificate))
        flash("Employee added successfully!", "success")
        return redirect("/manager_homepage")
    else:
        return render_template('add_employee.html')

@application.route('/add_plane', methods=['POST','GET'])
def add_plane():
    #Handles adding new planes to the fleet.
    #Creates both the plane record and its seating configuration (classes).
    if request.method == 'POST':
        plane_id = request.form.get('plane_id')
        purchase_date = request.form.get('purchase_date')
        size = request.form.get('size')
        manufacturer = request.form.get('manufacturer')
        economy_rows = request.form.get('economy_rows')
        economy_cols = request.form.get('economy_cols')
        business_rows = request.form.get('business_rows')
        business_cols = request.form.get('business_cols')
        
        with utils.db_cur() as cursor:
            cursor.execute("INSERT INTO plane (plane_id, purchase_date, size, manufacturer) VALUES (%s, %s, %s, %s)", (plane_id, purchase_date, size, manufacturer))
            if size == 'small':
                cursor.execute("INSERT INTO class (fk_plane_id, type, number_of_col, number_of_row) VALUES (%s, %s, %s, %s)", (plane_id, 'Economy', economy_cols, economy_rows))
            elif size == 'large':
                cursor.execute("INSERT INTO class (fk_plane_id, type, number_of_col, number_of_row) VALUES (%s, %s, %s, %s)", (plane_id, 'Economy', economy_cols, economy_rows))
                cursor.execute("INSERT INTO class (fk_plane_id, type, number_of_col, number_of_row) VALUES (%s, %s, %s, %s)", (plane_id, 'Business', business_cols, business_rows))
        flash("Plane added successfully!", "success")
        return redirect("/manager_homepage")
    else:
        return render_template('add_plane.html')

@application.route('/finalize_flight', methods=['POST','GET'])
def finalize_flight():
    #Final step of flight creation.
    #Persists flight, crew assignments, and ticket prices to the database.
    flight = utils.Flight(session["plane"][0], session["time"], session["date"], session["origin"], session["destination"])
    
    pilots_ids = [p[0] for p in session["selected_pilot"]]
    attendants_ids = [fa[0] for fa in session["selected_flight_attendant"]]
    
    economy_price = request.form.get('economy_price')
    business_price = request.form.get('business_price')
    
    flight.flight_create(pilots_ids, attendants_ids, economy_price, business_price)
    utils.clear_session()
    flash("Flight created successfully!", "success")
    return redirect("/manager_homepage")

@application.route('/finalize_customer', methods=['POST','GET'])
def finalize_customer():
    #Finalizes the customer booking process.
    #Creates the order and tickets in the database.
    if 'id' in session:
        return redirect('/manager_homepage')
        
    order_id = session.get('preview_order_id')
    order = utils.order(session["email"], session["total_price"], order_id=order_id)
    session.pop('preview_order_id', None)
    order_id = order.order_id
    order.order_create()
    for ticket in session["economy_seats"]:
        ticket = utils.ticket(ticket[0].split("-")[0], ticket[0].split("-")[1], order_id, session["plane_id"], "Economy", session["departure_time"], session["departure_date"], session["economy_price"]) 
        ticket.ticket_create()
    for ticket in session["business_seats"]:
        ticket = utils.ticket(ticket[0].split("-")[0], ticket[0].split("-")[1], order_id, session["plane_id"], "Business", session["departure_time"], session["departure_date"], session["business_price"]) 
        ticket.ticket_create()
    utils.clear_session() 
    flash("Order placed successfully!", "success")
    return redirect("/")

@application.route('/customer_login', methods=['POST','GET'])
def customer_login():
    #Handles registered customer login.
    #Redirects to previous flow step (booking) or home.
    if 'id' in session:
        return redirect('/manager_homepage')
    if request.method == 'POST':
        session["email"] = request.form.get('email')
        session["password"] = request.form.get('password')
        with utils.db_cur() as cursor:
            cursor.execute("SELECT * FROM signed_customer sc JOIN customer c ON sc.fk_signed_email = c.email WHERE fk_signed_email = %s AND password = %s", (session["email"], session["password"]))
            customer = cursor.fetchone()
            if customer:
                session["name"] = customer["first_name"] + " " + customer["last_name"]
                # Redirect to the return URL if it exists, otherwise home
                return_url = session.get('flow_return_url', '/')
                session.pop('flow_return_url', None)
                
                # Prevent redirect loop back to login choice pages
                if '/way_to_login' in return_url or '/guest_login' in return_url:
                    if session.get('economy_seats') or session.get('business_seats'):
                         return redirect('/customer_summary')
                    else:
                         return redirect('/')
                
                return redirect(return_url)
            else:
                return render_template('customer_login.html', error_msg="Invalid email or password")
    else:
        # Save the previous page as the return URL, unless we are already in the flow
        if 'flow_return_url' not in session:
            url_history = session.get('url_history', [])
            # If we have history, the previous page (index -2) is where we came from. 
            # If history is just [current], then presumably home is safe.
            if len(url_history) >= 2:
                session['flow_return_url'] = url_history[-2]
            else:
                session['flow_return_url'] = '/'
        return render_template('customer_login.html')

@application.route('/customer_signup', methods=['POST','GET'])
def customer_signup():
    #Step 1 of customer registration.
    #Collected personal details and credentials.
    if 'id' in session:
        return redirect('/manager_homepage')
    if request.method == 'POST':
        session["email"] = request.form.get('email')
        session["first_name"] = request.form.get('first_name').title()
        session["last_name"] = request.form.get('last_name').title()
        session["num_of_phone_numbers"] = int(request.form.get('num_of_phone_numbers'))
        session["passport_number"] = request.form.get('passport_number')
        session["birth_date"] = request.form.get('birth_date')
        session["password"] = request.form.get('password')
        with utils.db_cur() as cursor:
            cursor.execute("SELECT * FROM customer WHERE email = %s", (session["email"],))
            customer = cursor.fetchone()
            if customer:
                cursor.execute("SELECT * FROM signed_customer WHERE fk_signed_email = %s", (session["email"],))
                signed_customer = cursor.fetchone()
                if signed_customer:
                    return redirect('signup.html', error_msg="Email already exists")
                cursor.execute("UPDATE customer SET first_name = %s, last_name = %s WHERE email = %s", (session["first_name"], session["last_name"], session["email"]))
                cursor.execute("INSERT INTO signed_customer (fk_signed_email, passport, birth_date, sign_up_date, password) VALUES (%s, %s, %s, curdate(), %s)", (session["email"], session["passport_number"], session["birth_date"], session["password"]))
                return redirect("/final_signup")
            else:
                cursor.execute("INSERT INTO customer (email, first_name, last_name) VALUES (%s, %s, %s)", (session["email"], session["first_name"], session["last_name"]))
                cursor.execute("INSERT INTO signed_customer (fk_signed_email, passport, birth_date, sign_up_date, password) VALUES (%s, %s, %s, curdate(), %s)", (session["email"], session["passport_number"], session["birth_date"], session["password"]))
                return redirect("/final_signup")
    else:
        # Save entry point for signup flow
        if 'flow_return_url' not in session:
            url_history = session.get('url_history', [])
            if len(url_history) >= 2:
                session['flow_return_url'] = url_history[-2]
            else:
                session['flow_return_url'] = '/'
        
        # Check if we came from the booking flow login page
        if request.referrer and '/guest_login' in request.referrer:
            session['signup_redirect_to_booking'] = True
        elif request.referrer and '/customer_signup' not in request.referrer:
            # Clear flag if coming from somewhere else (unless reloading same page)
            session.pop('signup_redirect_to_booking', None)
            
        return render_template('signup.html')

@application.route('/final_signup', methods=['POST','GET'])
def final_signup():
    #Step 2 of customer registration.
    #Collects phone numbers and finalizes the account creation.
    if 'id' in session:
        return redirect('/manager_homepage')
    if request.method == 'POST':
        session["phone_numbers"] = []
        for i in range(session["num_of_phone_numbers"]):
            session["phone_numbers"].append(request.form.get(f'phone_number_{i+1}'))
        with utils.db_cur() as cursor:
            for phone_number in session["phone_numbers"]:
                cursor.execute("INSERT INTO phone_number (phone_number, fk_phone_email) VALUES (%s, %s)", (phone_number, session["email"]))
        session["name"] = session["first_name"] + " " + session["last_name"]
        
        # Redirect to the return URL saved at start of signup flow
        return_url = session.get('flow_return_url', '/')
        session.pop('flow_return_url', None)

        if session.pop('signup_redirect_to_booking', None):
             return redirect('/customer_summary')

        return redirect(return_url)
    else:
        return render_template('final_signup.html')
    
@application.route('/order_management', methods=['POST','GET'])
def order_management():
    #Retrieves and displays a single order by ID for the guest/user to view status.
    #Checks cancellation eligibility.
    if 'id' in session:
        return redirect('/manager_homepage')
    if request.method == 'POST':
        error_msg = None
        email = request.form.get('email')
        session['order_id'] = request.form.get('order_number')
        is_cancellable = False
        order_status = None
        with utils.db_cur() as cursor:
            cursor.execute("SELECT * FROM ticket WHERE fk_ticket_order_id = %s", (session['order_id'],))
            tickets = cursor.fetchall()
            for ticket in tickets:
                ticket['fk_ticket_departure_date'] = str(ticket['fk_ticket_departure_date'])
                ticket['fk_ticket_departure_time'] = str(ticket['fk_ticket_departure_time'])
            session['tickets'] = tickets
            
            if not session['tickets']:
                error_msg = "Order not found"
            else:
                cursor.execute("SELECT status FROM `order` WHERE order_id = %s", (session['order_id'],))
                order_info = cursor.fetchone()
                order_status = order_info['status'] if order_info else 'Unknown'
                is_cancellable = utils.is_cancellable(session['tickets'][0]['fk_ticket_departure_date'], session['tickets'][0]['fk_ticket_departure_time'], order_status, 36)
                session['total_price'] = sum(ticket['price'] for ticket in session['tickets'])    
        return render_template('order_management.html',tickets = session['tickets'], error_msg=error_msg, is_cancellable=is_cancellable, total_price=session.get('total_price', None), status=order_status)
    else:
        utils.update_db()
        return render_template('order_management.html')    
 
@application.route('/purchase_history', methods=['POST','GET'])
def purchase_history():

    #Displays the purchase history for a logged-in customer.
    #Allows filtering by status and sorting by date.
    if 'id' in session:
        return redirect('/manager_homepage')
    if request.method == 'POST':
        status = request.form.get('status')
        if not status:
            query = "SELECT * FROM `order` WHERE fk_order_email = %s ORDER BY order_date DESC"
            with utils.db_cur() as cursor:
                cursor.execute(query, (session['email'],))
                session['orders'] = cursor.fetchall()
                for order in session['orders']:
                    order['order_date'] = str(order['order_date'])
                    order['total_price'], order['origin'], order['destination'], order['departure_time'], order['departure_date'], order['arrival_date'], order['arrival_time'], order['duration'] = utils.order_details(order['order_id'])
        else:
            query = "SELECT * FROM `order` WHERE status = %s AND fk_order_email = %s ORDER BY order_date DESC"
            with utils.db_cur() as cursor:
                cursor.execute(query, (status, session['email']))
                session['orders'] = cursor.fetchall()
                for order in session['orders']:
                    order['order_date'] = str(order['order_date'])
                    order['total_price'], order['origin'], order['destination'], order['departure_time'], order['departure_date'], order['arrival_date'], order['arrival_time'], order['duration'] = utils.order_details(order['order_id'])
        return render_template('purchase_history.html')
    else:
        with utils.db_cur() as cursor:
            cursor.execute("SELECT * FROM `order` WHERE fk_order_email = %s", (session['email'],))
            session['orders'] = cursor.fetchall()
            for order in session['orders']:
                order['order_date'] = str(order['order_date'])
                order['total_price'], order['origin'], order['destination'], order['departure_time'], order['departure_date'], order['arrival_date'], order['arrival_time'], order['duration'] = utils.order_details(order['order_id'])
        return render_template('purchase_history.html')

@application.route('/cancel_order', methods=['POST','GET'])
def cancel_order():
    #Handles customer initiated order cancellation.
    #Refunds 5% of cost and updates status if eligible.
    if 'id' in session:
        return redirect('/manager_homepage')
    if request.method == 'POST':
        with utils.db_cur() as cursor:
            # Check if order is Active
            cursor.execute("SELECT status FROM `order` WHERE order_id = %s", (session['order_id'],))
            order_info = cursor.fetchone()
            
            if order_info and order_info['status'] == 'Active':
                cursor.execute("UPDATE ticket SET price = price * 0.05 WHERE fk_ticket_order_id = %s", (session['order_id'],))
                cursor.execute("UPDATE `order` SET status = 'Cancelled by customer', order_cost = order_cost * 0.05 WHERE order_id = %s", (session['order_id'],))
                flash("Order cancelled successfully!", "success")
                return redirect("/order_management")
            else:
                 # Order not active, cannot cancel
                 return render_template('cancel_order.html', session=session, error_msg="Only Active orders can be cancelled.")
    else:
        return render_template('cancel_order.html', session = session)

@application.route('/reports', methods=['POST','GET'])
def reports():
    #Renders status reports for managers.
    #Aggregates data based on user selection.
    if request.method == 'POST':
        result1, result2, result3, result4, result5 = utils.reports()   
        return render_template('reports.html', result1=result1, result2=result2, result3=result3, result4=result4, result5=result5)
    else:
        utils.update_db()
        return render_template('reports.html')

if __name__ == '__main__':
    print("Running on http://127.0.0.1:5000")
    application.run(debug=True)