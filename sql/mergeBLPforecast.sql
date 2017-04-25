SELECT
	blp_fcst.forecast_period, blp_fcst.release_date, fcst.avg_fcst AS own, blp_fcst.avg_fcst AS blp
FROM
	(
	SELECT
		tb2.forecast_period, tb1.release_date, tb1.value AS avg_fcst
	FROM
		blp_fcst_data as tb1
	LEFT JOIN
		blp_fcst_meta as tb2
	ON tb1.ticker = tb2.ticker
	WHERE tb2.provider IS NULL
	AND tb2.active = 1
    AND tb2.variable = "GDP"
	) as blp_fcst
LEFT JOIN
	(
	SELECT tb2.forecast_period, tb1.release_date, avg(tb1.value) AS avg_fcst
	FROM
		blp_fcst_data as tb1
	LEFT JOIN
		blp_fcst_meta as tb2
	ON tb1.ticker = tb2.ticker
	WHERE tb2.provider IS NOT NULL
	AND tb2.active = 1
    AND tb2.variable = "GDP"
	GROUP BY tb2.forecast_period, tb1.release_date
	) AS fcst
ON
	blp_fcst.forecast_period = fcst.forecast_period
AND
	blp_fcst.release_date = fcst.release_date
WHERE blp_fcst.forecast_period = date("2017-03-31")
AND date(blp_fcst.release_date) > date("2017-04-10")
ORDER BY blp_fcst.forecast_period, blp_fcst.release_date
; 

