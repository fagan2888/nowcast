
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

select * from data order by period_date;
-- select * from data order by period_date;
-- select t1.indicator_id, t1.period_date, t1.release_date, t1.value, t1.vintage  from data t1 left join data t2 on t1.period_date = t2.period_date and t1.vintage < t2.vintage order by period_date;
-- select max(vintage) from data where indicator_id = 4 group by period_date
-- select indicator_id, period_date, max(vintage) from data where indicator_id = 4 group by period_date
-- select indicator_id, period_date, max(vintage) from data where indicator_id = 4 group by period_date;