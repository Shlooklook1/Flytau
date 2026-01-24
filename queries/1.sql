USE flytau;
SELECT
    ROUND(COALESCE(AVG(ticket_num), 0), 2) AS average_passengers_per_landed_flight
FROM(
    SELECT 
        COUNT(o.order_id) AS ticket_num
    FROM
        flight AS f 
        LEFT JOIN ticket AS t ON f.fk_flight_plane_id = t.fk_ticket_plane_id 
                              AND f.departure_time = t.fk_ticket_departure_time 
                              AND f.departure_date = t.fk_ticket_departure_date
        LEFT JOIN orders AS o ON t.fk_ticket_order_id = o.order_id AND o.status = 'Finished'
    WHERE
        f.status = 'Landed'
    GROUP BY
        f.fk_flight_plane_id, f.departure_time, f.departure_date
) AS Avgtable;