

CREATE TABLE IF NOT EXISTS run_table ( 	run_id INTEGER NOT NULL AUTO_INCREMENT,
										timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        PRIMARY KEY (run_id)
									) ENGINE=INNODB;