DROP TABLE IF EXISTS model_indicators CASCADE;
DROP TABLE IF EXISTS model_controls CASCADE;
DROP TABLE IF EXISTS model_references CASCADE;
DROP TABLE IF EXISTS model_types CASCADE;
DROP TABLE IF EXISTS model_transformations CASCADE;

-- Create Model Types
CREATE TABLE IF NOT EXISTS model_types (
    model_type_id   INTEGER NOT NULL AUTO_INCREMENT,
    model_type_name varchar(100) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (model_type_id),
    UNIQUE KEY model_types_ix (model_type_name)
    )
ENGINE=INNODB;

INSERT INTO model_types (model_type_name) VALUES ('MS Dynamic Factor Model')
ON duplicate key update model_type_id = model_type_id, model_type_name = model_type_name;


select * from model_types;

-- Reference Table
CREATE TABLE IF NOT EXISTS model_references (
    model_id    INTEGER NOT NULL AUTO_INCREMENT,
    model_name  VARCHAR(50) NOT NULL,
    target_country_id   INTEGER NOT NULL,
    target_indicator_id INTEGER NOT NULL,
    model_type  INTEGER,
    created_by  VARCHAR(50) NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (model_id),
    CONSTRAINT model_references_fk1 FOREIGN KEY (model_type)
        REFERENCES model_types (model_type_id) ON DELETE CASCADE,
    CONSTRAINT model_references_fk2 FOREIGN KEY (target_country_id)
        REFERENCES master_country (country_id) ON DELETE CASCADE,
    CONSTRAINT model_references_fk3 FOREIGN KEY (target_indicator_id)
        REFERENCES indicators (indicator_id) ON DELETE CASCADE,
    UNIQUE KEY model_references_ix (model_name)
    )
ENGINE=INNODB;

select * from model_references;

-- Controls of the Models
CREATE TABLE IF NOT EXISTS model_controls (
    model_id        INTEGER NOT NULL,
    control_id      INTEGER NOT NULL,
    control_values 	FLOAT NOT NULL,
	CONSTRAINT model_control_fk1 FOREIGN KEY (model_id)
        REFERENCES model_references (model_id) ON DELETE CASCADE,
    CONSTRAINT model_controls_fk2 FOREIGN KEY (control_id)
        REFERENCES control_variables (variable_id) ON DELETE CASCADE,
    PRIMARY KEY (model_id, control_id),
    UNIQUE KEY model_controls_ix (model_id, control_id)
    )
ENGINE=INNODB;


-- model_transformations
CREATE TABLE IF NOT EXISTS model_transformations(
    transformation_id INTEGER NOT NULL UNIQUE PRIMARY KEY,
    transformation_description varchar(50)
    )
ENGINE INNODB;

INSERT INTO
    model_transformations (transformation_id, transformation_description)
VALUES
    (0, "X_{t}"),
    (1, "\log(X_{t})"),
    (2, "\Delta_{1} X_{t}"),
    (3, "\Delta_{3} X_{t}"),
    (4, "\Delta_{12} X_{t}"),
    (5, "100*\Delta_{1}\log(X_{t})"),
    (6, "400*\Delta_{3}\log(X_{t})"),
    (7, "100*\Delta_{3}\Delta_{12}\log(X_{t})")
ON duplicate key update transformation_id = transformation_id;


-- Indicators of the Model
CREATE TABLE IF NOT EXISTS model_indicators (
    model_id   INTEGER NOT NULL,
    indicator_id INTEGER NOT NULL,
    transformation_code INTEGER NOT NULL,
    presentation_code INTEGER NOT NULL,
    PRIMARY KEY (model_id, indicator_id),
	CONSTRAINT model_indicators_fk1 FOREIGN KEY (model_id)
		REFERENCES model_references (model_id) ON DELETE CASCADE,
	CONSTRAINT model_indicators_fk2 FOREIGN KEY (indicator_id)
		REFERENCES indicators (indicator_id) ON DELETE CASCADE,
    CONSTRAINT model_indicators_fk3 FOREIGN KEY (transformation_code)
		REFERENCES model_transformations (transformation_id) ON DELETE CASCADE,
	CONSTRAINT model_indicators_fk4 FOREIGN KEY (presentation_code)
		REFERENCES model_transformations (transformation_id) ON DELETE CASCADE,
    UNIQUE KEY model_indicators_ix (model_id, indicator_id)
    )
ENGINE=INNODB;
