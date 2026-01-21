USE flytau;
SELECT
	YEAR(O.order_date) `Year`,
    MONTH(O.order_date) `Month`,
    ((SUM(CASE
		WHEN O.status = 'Cancelled by customer' THEN 1 ELSE 0 END)) / COUNT(*)) * 100 AS AVG_Cancelation
FROM
	`order` AS O
GROUP BY
	YEAR(O.order_date),
    MONTH(O.order_date)