--- run (4) after (1) create_meta_tables.sql and (2) create_data_tables.sql and (3) create_model_tables.sql

-- Run Table id
CREATE TABLE IF NOT EXISTS output_run_table (
 	run_id 		INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	timestamp 	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (run_id)
	) ENGINE=INNODB;


-- Run Info
CREATE TABLE IF NOT EXISTS output_run_info(
	run_id 			INTEGER NOT NULL,
	model_id 		INTEGER NOT NULL,
	run_type		INTEGER NOT NULL,
	information_set TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	svn_repository 	VARCHAR(80),
	svn_revision	INTEGER,
	PRIMARY KEY 	(run_id),
    UNIQUE KEY		output_run_info_ix (run_id),
	CONSTRAINT output_run_info_ibfk_1 FOREIGN KEY (run_id)
		REFERENCES output_run_table (run_id) ON DELETE CASCADE,
	CONSTRAINT output_run_info_ibfk_2 FOREIGN KEY (model_id)
		REFERENCES model_references (model_id) ON DELETE CASCADE,
	CONSTRAINT output_run_info_ibfk_3 FOREIGN KEY (run_type)
		REFERENCES meta_run_type (run_type_id) ON DELETE CASCADE
    ) ENGINE = INNODB;


-- Forecast data
CREATE TABLE IF NOT EXISTS output_forecast_data (
	indicator_id 		INTEGER,
	period_date 		DATE NOT NULL,
    forecast_type_id 	INTEGER NOT NULL,
	low_forecast		REAL NOT NULL,
	mean_forecast 		REAL NOT NULL,
	hi_forecast			REAL NOT NULL,
	run_id 				INTEGER NOT NULL,
	PRIMARY KEY 		(indicator_id, period_date, mean_forecast, run_id),
	UNIQUE KEY 			output_forecast_data_ix (indicator_id, period_date, mean_forecast, run_id),
	CONSTRAINT output_forecast_data_ibfk_1 FOREIGN KEY (indicator_id)
		REFERENCES data_indicators (indicator_id) ON DELETE CASCADE,
	CONSTRAINT output_forecast_data_ibfk_2 FOREIGN KEY (run_id)
		REFERENCES output_run_table (run_id) ON DELETE CASCADE,
	CONSTRAINT output_forecast_data_ibfk_3 FOREIGN KEY (forecast_type_id)
		REFERENCES meta_forecast_types (forecast_type_id) ON DELETE CASCADE
	) ENGINE=INNODB;


-- Factors
CREATE TABLE IF NOT EXISTS output_factors (
	run_id 				INTEGER NOT NULL,
	period_date 		DATE NOT NULL,
	factor_id			INTEGER NOT NULL,
	forecast_type_id	INTEGER NOT NULL,
	factor_value		REAL NOT NULL,
	PRIMARY KEY 		(run_id, period_date, factor_id),
    UNIQUE KEY 			output_factors_ix (run_id, period_date, factor_id),
    CONSTRAINT factors_ibfk_1 FOREIGN KEY (run_id)
		REFERENCES output_run_table (run_id) ON DELETE CASCADE,
	CONSTRAINT factors_ibfk_2 FOREIGN KEY (forecast_type_id)
		REFERENCES meta_forecast_types (forecast_type_id) ON DELETE CASCADE
	) ENGINE=INNODB;
