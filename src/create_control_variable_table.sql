-- A table that stores the control variables of the Nowcasting model


CREATE TABLE IF NOT EXISTS control_variables( 	variable_id 			INTEGER NOT NULL AUTO_INCREMENT,
												variable_name			VARCHAR(20) NOT NULL,
                                                variable_description	TEXT,
												PRIMARY KEY(variable_id, variable_name)
                                             )ENGINE=INNODB;
									
INSERT INTO control_variables (variable_name, variable_description) VALUES
								("p_lag", "The lag of the idiosyncratic components"),
                                ("time_horizon", "The forecast horizon"),
                                ("q_lag", "The lag for the factor components"),
                                ("Nx", "Number of Factors"),
                                ("model_type", "The type of the model"),
                                ("high_scenario", "The high range of the estimate in standard deviations"),
                                ("low_scenario", "The low range of the estimate in standard deviations");
                                
                                
                                