-- insert into data (indicator_id,value, start_date, end_date, release_date, next_date, latest, vintage ) 
-- SELECT ind_table.indicator_id,1.12E+13, from indicators ind_table where ind_table.vendor_key = 'usnaac0169'


CREATE TABLE IF NOT EXISTS release_frequencies(	frequency_id 	INTEGER NOT NULL AUTO_INCREMENT, 
												frequency 	VARCHAR(2) NOT NULL , 
                                                frequency_text 	VARCHAR(15) NOT NULL, 
                                                frequency_info 	TEXT NOT NULL, 
                                                PRIMARY KEY (frequency_id),
                                                UNIQUE release_frequencies_ix(frequency)
                                                ) ENGINE=INNODB;

INSERT INTO release_frequencies (frequency, frequency_text, frequency_info) VALUES
								('M', 'Minute', 'Release frequency of 1 minute/ every minute'),
								('H', 'Hourly', 'Release frequency of 1 hour'),
                                ('d', 'Daily', 'Release frequency of 1 day'),
								('w', 'Weekly', 'Release frequency of 1 week'),
								('2w', 'Bi-Weekly', 'Release frequency of two weeks'),
                                ('3w', 'Tri-Weekly', 'Release frequency of three weeks'),
								('m', 'Monthly', 'Release frequency of 1 month '),
								('2m', 'Bi-Monthly', 'Release frequency of 2 months'),
                                ('6m', 'Half-Yearly', 'Release frequency every 6 months'),
                                ('q', 'Quaterly', 'Release frequency every quarter'),
								('y', 'Yearly', 'Release frequency every year') ON duplicate key update frequency_id = frequency_id, frequency = frequency;
