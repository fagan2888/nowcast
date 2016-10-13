
CREATE TABLE IF NOT EXISTS factor_type( 	factor_id INTEGER NOT NULL AUTO_INCREMENT,
											factor_type VARCHAR(25),
                                            factor_info TEXT,
                                            PRIMARY KEY(factor_id)
										) ENGINE=INNODB;


INSERT INTO factor_type (factor_type, factor_info) VALUES 
							("Estimated", "Factors describing in sample observations"),
                            ("Nowcast", "Factors describing some in sample data some Nowcast"),
                            ("Forecast", "Factors describing out of sample data");