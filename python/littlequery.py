"""
This script is responsible for resetting the database to its initial state.
It connects to the database using the utils module, clears all existing data from tables,
and repopulates them with a predefined set of mock data including managers, crew, customers, flights, and orders.
"""
import utils

with utils.db_cur() as cursor:
    cursor.execute("""


/* 1. DISABLE CHECKS & RESET TABLES */
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_SAFE_UPDATES = 0;

DELETE FROM ticket;
DELETE FROM `order`;
DELETE FROM air_crew_assignment;
DELETE FROM flight_price;
DELETE FROM flight;
DELETE FROM class;
DELETE FROM plane;
DELETE FROM route;
DELETE FROM signed_customer;
DELETE FROM phone_number;
DELETE FROM customer;
DELETE FROM air_crew;
DELETE FROM manager;

SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 1;


/* 2. BASE TABLES */

/* MANAGERS */
INSERT INTO manager (id, first_name, last_name, phone_number, hire_date, city, street, house_number, password) VALUES
('039485721', 'ערן', 'בוס', '050-0000001', '2020-01-01', 'Tel Aviv', 'Herzl', '1', 'admin123'),
('204593817', 'נטע', 'בוסית', '050-0000002', '2021-05-15', 'Haifa', 'Ben Gurion', '10', 'neta123');

/* AIR CREW */
INSERT INTO air_crew (id, first_name, last_name, role, long_flight_certificate, hire_date) VALUES
-- Pilots
('300584921', 'דני', 'טייס', 'Pilot', 1, '2019-01-01'),
('300123456', 'רון', 'שחקים', 'Pilot', 1, '2019-01-01'),
('300987654', 'גל', 'מעופף', 'Pilot', 1, '2019-01-01'),
('300654321', 'טל', 'אביב', 'Pilot', 1, '2019-01-01'),
('300741852', 'שי', 'רום', 'Pilot', 1, '2019-01-01'),
('300369258', 'מירי', 'כהן', 'Pilot', 1, '2019-01-01'),
('300147258', 'אלי', 'לוי', 'Pilot', 1, '2019-01-01'),
('300258369', 'נועה', 'קופטר', 'Pilot', 1, '2019-01-01'),
('300951753', 'אבי', 'רון', 'Pilot', 1, '2019-01-01'),
('300753951', 'יוני', 'רון', 'Pilot', 1, '2019-01-01'),
-- Flight Attendants
('200123789', 'דליה', 'דייל', 'Flight attendant', 1, '2020-01-01'),
('310456123', 'דנה', 'שירות', 'Flight attendant', 1, '2020-01-01'),
('200789456', 'רינה', 'עזר', 'Flight attendant', 1, '2020-01-01'),
('310654987', 'יוסי', 'מגש', 'Flight attendant', 1, '2020-01-01'),
('200321654', 'מיכל', 'מושב', 'Flight attendant', 1, '2020-01-01'),
('310987321', 'קרן', 'מים', 'Flight attendant', 1, '2020-01-01'),
('200159753', 'עומר', 'אוכל', 'Flight attendant', 1, '2020-01-01'),
('310357159', 'ניר', 'בטוח', 'Flight attendant', 1, '2020-01-01'),
('200456852', 'ליאת', 'יציאה', 'Flight attendant', 1, '2020-01-01'),
('310852456', 'תומר', 'ווסט', 'Flight attendant', 1, '2020-01-01'),
('200963741', 'שיר', 'חגורה', 'Flight attendant', 1, '2020-01-01'),
('310741963', 'מור', 'תיק', 'Flight attendant', 1, '2020-01-01'),
('200852963', 'חן', 'קפה', 'Flight attendant', 1, '2020-01-01'),
('310159357', 'אור', 'תה', 'Flight attendant', 1, '2020-01-01'),
('200357951', 'בן', 'תורן', 'Flight attendant', 1, '2020-01-01'),
('310258147', 'דור', 'חופשי', 'Flight attendant', 1, '2020-01-01'),
('200147369', 'גל', 'עגלה', 'Flight attendant', 1, '2020-01-01'),
('310369147', 'טל', 'חיוך', 'Flight attendant', 1, '2020-01-01'),
('200753159', 'ים', 'ענן', 'Flight attendant', 1, '2020-01-01'),
('310951357', 'רון', 'אוויר', 'Flight attendant', 1, '2020-01-01');

/* CUSTOMERS */
INSERT INTO customer (email, first_name, last_name) VALUES
('guest1@gmail.com', 'John', 'Guest'),
('guest2@gmail.com', 'Jane', 'Visitor'),
('reg1@gmail.com', 'Israel', 'Israeli'),
('reg2@gmail.com', 'Rivka', 'Cohen'),
('reg3@gmail.com', 'David', 'Levi'),
('reg4@gmail.com', 'Sarah', 'Klein');

INSERT INTO signed_customer (fk_signed_email, passport, birth_date, sign_up_date, password) VALUES
('reg1@gmail.com', 'P12345678', '1990-01-01', CURDATE(), 'pass1'),
('reg2@gmail.com', 'P87654321', '1992-05-05', CURDATE(), 'pass2'),
('reg3@gmail.com', 'P11223344', '1985-11-20', CURDATE(), 'pass3'),
('reg4@gmail.com', 'P99887766', '1999-03-30', CURDATE(), 'pass4');

/* ROUTES */
INSERT INTO route (origin, destination, duration) VALUES
('Israel', 'Italy', 240), -- Short (4h)
('Italy', 'Israel', 240), -- Short
('Israel', 'USA', 720),    -- Long (12h)
('USA', 'Israel', 660),    -- Long (11h)
('Israel', 'Japan', 750),  -- Long
('Japan', 'Israel', 780),  -- Long
('Israel', 'Montenegro', 200), -- Short
('Montenegro', 'Israel', 180), -- Short
('Israel', 'Philipines', 600), -- Long (10h)
('Philipines', 'Israel', 620); -- Long

/* PLANES */
INSERT INTO plane (plane_id, purchase_date, size, manufacturer) VALUES
('PLN-L1', '2020-01-01', 'Large', 'Boeing'),
('PLN-L2', '2021-06-15', 'Large', 'Airbus'),
('PLN-L3', '2019-11-20', 'Large', 'Boeing'),
('PLN-S1', '2022-03-10', 'Small', 'Dassault'),
('PLN-S2', '2023-08-05', 'Small', 'Airbus'),
('PLN-S3', '2024-02-28', 'Small', 'Boeing');


/* 3. DEPENDENT TABLES */

/* CLASSES */
INSERT INTO class (fk_plane_id, type, number_of_col, number_of_row) VALUES
('PLN-L1', 'Economy', 6, 30), ('PLN-L1', 'Business', 4, 10),
('PLN-L2', 'Economy', 6, 30), ('PLN-L2', 'Business', 4, 10),
('PLN-L3', 'Economy', 6, 30), ('PLN-L3', 'Business', 4, 10),
('PLN-S1', 'Economy', 4, 20),
('PLN-S2', 'Economy', 4, 20),
('PLN-S3', 'Economy', 4, 20);


/* RE-ENABLE CHECKS */
SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 1;
""")
    print(cursor.fetchall())