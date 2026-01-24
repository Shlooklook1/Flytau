USE flytau;
SELECT
    P.plane_id,
    YEAR(F.departure_date) `Year`,
    MONTH(F.departure_date) `Month`,
    SUM(CASE 
        WHEN F.`status` = 'Landed' THEN 1 ELSE 0 END) Landed_flights,
    SUM(CASE 
        WHEN F.`status` = 'Cancelled' THEN 1 ELSE 0 END) Cancelled_flights,
    ROUND((COUNT(DISTINCT CASE WHEN F.status = 'Landed' THEN F.departure_date END) / 30.0) * 100, 2) AS Utilization,
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