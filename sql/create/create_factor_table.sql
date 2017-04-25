

CREATE TABLE IF NOT EXISTS factors ( 	run_id 			INTEGER NOT NULL,
										factor_value	REAL NOT NULL,
                                        forecast_type_id		INTEGER NOT NULL,
                                        CONSTRAINT factors_ibfk_1 FOREIGN KEY (run_id)
											REFERENCES run_table(run_id) ON DELETE CASCADE,
										CONSTRAINT factors_ibfk_2 FOREIGN KEY (forecast_type_id)
											REFERENCES forecast_types(forecast_type_id) ON DELETE CASCADE,
										PRIMARY KEY (run_id, factor_value, forecast_type_id),
                                        UNIQUE (run_id, factor_value, forecast_type_id)
									) ENGINE=INNODB;
                                        
										
									