SELECT 
    indicator_id, period_date, mean_forecast, run_id
FROM
    forecast_data AS fc
    WHERE fc.indicator_id = 20
;



SELECT run_table.timestamp, fc.period_date, fc.mean_forecast
FROM forecast_data AS fc
LEFT JOIN run_table
ON run_table.run_id = fc.run_id
WHERE fc.indicator_id = 20
ORDER BY fc.period_date, run_table.timestamp;
