
CREATE TABLE IF NOT EXISTS forecast_data ( 	indicator_id 	INTEGER,
											period_date 	DATE NOT NULL,				
											low_forecast	REAL NOT NULL,
											mean_forecast 	REAL NOT NULL,
											hi_forecast		REAL NOT NULL,
											run_id 		INTEGER NOT NULL,
											created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
											changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
											CONSTRAINT forecast_data_ibfk_1 FOREIGN KEY (indicator_id)
												REFERENCES indicators(indicator_id) ON DELETE CASCADE,
											CONSTRAINT forecast_data_ibfk_2 FOREIGN KEY (run_id) 
												REFERENCES run_table(run_id) ON DELETE CASCADE,
										PRIMARY KEY (indicator_id, period_date, mean_forecast, run_id),
										UNIQUE forecast_data_ix (indicator_id, period_date, mean_forecast, run_id)
										) ENGINE=INNODB;
                                        