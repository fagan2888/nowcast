-- Script to create the data table, timeseries' of economic data.
-- indicator_id | value  | period_date | frequency_id | release_date | next_release | latest | vintage

CREATE TABLE IF NOT EXISTS data ( 	indicator_id 	INTEGER, 
									value 			REAL NOT NULL,
									period_date 	DATE NOT NULL,
									frequency_id 	INTEGER NOT NULL,
									release_date 	DATETIME NOT NULL,
									next_release 	DATETIME,
									latest 			BOOLEAN NOT NULL DEFAULT True,
									vintage 		INTEGER NOT NULL DEFAULT 1,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
									changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
									CONSTRAINT data_ibfk_1 FOREIGN KEY (indicator_id)
										REFERENCES indicators(indicator_id) ON DELETE CASCADE,
									CONSTRAINT data_ibfk_2 FOREIGN KEY (frequency_id) 
										REFERENCES release_frequencies(frequency_id) ON DELETE CASCADE,
									UNIQUE data_ix (indicator_id, period_date, value),
                                    PRIMARY KEY (indicator_id, period_date, value, release_date)
                                    ) ENGINE=INNODB;
                                        
									
