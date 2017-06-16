-- Forecast tables
-- run (5) after 1,2,3,4

DROP TABLE IF EXISTS fcst_data;
DROP TABLE IF EXISTS fcst_tickers;
DROP TABLE IF EXISTS fcst_sources;
DROP TABLE IF EXISTS fcst_variables;

-- Target variables
CREATE TABLE IF NOT EXISTS fcst_variables (
	fcst_variable_id   INTEGER NOT NULL,
	fcst_variable_tick VARCHAR(6) NOT NULL,
	target_variable_id INTEGER NOT NULL UNIQUE,
	PRIMARY KEY        (fcst_variable_id),
	UNIQUE KEY         fcst_blp_variables_ix (fcst_variable_id),
    CONSTRAINT fcst_blp_variable_ibfk_1 FOREIGN KEY(target_variable_id)
		REFERENCES data_variable_id (variable_id)
    ) ENGINE=INNODB;
INSERT INTO meta_table_updated (dataset, last_updated) VALUES ('fcst_variables', STR_TO_DATE('1900-01-01', '%Y-%m-%d'));

-- Forecast Providers
CREATE TABLE IF NOT EXISTS fcst_sources (
    fcst_source_id   INTEGER NOT NULL,
    fcst_source_name VARCHAR(40) NOT NULL,
    fcst_source_code VARCHAR(3),
    PRIMARY KEY (fcst_source_code),
    UNIQUE KEY fcst_sources_ix (fcst_source_id)
    ) ENGINE=INNODB;
INSERT INTO meta_table_updated (dataset, last_updated) VALUES ('fcst_sources', STR_TO_DATE('1900-01-01', '%Y-%m-%d'));

-- active tickers: generate automatically
CREATE TABLE IF NOT EXISTS fcst_tickers (
	ticker_id        INTEGER NOT NULL AUTO_INCREMENT,
    ticker_code      VARCHAR(21) NOT NULL,
    active           BOOLEAN NOT NULL DEFAULT TRUE,
    target_period    DATE NOT NULL,
    fcst_variable_id INTEGER NOT NULL,
    fcst_source_id   INTEGER NOT NULL,
    provider_id      INTEGER NOT NULL,
    target_frequency INTEGER NOT NULL,
    PRIMARY KEY (ticker_code),
    UNIQUE KEY fcst_tickers_ix (ticker_id),
    CONSTRAINT fcst_ticker_ibfk_1 FOREIGN KEY (fcst_variable_id)
        REFERENCES fcst_variables (fcst_variable_id),
    CONSTRAINT fcst_ticker_ibfk_2 FOREIGN KEY (fcst_source_id)
        REFERENCES fcst_sources (fcst_source_id),
    CONSTRAINT fcst_ticker_ibfk_3 FOREIGN KEY (provider_id)
        REFERENCES data_sources (source_id),
    CONSTRAINT fcst_ticker_ibfk_4 FOREIGN KEY (target_frequency)
        REFERENCES meta_release_frequencies (frequency_id)
    ) ENGINE=INNODB;
INSERT INTO meta_table_updated (dataset, last_updated) VALUES ('fcst_tickers', STR_TO_DATE('1900-01-01', '%Y-%m-%d'));

-- data - to be populated
CREATE TABLE IF NOT EXISTS fcst_data (
    ticker_id       INTEGER NOT NULL,
    release_date    DATE NOT NULL,
	latest 			BOOLEAN NOT NULL DEFAULT True,
	vintage 		INTEGER NOT NULL DEFAULT 1,
	created_at		TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	changed_at		TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    value           REAL NOT NULL,
	PRIMARY KEY     (ticker_id, release_date, vintage),
	UNIQUE KEY      fcst_data_ix (ticker_id, release_date, vintage),
    CONSTRAINT fcst_data_ibfk_1 FOREIGN KEY (ticker_id)
        REFERENCES fcst_tickers (ticker_id)
    ) ENGINE=INNODB;
INSERT INTO meta_table_updated (dataset, last_updated) VALUES ('fcst_data', STR_TO_DATE('1900-01-01', '%Y-%m-%d'));
