
-- select t1.indicator_id, t1.value,  t1.period_date, t1.frequency_id, t1.release_date, t1.next_release, t1.vintage from data t1 left join data t2 on t1.period_date = t2.period_date and t1.vintage < t2.vintage order by period_date;
-- select t1.vintage from data t1 left join data t2 on t1.period_date = t2.period_date and t1.vintage < t2.vintage

-- update data set latest = True where indicator_id = %s, period_date = %s, release_date = %s, vintage = %s
-- select * from data where release_date = '2016-09-01';
-- select * from data order by period_date desc;
-- select * from data where release_date > str_to_date('2016-09-01', '%Y-%m-%d')
-- select * from economic_database.data;

-- update data set vintage = vintage + 1 where period_date = '2015-01-01' and release_date > '2016-09-01';

-- select min(vintage) from a;
-- select 4, 6, (select min(vintage) from data where period_date = date'2015-01-10' and release_date > '2016-09-01');
-- select * from data;
-- elect  4, 3001,'2016-03-01', 4, '2016-04-01', '2016-05-01', True, (select (select(min(vintage) from data where period_date = '2015-01-10' and release_date > '2016-09-01')(select 1 from data ));

 /*INSERT INTO data(indicator_id, value, period_date, frequency_id, release_date, next_release, latest, vintage) 
			select  4, 3001,'2016-03-01', 4, '2016-04-01', '2016-05-01', True,(select min(vintage) from data where period_date = '2015-01-10' and release_date > '2016-09-01')
           ON duplicate key update indicator_id = indicator_id, period_date = period_date, release_date = release_date, latest = True, value = value, vintage = vintage;
*/
-- select period_date,release_date from data where release_date = '2016-09-01';

-- select max(t1.vintage) from data t1 left join data t2 on  t1.period_date = t2.period_date;

-- create database ms_econ_Db_UAT;
-- select t1.indicator_id, t1.period_date, t1.release_date, t1.vintage  from data t1 left join data t2 on t1.period_date = t2.period_date and t1.release_date = t2.release_date and t2.vintage < t1.vintage
use ms_econ_Db_DEV;
/*select * from data_series_v where frequency = 'q';
select * from indicator_types order by indicator_type_id;
select * from presentation_units order by unit_id;

SELECT t4.iso_alpha_2, t2.vendor_key, t2.indicator_info, t1.value, t1.period_date, t1.release_date, t1.next_release, t1.latest, t1.vintage, t3.frequency, t5.indicator_origin, t6.presentation_unit FROM data t1 LEFT JOIN (indicators t2) ON  (t1.indicator_id = t2.indicator_id) LEFT JOIN (release_frequencies t3) ON(t2.frequency_id = t3.frequency_id) LEFT JOIN (indicator_types t5) ON (t2.indicator_type = t5.indicator_type_id) LEFT JOIN (presentation_units t6) ON (t2.indicator_presentation = t6.unit_id) LEFT JOIN (master_country t4) USING(country_id);


*/
select * from forecast_data;
SELECT t1.period_date, t1.mean_forecast, t2.vendor_key, t3.forecast_type, t1.run_id, t5.timestamp from forecast_data t1 LEFT JOIN (indicators t2) ON (t2.indicator_id = t1.indicator_id) LEFT JOIN (forecast_types t3) ON (t3.forecast_type_id = t1.forecast_type_id) LEFT JOIN (run_table t4) ON (t4.run_id > t1.run_id) LEFT JOIN (run_table t5) ON (t5.run_id = t1.run_id) where t4.timestamp is NULL;
select t1.run_id, t2.variable_name, t1.variable_value from run_info t1 LEFT JOIN (control_variables t2) ON (t2.variable_id = t1.variable_id);

SELECT 
MAX(CASE WHEN t3.fieldname = 'variable_name' THEN t3.fieldvalue ELSE NULL END) AS variable_name,
MAX(CASE WHEN t3.fieldname = 'variable_value' THEN t3.fieldvalue ELSE NULL END) AS variable_value,
FROM (select t1.run_id, t2.variable_name, t1.variable_value from run_info t1 LEFT JOIN (control_variables t2) ON (t2.variable_id = t1.variable_id)) AS t3
GROUP BY t3.run_id;


-- select * from data order by period_date;
-- select t1.indicator_id, t1.period_date, t1.release_date, t1.value, t1.vintage  from data t1 left join data t2 on t1.period_date = t2.period_date and t1.vintage < t2.vintage order by period_date;
-- select max(vintage) from data where indicator_id = 4 group by period_date
-- select indicator_id, period_date, max(vintage) from data where indicator_id = 4 group by period_date
-- select indicator_id, period_date, max(vintage) from data where indicator_id = 4 group by period_date;