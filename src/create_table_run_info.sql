

CREATE TABLE IF NOT EXISTS run_info(run_id INTEGER NOT NULL,
									variable_id INTEGER NOT NULL,
                                    variable_value FLOAT NOT NULL,
									CONSTRAINT run_info_ibfk_1 FOREIGN KEY (run_id)
										REFERENCES run_table(run_id) ON DELETE CASCADE,
									CONSTRAINT run_info_ibfk_2 FOREIGN KEY (variable_id)
										REFERENCES control_variables(variable_id) ON DELETE CASCADE,
									PRIMARY KEY (run_id, variable_id),
                                    UNIQUE run_info_ix (run_id, variable_id)
                                    )ENGINE = INNODB;