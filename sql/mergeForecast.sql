
SELECT 
	d1.period_date, d1.indicator_id, d1.mean_forecast, d1.run_id, d1.indicator_short_info, d1.forecast_type, d1.timestamp
FROM 
	(
	SELECT 
		tb4.period_date, tb4.indicator_id, tb4.mean_forecast, tb4.run_id, tb4.indicator_short_info, tb4.forecast_type, tb5.timestamp
	FROM
	(
		SELECT
			tb1.period_date, tb1.indicator_id, tb1.mean_forecast, tb1.run_id, tb2.indicator_short_info, tb3.forecast_type
		FROM 
			forecast_data as tb1
		LEFT JOIN
			indicators as tb2
		ON tb1.indicator_id = tb2.indicator_id
		LEFT JOIN
			forecast_types AS tb3
		ON tb1.forecast_type_id = tb3.forecast_type_id
	) AS tb4
	LEFT JOIN
		run_table AS tb5
	ON
		tb4.run_id = tb5.run_id
	WHERE 
		indicator_id = 20
	AND
		month(tb4.period_date) % 3 = 0
	) AS d1
LEFT JOIN
	(SELECT date(timestamp) AS datestamp, max(run_id) AS run_id FROM run_table GROUP BY date(timestamp)) AS d2
ON
	date(d1.timestamp) = d2.datestamp
WHERE
	d1.run_id = d2.run_id
    ;
    
SELECT date(timestamp), max(run_id) FROM run_table GROUP BY date(timestamp);
