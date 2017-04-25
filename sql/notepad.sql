SHOW tables;

/*INSERT INTO instrument_type(instrument_type_id, instrument_class_id, instrument_type) SELECT (SELECT MAX(it.instrument_type_id) + 1 from instrument_type it), ic.instrument_class_id,'Government Bond' FROM instrument_class ic WHERE ic.instrument_class = 'Bond' ON DUPLICATE KEY UPDATE instrument_type_id = instrument_type_id, instrument_class_id = ic.instrument_class_id, instrument_type = instrument_type;
*/
SELECT max(run_id),max(timestamp) as timestamp, date_format(timestamp, '%Y-%m-%d') as date from run_table as rt group by date order by date desc;
SELECT t1.period_date, t1.mean_forecast as forecast, t1.run_id, t5.timestamp as timestamp from forecast_data t1 LEFT JOIN (indicators t2) ON (t2.indicator_id = t1.indicator_id) LEFT JOIN (run_table t5) ON (t5.run_id = t1.run_id) where t2.vendor_key = 'usnaac0169' order by t5.timestamp DESC;
SELECT t1.period_date, t1.mean_forecast as forecast,, t1.run_id, t5.run_date from forecast_data t1 LEFT JOIN (SELECT max(run_id) as run_id,max(timestamp) as timestamp, date_format(timestamp, '%Y-%m-%d') as run_date from run_table group by run_date) t5 ON (t5.run_id = t1.run_id) LEFT JOIN (indicators t2) ON (t2.indicator_id = t1.indicator_id) LEFT JOIN (forecast_types t3) ON (t3.forecast_type_id = t1.forecast_type_id) LEFT JOIN (presentation_units t6) ON (t2.indicator_presentation = t6.unit_id) where vendor_key = 'usnaac0169' and t5.timestamp is not NULL order by t5.run_date desc;



select * from gdp_fcs_time;

/*select * from forecast_data where period_date > '2016-09-01' and indicator_id = 5 and run_id > 38;

select * from data_series_v where vendor_key = 'ussurv0354' order by period_date desc; 

select * from master_country where iso_currency_alpha_3 = 'USD';

select * from strategies;
SELECT * from instrument_type;

select * from instrument_class;
SELECT max(it.instrument_type_id) + 1, ic.instrument_class_id,'Government Bond' FROM instrument_class ic, instrument_type it WHERE ic.instrument_class = 'Bond';

select * from data_series_v where vendor_key = 'ussurv0354' order by period_date desc;*/
/*drop table instrument_type;
drop table instruments;
delete from instruments where instrument_id > 1;
alter table instruments AUTO_INCREMENT = 1;*/
