-- A table that stores the control variables of the Nowcasting model


CREATE TABLE IF NOT EXISTS control_variables( 	variable_id 			INTEGER NOT NULL AUTO_INCREMENT,
												variable_name			VARCHAR(20) NOT NULL,
                                                variable_description	TEXT,
												PRIMARY KEY(variable_id, variable_name),
                                                UNIQUE (variable_id, variable_name)
                                             ) ENGINE=INNODB;
									
INSERT INTO control_variables (variable_name, variable_description) VALUES
								("plag", "The lag of the idiosyncratic components"),
                                ("hor", "The forecast horizon"),
                                ("qlag", "The lag for the factor components"),
                                ("Nx", "Number of Factors"),
                                ("modelType", "The type of the model"),
                                ("high", "The high range of the estimate in standard deviations"),
                                ("low", "The low range of the estimate in standard deviations");
                                
                                
                                