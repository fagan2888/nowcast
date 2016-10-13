-- Create a table with run information

CREATE TABLE IF NOT EXISTS run_info ( run_number INTEGER NOT NULL,
										variable_id INTEGER NOT NULL,
                                        variable_value FLOAT NOT NULL,
                                        CONSTRAINT data_ibfk_1 FOREIGN KEY (variable_id)
											REFERENCES control_variables(variable_id) ON DELETE CASCADE,
                                        PRIMARY KEY (run_number, variable_id)
                                        );
                                        
                                        