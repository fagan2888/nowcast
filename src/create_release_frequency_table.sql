-- insert into data (indicator_id,value, start_date, end_date, release_date, next_date, latest, vintage ) 
-- SELECT ind_table.indicator_id,1.12E+13, from indicators ind_table where ind_table.vendor_key = 'usnaac0169'


CREATE TABLE IF NOT EXISTS release_frequencies(	frequency_id 	INTEGER NOT NULL AUTO_INCREMENT, 
												frequency 		INTEGER NOT NULL, 
                                                frequency_text 	VARCHAR(15) NOT NULL, 
                                                frequency_type 	VARCHAR(10) NOT NULL, 
                                                PRIMARY KEY (frequency_id),
                                                UNIQUE frequency_ix (frequency, frequency_type)
                                                ) ENGINE=INNODB;

INSERT INTO release_frequencies (frequency, frequency_text, frequency_type) VALUES 
								('1', 'daily', 'day'),
								('7', 'bweekly', 'day'),
								('14', 'bi-weekly', 'day'),
								('30', 'monthly', 'day'),
								('60', 'bi-monthly', 'day'),
								('91', 'quarterly', 'day'),
								('182', 'bi-annually', 'day'),
								('365', 'yearly', 'day') ;
