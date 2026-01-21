import mysql.connector
import random
import string
from flask import Flask, render_template, request, redirect, url_for, session
from contextlib import contextmanager
from datetime import datetime, timedelta, date, time
import os

DB_HOST = os.environ.get("DB_HOST", "flytaudb.covk0aacgf9k.us-east-1.rds.amazonaws.com")
DB_USER = os.environ.get("DB_USER", "admin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "admin-flytau")
DB_NAME = os.environ.get("DB_NAME", "flytaudb") 
@contextmanager
def db_cur():
    mydb = None
    cursor = None
    try:
        mydb = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            autocommit=True
        )
        cursor = mydb.cursor(dictionary=True)
        yield cursor
    except mysql.connector.Error as err:
        raise err
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()

def get_flight(status):
    session['origin'] = request.form.get('origin')
    session['destination'] = request.form.get('destination')
    session['date'] = request.form.get('date')
    query = f'SELECT * FROM flight WHERE status = {status}'
    params = []
    if session['origin']:
        query += " AND fk_origin = %s"
        params.append(session['origin'])

    if session['destination']:
        query += " AND fk_destination = %s"
        params.append(session['destination'])

    if session['date']:
        query += " AND departure_date = %s"
        params.append(session['date'])

    with db_cur() as cursor:
        cursor.execute(query, tuple(params))
        return cursor.fetchall()

def get_manager_flights():
    params = []
    # Use different keys for search parameters to avoid overwriting the lists of all origins/destinations
    session['search_origin'] = request.form.get('origin')
    session['search_destination'] = request.form.get('destination')
    session['search_date'] = request.form.get('date')
    session['search_status'] = request.form.getlist('status')
    with db_cur() as cursor:
        query = "SELECT * FROM flight WHERE 1=1 "
        if session['search_origin']:
            query += "AND fk_origin = %s "
            params.append(session['search_origin'])
        if session['search_destination']:
            query += "AND fk_destination = %s "
            params.append(session['search_destination'])
        if session['search_date']:
            query += "AND departure_date = %s "
            params.append(session['search_date'])
        if session['search_status']:
            placeholders = ', '.join(['%s'] * len(session['search_status']))
            query += f" AND status IN ({placeholders})"
            params.extend(session['search_status'])
        cursor.execute(query, tuple(params))
        return cursor.fetchall()


class plane_class:
    def __init__(self, plane_id, type, rows, cols):
        self.plane_id = plane_id
        self.type = type
        self.rows = rows
        self.cols = cols



    def get_occupied(self, date, time):
        with db_cur() as cursor:
            cursor.execute("SELECT `row`, `col` FROM ticket WHERE fk_ticket_plane_id = %s "
                           "AND fk_ticket_class = %s AND fk_ticket_departure_time = %s "
                           "AND fk_ticket_departure_date = %s", (self.plane_id, self.type, time, date))
            occupied = []
            seats = cursor.fetchall()
            for i in seats:
                occupied.append(str(i['row']) + '-' + str(i['col']))
            return occupied



def seat_selection():
    flight_key = request.form.get('selected_flight_key')
    if flight_key:
        selected_flight = flight_key.split('|')
        plane_id, departure_date, departure_time = selected_flight
    elif 'plane_id' in session and 'departure_date' in session and 'departure_time' in session:
        # Fallback to session
        plane_id = session['plane_id']
        departure_date = session['departure_date']
        departure_time = session['departure_time']
    else:
        return None, None, None, None, None, None
    with db_cur() as cursor:
        cursor.execute(" SELECT type, number_of_row, number_of_col FROM class WHERE fk_plane_id = %s"
                       " ORDER BY type DESC", (plane_id,))
        classes = cursor.fetchall()
        class_list = []
        for i in classes:
            class_list.append(plane_class(plane_id, i['type'], i['number_of_row'], i['number_of_col']))
            
        # Also fetch origin and destination for the specific flight
        cursor.execute("SELECT fk_origin, fk_destination FROM flight WHERE fk_flight_plane_id = %s AND departure_date = %s AND departure_time = %s", (plane_id, departure_date, departure_time))
        flight_info = cursor.fetchone()
        
    return class_list, str(departure_date), str(departure_time), plane_id, flight_info['fk_origin'], flight_info['fk_destination']


def is_long_flight(origin, destination):
    with db_cur() as cursor:
        cursor.execute("SELECT duration FROM route WHERE origin = %s AND destination = %s", (origin, destination))
        duration = cursor.fetchone()
        if duration and duration["duration"] >= 360:
            return True            
        return False

def arrival(origin, destination, departure_date, departure_time):
    with db_cur() as cursor:
        cursor.execute("SELECT duration FROM route WHERE origin = %s AND destination = %s", (origin, destination))
        result = cursor.fetchone()
    
    if not result:
        return None, None, None
        
    duration = result["duration"]

    # 1. טיפול בתאריך
    if isinstance(departure_date, str):
        departure_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
        
    # 2. טיפול בשעה (התיקון נמצא כאן)
    if isinstance(departure_time, str):
        try:
            # מנסים קודם כל פורמט מלא עם שניות (08:00:00)
            departure_time = datetime.strptime(departure_time, '%H:%M:%S').time()
        except ValueError:
            # אם זה נכשל, מנסים פורמט קצר בלי שניות (08:00)
            departure_time = datetime.strptime(departure_time, '%H:%M').time()
            
    elif isinstance(departure_time, timedelta):
        # טיפול במקרה שהדאטה בייס מחזיר timedelta
        departure_time = (datetime.min + departure_time).time()
        
    if not departure_date or not departure_time:
        return None, None, None 
        
    # 3. ביצוע החישוב
    full_departure = datetime.combine(departure_date, departure_time)
    full_arrival = full_departure + timedelta(minutes=duration)
    
    # החזרה כ-String כדי למנוע קריסות ב-Session
    return full_arrival.date(), full_arrival.time(), duration

def check_availability(entity_id, entity_type, origin, destination, target_dep_date, target_dep_time):
    # Helper to check constraints for a single entity
    target_dep_dt = datetime.combine(target_dep_date, target_dep_time)
    
    # Calculate target arrival to check for overlaps
    target_arr_date, target_arr_time, _ = arrival(origin, destination, target_dep_date, target_dep_time)
    if not target_arr_date:
        return False # Invalid route
    target_arr_dt = datetime.combine(target_arr_date, target_arr_time)

    with db_cur() as cursor:
        # 1. Check for PREVIOUS flight (to determine location and readiness)
        # We look for the latest flight that departed BEFORE our target departure
        # Note: We need careful handling of dates/times for comparison in SQL
        query_prev = """
            SELECT F.fk_origin, F.fk_destination, F.departure_date, F.departure_time, F.status
            FROM flight F
            LEFT JOIN air_crew_assignment ACA ON ACA.fk_assignment_plane_id = F.fk_flight_plane_id
            AND ACA.fk_assignment_departure_date = F.departure_date
            AND ACA.fk_assignment_departure_time = F.departure_time 
            WHERE 1=1
        """
        
        if entity_type == 'plane':
             query_prev = """
                SELECT fk_origin, fk_destination, departure_date, departure_time, status
                FROM flight
                WHERE fk_flight_plane_id = %s
             """
        else:
             query_prev += " AND ACA.fk_air_crew_id = %s"
             
        # Add Time Filter and Sort
        query_prev += " AND TIMESTAMP(departure_date, departure_time) < %s ORDER BY departure_date DESC, departure_time DESC LIMIT 1"
        
        cursor.execute(query_prev, (entity_id, target_dep_dt))
        prev_flight = cursor.fetchone()
        
        # Default state (new employee/plane) -> Assume available at Israel or implicitly 'Available'
        # Prompt implies checking if they "landed", suggesting we must chain. 
        # But for strictly new entities, we can default to available if no history.
        curr_loc = "Israel" 
        ready_dt = datetime.min
        
        if prev_flight:
            prev_status = prev_flight['status']
            p_origin = prev_flight['fk_origin']
            p_dest = prev_flight['fk_destination']
            p_date = prev_flight['departure_date']
            p_time = prev_flight['departure_time']
            # p_time might be timedelta
            if isinstance(p_time, timedelta):
                p_time = (datetime.min + p_time).time()
            
            p_dep_dt = datetime.combine(p_date, p_time)

            if prev_status == 'Cancelled':
                # If cancelled, they never left origin.
                curr_loc = p_origin
                ready_dt = p_dep_dt # Effectively available immediately/at dep time
            else:
                # Active or Landed
                curr_loc = p_dest
                # Calculate arrival
                p_arr_date, p_arr_time, _ = arrival(p_origin, p_dest, p_date, p_time)
                if p_arr_date:
                     p_arr_dt = datetime.combine(p_arr_date, p_arr_time)
                     ready_dt = p_arr_dt + timedelta(hours=2) # 2 hours rest
                else:
                     # Should not happen for valid flights
                     ready_dt = p_dep_dt + timedelta(hours=5) # Fallback

        if curr_loc != origin:
            return False
        if ready_dt > target_dep_dt:
            return False

        # 2. Check for FUTURE/OVERLAPPING flights
        # They cannot be assigned to another flight that starts BEFORE we land + 2h
        # And we cannot overlap with an existing flight that starts BEFORE we depart (handled by prev check usually, but double check overlaps)
        
        query_overlap = """
            SELECT F.departure_date, F.departure_time
            FROM flight F
            LEFT JOIN air_crew_assignment ACA ON ACA.fk_assignment_plane_id = F.fk_flight_plane_id
            AND ACA.fk_assignment_departure_date = F.departure_date
            AND ACA.fk_assignment_departure_time = F.departure_time 
            WHERE 1=1
        """
        if entity_type == 'plane':
             query_overlap = """
                SELECT departure_date, departure_time
                FROM flight
                WHERE fk_flight_plane_id = %s
             """
        else:
             query_overlap += " AND ACA.fk_air_crew_id = %s"
        
        # We need to find any flight that starts AFTER our previous reference (so we don't pick up the past flight)
        # AND starts BEFORE our projected available time (Target Arrival + buffer?)
        # Actually simplest check: 
        # Is there any flight where:
        #   (ExistingStart < TargetEnd) AND (ExistingEnd > TargetStart)
        # But calculating ExistingEnd for all is heavy.
        # Simplified: Check if any flight starts in [TargetStart, TargetEnd + 2h]
        
        query_next = query_overlap + " AND TIMESTAMP(departure_date, departure_time) >= %s ORDER BY departure_date ASC, departure_time ASC LIMIT 1"
        cursor.execute(query_next, (entity_id, target_dep_dt))
        next_flight = cursor.fetchone()
        
        if next_flight:
            n_date = next_flight['departure_date']
            n_time = next_flight['departure_time']
            if isinstance(n_time, timedelta):
                n_time = (datetime.min + n_time).time()
            n_dep_dt = datetime.combine(n_date, n_time)
            
            # We must Land + 2h before Next Start
            if (target_arr_dt + timedelta(hours=2)) > n_dep_dt:
                return False

    return True

def available_pilots(origin, destination, date, time):
    if is_long_flight(origin, destination):
        query_pilots = "SELECT id, first_name, last_name FROM air_crew WHERE role = 'Pilot' AND long_flight_certificate = 1"
    else:
        query_pilots = "SELECT id, first_name, last_name FROM air_crew WHERE role = 'Pilot'"
    
    try:
        if date and time:
            dep_date = datetime.strptime(date, '%Y-%m-%d').date()
            if len(time) > 5:
                dep_time = datetime.strptime(time, '%H:%M:%S').time()
            else:
                 dep_time = datetime.strptime(time, '%H:%M').time()
        else:
            return []
    except ValueError:
        return []

    relevant_pilots = []
    with db_cur() as cursor:
        cursor.execute(query_pilots)
        all_pilots = cursor.fetchall()
        for pilot in all_pilots:
            if check_availability(pilot['id'], 'crew', origin, destination, dep_date, dep_time):
                relevant_pilots.append(pilot)
    return relevant_pilots

def available_flight_attendants(origin, destination, date, time):
    if is_long_flight(origin, destination):
        query_fa = "SELECT id, first_name, last_name FROM air_crew WHERE role = 'Flight Attendant' AND long_flight_certificate = 1"
    else:
        query_fa = "SELECT id, first_name, last_name FROM air_crew WHERE role = 'Flight Attendant'"
    
    try:
        if date and time:
            dep_date = datetime.strptime(date, '%Y-%m-%d').date()
            if len(time) > 5:
                dep_time = datetime.strptime(time, '%H:%M:%S').time()
            else:
                 dep_time = datetime.strptime(time, '%H:%M').time()
        else:
            return []
    except ValueError:
        return []

    relevant_fa = []
    with db_cur() as cursor:
        cursor.execute(query_fa)
        all_fa = cursor.fetchall()
        for fa in all_fa:
             if check_availability(fa['id'], 'crew', origin, destination, dep_date, dep_time):
                relevant_fa.append(fa)
    return relevant_fa

def available_plane(origin, destination, date, time):
    if is_long_flight(origin, destination):
        query_plane = "SELECT * FROM plane WHERE size= 'Large'"
    else:
        query_plane = "SELECT * FROM plane"
    
    try:
        if date and time:
            dep_date = datetime.strptime(date, '%Y-%m-%d').date()
            if len(time) > 5:
                dep_time = datetime.strptime(time, '%H:%M:%S').time()
            else:
                 dep_time = datetime.strptime(time, '%H:%M').time()
        else:
             return []
    except ValueError:
         return []
    
    relevant_planes = []
    with db_cur() as cursor:
        cursor.execute(query_plane)
        all_planes = cursor.fetchall()
        for plane in all_planes:
            if check_availability(plane['plane_id'], 'plane', origin, destination, dep_date, dep_time):
                relevant_planes.append(plane)
    return relevant_planes

class Flight:
    def __init__(self, plane_id, departure_time, departure_date, origin, destination):
        self.plane_id = plane_id
        self.departure_time = departure_time
        self.departure_date = departure_date
        self.origin = origin
        self.destination = destination
        self.status = "Active"
    def flight_create(self, pilots_ids, attendants_ids, economy_price, business_price):
        with db_cur() as cursor:
            # 1. Insert Flight
            cursor.execute("INSERT INTO flight (fk_flight_plane_id, departure_time, departure_date, fk_origin, fk_destination, status) VALUES (%s, %s, %s, %s, %s, %s)", (self.plane_id, self.departure_time, self.departure_date, self.origin, self.destination, self.status))
            
            # 2. Insert Air Crew Assignments
            # Pilots
            for p_id in pilots_ids:
                cursor.execute("INSERT INTO air_crew_assignment (fk_assignment_plane_id, fk_assignment_departure_date, fk_assignment_departure_time, fk_air_crew_id) VALUES (%s, %s, %s, %s)", (self.plane_id, self.departure_date, self.departure_time, p_id))
            # Flight Attendants
            for fa_id in attendants_ids:
                cursor.execute("INSERT INTO air_crew_assignment (fk_assignment_plane_id, fk_assignment_departure_date, fk_assignment_departure_time, fk_air_crew_id) VALUES (%s, %s, %s, %s)", (self.plane_id, self.departure_date, self.departure_time, fa_id))
            
            # 3. Insert Flight Prices
            # Economy
            cursor.execute("INSERT INTO flight_price (fk_price_plane_id, fk_price_departure_date, fk_price_departure_time, fk_price_class, price) VALUES (%s, %s, %s, %s, %s)", (self.plane_id, self.departure_date, self.departure_time, 'Economy', economy_price))
            # Business
            if business_price:
                cursor.execute("INSERT INTO flight_price (fk_price_plane_id, fk_price_departure_date, fk_price_departure_time, fk_price_class, price) VALUES (%s, %s, %s, %s, %s)", (self.plane_id, self.departure_date, self.departure_time, 'Business', business_price))

class ticket:
    def __init__(self, row, col, order_id, plane_id, class_type, departure_time, departure_date, price):
        self.row = row
        self.col = col
        self.order_id = order_id
        self.plane_id = plane_id
        self.class_type = class_type
        self.departure_time = departure_time
        self.departure_date = departure_date
        self.price = price

    def ticket_create(self):
        with db_cur() as cursor:
            cursor.execute("INSERT INTO ticket (`row`, `col`, fk_ticket_order_id, fk_ticket_plane_id, fk_ticket_class, fk_ticket_departure_time, fk_ticket_departure_date, price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (self.row, self.col, self.order_id, self.plane_id, self.class_type, self.departure_time, self.departure_date, self.price))


def generate_unique_order_id():
    while True:
        chars = string.ascii_uppercase + string.digits
        order_id = ''.join(random.choices(chars, k=6))
        with db_cur() as cursor:
            sql = "SELECT 1 FROM `order` WHERE order_id = %s LIMIT 1"
            cursor.execute(sql, (order_id,))
            exists = cursor.fetchone()
            if not exists:
                return order_id
class order:
    def __init__(self, email, cost, order_id=None):
        if order_id:
            self.order_id = order_id
        else:
            self.order_id = generate_unique_order_id()
        self.status = "Active"
        self.email = email
        self.cost = cost
        self.date = datetime.now().strftime('%Y-%m-%d')

    def order_create(self):
        with db_cur() as cursor:
            cursor.execute("INSERT INTO `order` (order_id, fk_order_email, status, order_date, order_cost) VALUES (%s, %s, %s, %s, %s)", (self.order_id, self.email, self.status, self.date, self.cost))
        
def get_prices():
    economy_price = 0
    business_price = 0
    query = "SELECT fk_price_class, price FROM flight_price WHERE fk_price_plane_id = %s AND fk_price_departure_date = %s AND fk_price_departure_time = %s"
    with db_cur() as cursor:
        cursor.execute(query, (session['plane_id'], session['departure_date'], session['departure_time']))
        prices = cursor.fetchall()
        
        if not prices:
            print(f"Error: No prices found for plane {session['plane_id']} on {session['departure_date']} at {session['departure_time']}")
            return 0, 0, 0
            
        for p in prices:
            if p['fk_price_class'] == 'Economy':
                economy_price = p['price']
            elif p['fk_price_class'] == 'Business':
                business_price = p['price']
                
    # Using 'business_seats' to match main.py's recent changes
    total_price = economy_price * len(session.get('economy_seats', [])) + business_price * len(session.get('business_seats', []))            
    return economy_price, business_price, total_price
def insert_new_tickets(plane_id, departure_date, departure_time, economy_seats, business_seats):
    query = "INSERT INTO ticket (`row`, `col`, fk_plane_id, class, fk_departure_time, fk_departure_date) VALUES (%s, %s, %s, %s, %s, %s)"

    with db_cur() as cursor:
        if economy_seats:
            for seat in economy_seats:
                cursor.execute(query, (seat[0], seat[1], plane_id, 'Economy', departure_time, departure_date))
        
        if business_seats:
            for seat in business_seats:
                cursor.execute(query, (seat[0], seat[1], plane_id, 'Business', departure_time, departure_date))

def is_cancellable(flight_date, flight_time, status, hours_limit):
    if status != 'Active' and status != 'Full':
        return False
    if isinstance(flight_date, str):
        try:
            flight_date = datetime.strptime(flight_date, '%Y-%m-%d').date()
        except ValueError:
            return False
    if isinstance(flight_time, timedelta):
        flight_time = (datetime.min + flight_time).time()
    elif isinstance(flight_time, str):
        try:
            if len(flight_time) > 5:
                flight_time = datetime.strptime(flight_time, '%H:%M:%S').time()
            else:
                flight_time = datetime.strptime(flight_time, '%H:%M').time()
        except ValueError:
            return False
    if not isinstance(flight_date, date) or not isinstance(flight_time, time):
        return False
    try:
        flight_dt = datetime.combine(flight_date, flight_time)
    except Exception:
        return False
    current_time = datetime.now()
    time_remaining = flight_dt - current_time
    if time_remaining.total_seconds() < 0:
        return False
    return time_remaining > timedelta(hours=hours_limit)

def order_details(order_id):
    with db_cur() as cursor:
        cursor.execute("SELECT price, fk_ticket_plane_id, fk_ticket_departure_time, fk_ticket_departure_date FROM ticket WHERE fk_ticket_order_id = %s", (order_id,))
        flight_key = cursor.fetchall()
        if not flight_key:
            return 0, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", 0

        plane_id = flight_key[0]['fk_ticket_plane_id']
        departure_time = flight_key[0]['fk_ticket_departure_time']
        departure_date = flight_key[0]['fk_ticket_departure_date']
        total_price = 0
        for ticket in flight_key:
            total_price += ticket['price']
        
        cursor.execute("SELECT fk_origin, fk_destination FROM flight WHERE fk_flight_plane_id = %s AND departure_time = %s AND departure_date = %s", (plane_id, departure_time, departure_date))
        flight = cursor.fetchall()
        if not flight:
             return total_price, "N/A", "N/A", str(departure_time), str(departure_date), "N/A", "N/A", 0
             
        origin = flight[0]['fk_origin']
        destination = flight[0]['fk_destination']
        arrival_date, arrival_time, duration = arrival(origin, destination, departure_date, departure_time)
        
    # Convert date/time objects to strings for session serialization
    return total_price, origin, destination, str(departure_time), str(departure_date), str(arrival_date), str(arrival_time), duration

def reports():
    reports = request.form.getlist('report')
    result1 = None
    result2 = None
    result3 = None
    result4 = None
    result5 = None
    query1 = """
SELECT ROUND(COALESCE(AVG(ticket_num), 0), 2) AS average_passengers_per_landed_flight
FROM (
    SELECT COUNT(t.`row`) AS ticket_num 
    FROM flight AS f 
    LEFT JOIN ticket AS t ON 
        f.fk_flight_plane_id = t.fk_ticket_plane_id AND 
        f.departure_time = t.fk_ticket_departure_time AND 
        f.departure_date = t.fk_ticket_departure_date 
    WHERE f.status = 'Landed' 
    GROUP BY f.fk_flight_plane_id, f.departure_time, f.departure_date
) AS Avgtable;
"""
    query2 = """
SELECT
    P.size AS Plane_size,
    P.manufacturer AS Plane_manufacturer,
    C.type AS Class,
    COALESCE(SUM(T.price), 0) AS Total_income
FROM
    plane P
    JOIN class C ON P.plane_id = C.fk_plane_id
    LEFT JOIN ticket T ON C.fk_plane_id = T.fk_ticket_plane_id AND C.type = T.fk_ticket_class
GROUP BY
    P.size,
    P.manufacturer,
    C.type
ORDER BY
    P.size, P.manufacturer;
"""
    query3 = """
SELECT
    AC.id,
    AC.first_name,
    AC.last_name,
    AC.`role`,
    ROUND(COALESCE(SUM(CASE WHEN R.duration <= 360 THEN R.duration ELSE 0 END)/60, 0), 2) AS Short_flights_hours,
    ROUND(COALESCE(SUM(CASE WHEN R.duration > 360 THEN R.duration ELSE 0 END)/60, 0), 2) AS Long_flights_hours
FROM
    air_crew AC
    LEFT JOIN air_crew_assignment ACA ON AC.id = ACA.fk_air_crew_id
    LEFT JOIN flight F ON ACA.fk_assignment_plane_id = F.fk_flight_plane_id
        AND ACA.fk_assignment_departure_time = F.departure_time
        AND ACA.fk_assignment_departure_date = F.departure_date
    LEFT JOIN route R ON F.fk_origin = R.origin AND F.fk_destination = R.destination
GROUP BY
    AC.id,
    AC.first_name,
    AC.last_name,
    AC.`role`;
"""
    query4 = """
SELECT
	YEAR(O.order_date) `Year`,
    MONTH(O.order_date) `Month`,
    ROUND(((SUM(CASE WHEN O.status = 'Cancelled by customer' THEN 1 ELSE 0 END)) / COUNT(*)) * 100, 2) AS AVG_Cancelation
FROM
	`order` AS O
GROUP BY
	YEAR(O.order_date),
    MONTH(O.order_date);
"""
    query5 = """
SELECT
	P.plane_id,
	YEAR(F.departure_date) `Year`,
    MONTH(F.departure_date) `Month`,
    SUM(CASE 
		WHEN F.`status` = 'Landed' THEN 1 ELSE 0 END) Landed_flights,
    SUM(CASE 
		WHEN F.`status` = 'Cancelled' THEN 1 ELSE 0 END) Cancelled_flights,
    ROUND((COUNT(DISTINCT(F.departure_date)) / 30.0) * 100, 2) AS Utilization,
    (SELECT 
		CONCAT(F2.fk_origin,'-',F2.fk_destination)
    FROM
		flight F2
	WHERE 
		F2.fk_flight_plane_id = P.plane_id AND
        YEAR(F2.departure_date) = YEAR(MAX(F.departure_date)) AND
        MONTH(F2.departure_date) = MONTH(MAX(F.departure_date))
    GROUP BY
		F2.fk_origin,
        F2.fk_destination
    HAVING 
		COUNT(*) >= ALL (SELECT
							COUNT(*)
						 FROM
							flight F3
						 WHERE 
							F3.fk_flight_plane_id = P.plane_id AND
							YEAR(F3.departure_date) = YEAR(MAX(F.departure_date)) AND
							MONTH(F3.departure_date) = MONTH(MAX(F.departure_date))
						 GROUP BY
							F3.fk_origin,
							F3.fk_destination)
	LIMIT 1) Dominant_route
FROM
	plane P LEFT JOIN flight F ON P.plane_id = F.fk_flight_plane_id
GROUP BY
	P.plane_id,
	YEAR(F.departure_date),
	MONTH(F.departure_date);
"""
    if '1' in reports:
        with db_cur() as cursor:
            cursor.execute(query1)
            result1 = cursor.fetchone()
    if '2' in reports:
        with db_cur() as cursor:
            cursor.execute(query2)
            result2 = cursor.fetchall()
    if '3' in reports:
        with db_cur() as cursor:
            cursor.execute(query3)
            result3 = cursor.fetchall()
    if '4' in reports:
        with db_cur() as cursor:
            cursor.execute(query4)
            result4 = cursor.fetchall()
    if '5' in reports:
        with db_cur() as cursor:
            cursor.execute(query5)
            result5 = cursor.fetchall()
    return result1, result2, result3, result4, result5


def update_db():
    with db_cur() as cursor:
        # Update 'Landed' flights
        cursor.execute("""
            UPDATE flight F
            SET F.status = 'Landed'
            WHERE F.status IN ('Active', 'Full') 
            AND DATE_ADD(TIMESTAMP(F.departure_date, F.departure_time), INTERVAL (
                SELECT duration FROM route R WHERE R.origin = F.fk_origin AND R.destination = F.fk_destination
            ) MINUTE) < NOW();
        """)
        
        # Update 'Full' flights
        cursor.execute("""
            UPDATE flight F
            SET F.status = 'Full'
            WHERE F.status = 'Active'
            AND (
                SELECT COUNT(*) 
                FROM ticket T 
                WHERE T.fk_ticket_plane_id = F.fk_flight_plane_id 
                AND T.fk_ticket_departure_date = F.departure_date 
                AND T.fk_ticket_departure_time = F.departure_time
            ) = (
                SELECT SUM(C.number_of_row * C.number_of_col) 
                FROM class C 
                WHERE C.fk_plane_id = F.fk_flight_plane_id
            );
        """)
        cursor.execute("""
            UPDATE `order` O
            SET O.status = 'Finished'
            WHERE O.status = 'Active' AND (SELECT TIMESTAMP(T.fk_ticket_departure_date, T.fk_ticket_departure_time) FROM ticket T WHERE T.fk_ticket_order_id = O.order_id LIMIT 1) < NOW();
        """)

def clear_session():
    # Keep login details and navigation history
    keep_keys = ['url_history']
    
    # Manager has 'id'
    if 'id' in session:
        keep_keys.append('id')
        
    # Signed customer has 'name' (guests do not have 'name' set)
    if 'name' in session:
        keep_keys.extend(['email', 'name'])
    
    keys = list(session.keys())
    for key in keys:
        if key not in keep_keys:
            session.pop(key, None)            