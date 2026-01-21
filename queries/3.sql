USE flytau;
SELECT
	AC.id,
    AC.first_name,
    AC.last_name,
    AC.`role`,
    SUM(CASE WHEN R.duration <= 6 THEN R.duration ELSE 0 END) AS Short_flight_hours,
    SUM(CASE WHEN R.duration > 6 THEN R.duration ELSE 0 END) AS Long_flight_hours
FROM
	air_crew AC LEFT JOIN air_crew_assignment ACA ON AC.id = ACA.fk_air_crew_id 
    LEFT JOIN flight F ON ACA.fk_assignment_plane_id = F.fk_flight_plane_id 
    AND ACA.fk_assignment_departure_time = F.departure_time AND ACA.fk_assignment_departure_date = F.departure_date
    LEFT JOIN route R ON F.fk_origin = R.origin AND F.fk_destination = R.destination
GROUP BY
	AC.id,
    AC.first_name,
    AC.last_name,
    AC.`role`
;	
    
    
    