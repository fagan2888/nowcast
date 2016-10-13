

CREATE TABLE IF NOT EXISTS factors ( 	run_id 			INTEGER NOT NULL,
										factor_value	REAL NOT NULL,
                                        factor_id		INTEGER NOT NULL,
                                        CONSTRAINT factors_ibfk_1 FOREIGN KEY (run_id)
											REFERENCES run_table(run_id) ON DELETE CASCADE,
										CONSTRAINT factors_ibfk_2 FOREIGN KEY (factor_id)
											REFERENCES factor_type(factor_id) ON DELETE CASCADE,
										PRIMARY KEY (run_id, factor_value, factor_id)
									) ENGINE=INNODB;
                                        
										
									