
CREATE TABLE IF NOT EXISTS forecast_type( 	forecast_type_id INTEGER NOT NULL AUTO_INCREMENT,
											forecast_type VARCHAR(25),
                                            forecast_info TEXT,
                                            PRIMARY KEY(forecast_type_id),
                                            UNIQUE factor_ix(forecast_type_id, forecast_type)
										) ENGINE=INNODB;


INSERT INTO forecast_type (forecast_type, forecast_info) VALUES 
							("Backcast", "Describing in sample observations"),
                            ("Nowcast", "Describing some in sample data"),
                            ("Forecast", "Describing out of sample data") ON DUPLICATE KEY UPDATE forecast_type_id = forecast_type_id;