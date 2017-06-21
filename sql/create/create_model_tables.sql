--- run (3) after (1) create_meta_tables.sql and (2) create_data_tables.sql

-- DROP TABLE IF EXISTS model_indicators CASCADE;
-- DROP TABLE IF EXISTS model_controls CASCADE;
-- DROP TABLE IF EXISTS model_references CASCADE;
-- DROP TABLE IF EXISTS model_types CASCADE;

-- Model Types
CREATE TABLE IF NOT EXISTS model_types (
    model_type_id   INTEGER NOT NULL AUTO_INCREMENT,
    model_type_name varchar(100) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (model_type_id),
    UNIQUE KEY model_types_ix (model_type_name)
    )
ENGINE=INNODB;

INSERT INTO model_types
    (model_type_name)
VALUES
    ('MS Dynamic Factor Model')
ON DUPLICATE KEY UPDATE model_type_id = model_type_id, model_type_name = model_type_name;


-- Reference Table
CREATE TABLE IF NOT EXISTS model_references (
    model_id            INTEGER NOT NULL AUTO_INCREMENT,
    model_name          VARCHAR(50) NOT NULL,
    target_country_id   INTEGER NOT NULL,
    target_variable_id  INTEGER NOT NULL,
    model_type          INTEGER,
    created_by          VARCHAR(50) NOT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (model_id),
    UNIQUE KEY  model_references_ix (model_name),
    CONSTRAINT model_references_fk1 FOREIGN KEY (model_type)
        REFERENCES model_types (model_type_id) ON DELETE CASCADE,
    CONSTRAINT model_references_fk2 FOREIGN KEY (target_country_id)
        REFERENCES meta_master_country (country_id) ON DELETE CASCADE,
    CONSTRAINT model_references_fk3 FOREIGN KEY (target_variable_id)
        REFERENCES data_variable_id (variable_id) ON DELETE CASCADE
    )
ENGINE=INNODB;


-- Controls of the Models
CREATE TABLE IF NOT EXISTS model_controls (
    model_id        INTEGER NOT NULL,
    control_id      INTEGER NOT NULL,
    control_values 	FLOAT NOT NULL,
    PRIMARY KEY     (model_id, control_id),
    UNIQUE KEY      model_controls_ix (model_id, control_id),
	CONSTRAINT model_control_fk1 FOREIGN KEY (model_id)
        REFERENCES model_references (model_id) ON DELETE CASCADE,
    CONSTRAINT model_controls_fk2 FOREIGN KEY (control_id)
        REFERENCES meta_control_variables (variable_id) ON DELETE CASCADE
    )
ENGINE=INNODB;


-- Indicators of the Model
CREATE TABLE IF NOT EXISTS model_indicators (
    model_id            INTEGER NOT NULL,
    indicator_id        INTEGER NOT NULL,
    transformation_code INTEGER NOT NULL,
    presentation_code   INTEGER NOT NULL,
    PRIMARY KEY         (model_id, indicator_id),
    UNIQUE KEY          model_indicators_ix (model_id, indicator_id),
	CONSTRAINT model_indicators_fk1 FOREIGN KEY (model_id)
		REFERENCES model_references (model_id) ON DELETE CASCADE,
	CONSTRAINT model_indicators_fk2 FOREIGN KEY (indicator_id)
		REFERENCES data_indicators (indicator_id) ON DELETE CASCADE,
    CONSTRAINT model_indicators_fk3 FOREIGN KEY (transformation_code)
		REFERENCES meta_data_transformations (transformation_id) ON DELETE CASCADE,
	CONSTRAINT model_indicators_fk4 FOREIGN KEY (presentation_code)
		REFERENCES meta_data_transformations (transformation_id) ON DELETE CASCADE
    )
ENGINE=INNODB;
