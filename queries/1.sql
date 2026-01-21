USE flytau;
SELECT
	AVG(ticket_num) AS average_passengers_per_landed_flight
FROM(
	SELECT 
		COUNT(t.`row`) AS ticket_num
	FROM
		flight AS f LEFT JOIN ticket AS t ON f.fk_flight_plane_id = t.fk_ticket_plane_id AND
		f.departure_time = t.fk_ticket_departure_time AND
		f.departure_date = t.fk_ticket_departure_date
	WHERE
		status = 'Landed'
	GROUP BY
		f.fk_flight_plane_id, f.departure_time, f.departure_date
) AS Avgtable