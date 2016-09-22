-- Script to create the data table, timeseries' of economic data.
-- indicator_id | value  | start_date | end_date | frequency_id | release_date | next_release | latest | vintage

CREATE TABLE IF NOT EXISTS data ( 	indicator_id 	INTEGER, 
									value 			REAL NOT NULL,
									start_date 		DATE NOT NULL,
									end_date 		DATE NOT NULL,
									frequency_id 	INTEGER NOT NULL,
									release_date 	DATE NOT NULL,
									next_release 	DATE,
									latest 			BOOLEAN NOT NULL,
									vintage 		INTEGER NOT NULL,
									CONSTRAINT data_ibfk_1 FOREIGN KEY (indicator_id)
										REFERENCES indicators(indicator_id) ON DELETE CASCADE,
									CONSTRAINT data_ibfk_2 FOREIGN KEY (frequency_id) 
										REFERENCES release_frequencies(frequency_id) ON DELETE RESTRICT,
									UNIQUE data_ix (indicator_id, start_date, vintage)
                                    ) ENGINE=INNODB;
                                        
                                        

