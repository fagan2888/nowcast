-- Script to create the tables associated with the data
--- run (2) after create_meta_tables.sql

-- Data Sources
CREATE TABLE IF NOT EXISTS data_sources (
    source_id           INTEGER NOT NULL,
    source_name         VARCHAR(60) NOT NULL,
    source_description  TEXT,
    PRIMARY KEY         (source_id),
    UNIQUE KEY          data_sources_ix (source_name)
    ) ENGINE = INNODB;



-- Data Variables
-- DROP TABLE IF EXISTS data_variable_id CASCADE;
CREATE TABLE IF NOT EXISTS data_variable_id (
	variable_id             INTEGER NOT NULL,
	variable_name           VARCHAR(60) NOT NULL,
    variable_description    TEXT,
    source_id               INTEGER, -- OBS Link
    dataset                 VARCHAR(50),
    frequency_id 		    INTEGER NOT NULL,
    country_id 			    INTEGER NOT NULL,
    indicator_type          INTEGER NOT NULL,
    publication_lags        INTEGER, -- DAYS
	PRIMARY KEY             (variable_id),
    UNIQUE KEY              data_variable_id_ix (variable_name),
    CONSTRAINT data_variable_id_ibfk_1 FOREIGN KEY (frequency_id)
		REFERENCES meta_release_frequencies (frequency_id),
    CONSTRAINT data_variable_id_ibfk_2 FOREIGN KEY (country_id)
		REFERENCES meta_master_country (country_id) ON DELETE CASCADE,
    CONSTRAINT data_variable_id_ibfk_3 FOREIGN KEY (indicator_type)
		REFERENCES meta_indicator_types (indicator_type_id),
    CONSTRAINT data_variable_id_ibfk_4 FOREIGN KEY(source_id)
		REFERENCES data_sources (source_id)
    ) ENGINE = INNODB;


-- Data Providers
CREATE TABLE IF NOT EXISTS data_provider (
	provider_id        INTEGER NOT NULL AUTO_INCREMENT,
	provider_name      VARCHAR(25) NOT NULL,
	provider_long_name TEXT,
	PRIMARY KEY        (provider_id),
	UNIQUE KEY         data_provider_ix (provider_name)
    ) ENGINE=INNODB;


-- Data Indicators
-- DROP TABLE IF EXISTS data_indicators;
CREATE TABLE IF NOT EXISTS data_indicators (
    indicator_id 			INTEGER NOT NULL AUTO_INCREMENT,
	provider_id 			INTEGER NOT NULL,
	vendor_key 				VARCHAR (25) NOT NULL,
    variable_id				INTEGER NOT NULL,
	PRIMARY KEY             (indicator_id),
    UNIQUE KEY              data_indicators_ix (provider_id, vendor_key),
	CONSTRAINT data_indicators_ibfk_1 FOREIGN KEY (provider_id)
		REFERENCES data_provider (provider_id) ON DELETE CASCADE,
	CONSTRAINT data_indicators_ibfk_2 FOREIGN KEY (variable_id)
		REFERENCES data_variable_id (variable_id) ON DELETE CASCADE
    ) ENGINE=INNODB;


-- Data Values
-- DROP TABLE IF EXISTS data_values CASCADE;
CREATE TABLE IF NOT EXISTS data_values (
	indicator_id 	INTEGER,
	value 			REAL NOT NULL,
	period_date 	DATE NOT NULL,
	release_date 	DATETIME NOT NULL,
	next_release 	DATETIME,
	latest 			BOOLEAN NOT NULL DEFAULT True,
	vintage 		INTEGER NOT NULL DEFAULT 1,
	created_at		TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	changed_at		TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY    (indicator_id, period_date, value, release_date),
	UNIQUE KEY     data_values_ix (indicator_id, period_date, value),
    CONSTRAINT data_values_ibfk_1 FOREIGN KEY (indicator_id)
		REFERENCES data_indicators (indicator_id) ON DELETE CASCADE
    )
ENGINE = INNODB;
