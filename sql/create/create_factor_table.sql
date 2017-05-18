

CREATE TABLE IF NOT EXISTS factors (
	run_id 				INTEGER NOT NULL,
	period_date 		DATE NOT NULL,
	factor_id			INTEGER NOT NULL,
	forecast_type_id	INTEGER NOT NULL,
	factor_value		REAL NOT NULL,
    CONSTRAINT factors_ibfk_1 FOREIGN KEY (run_id)
		REFERENCES run_table(run_id) ON DELETE CASCADE,
	CONSTRAINT factors_ibfk_2 FOREIGN KEY (forecast_type_id)
		REFERENCES forecast_types(forecast_type_id) ON DELETE CASCADE,
	PRIMARY KEY (run_id, period_date, factor_id),
    UNIQUE (run_id, period_date, factor_id)
	) ENGINE=INNODB;
