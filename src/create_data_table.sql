-- Script to create the data table, timeseries' of economic data.
-- indicator_id | value  | period_date | frequency_id | release_date | next_release | latest | vintage

CREATE TABLE IF NOT EXISTS data ( 	indicator_id 	INTEGER, 
									value 			REAL NOT NULL,
									period_date 	DATE NOT NULL,
									frequency_id 	INTEGER NOT NULL,
									release_date 	DATE NOT NULL,
									next_release 	DATE,
									latest 			BOOLEAN NOT NULL DEFAULT True,
									vintage 		INTEGER NOT NULL DEFAULT 1,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
									changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
									CONSTRAINT data_ibfk_1 FOREIGN KEY (indicator_id)
										REFERENCES indicators(indicator_id) ON DELETE CASCADE,
									CONSTRAINT data_ibfk_2 FOREIGN KEY (frequency_id) 
										REFERENCES release_frequencies(frequency_id) ON DELETE CASCADE,
									UNIQUE data_ix (indicator_id, period_date, value)
                                    ) ENGINE=INNODB;
                                        
									
 -- INSERT INTO data(indicator_id, value, period_date, frequency_id, release_date, next_release, latest, vintage) 
	--		VALUES (4, 3001,'2016-03-01', 4, '2016-04-01', '2016-05-01', True, ) 
      --     ON duplicate key update indicator_id = indicator_id, period_date = period_date, release_date = release_date, latest = True, value = value, vintage = vintage;