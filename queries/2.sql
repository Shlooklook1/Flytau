USE flytau;
SELECT
	P.size Plane_size,
    P.manufacturer Plane_manufacturer,
    T.fk_ticket_class Class,
    SUM(T.price) Total_income
FROM
	ticket T JOIN Plane P ON T.fk_ticket_plane_id=P.plane_id
GROUP BY
	P.size,
    P.manufacturer,
    T.fk_ticket_class;
