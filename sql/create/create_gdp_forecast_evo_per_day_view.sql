#This creates a view of the last forecast that the model produces on a day. e.g if we have two releases on a day and thus two model runs on a day we only take the last one
CREATE VIEW gdp_fcst_evo_over_time_v AS SELECT t1.period_date, t1.mean_forecast, t2.vendor_key, t2.indicator_short_info, t3.forecast_type, t1.run_id, t6.presentation_unit, t5.timestamp, t5.run_date from forecast_data t1 LEFT JOIN (SELECT max(run_id) as run_id,max(timestamp) as timestamp, date_format(timestamp, '%Y-%m-%d') as run_date from run_table group by run_date) t5 ON (t5.run_id = t1.run_id) LEFT JOIN (indicators t2) ON (t2.indicator_id = t1.indicator_id) LEFT JOIN (forecast_types t3) ON (t3.forecast_type_id = t1.forecast_type_id) LEFT JOIN (presentation_units t6) ON (t2.indicator_presentation = t6.unit_id) where vendor_key = 'usnaac0169' and t5.timestamp is not NULL order by t5.run_date desc;