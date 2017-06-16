CREATE TABLE IF NOT EXISTS meta_last_updated (
    dataset_id INTEGER NOT NULL AUTO_INCREMENT,
    dataset varchar(20) NOT NULL,
    last_updated DATETIME NOT NULL,
    PRIMARY KEY dataset
    UNIQUE KEY meta_last_updated_ix (dataset_id)
    CONSTRAINT meta_last_updated_ibfk_1 FOREIGN KEY (dataset)
		REFERENCES information_schema.tables (table_name) ON DELETE CASCADE
    ) ENGINE = INNODB;
