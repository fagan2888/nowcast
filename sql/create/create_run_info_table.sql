

CREATE TABLE IF NOT EXISTS run_info(
	run_id 			INTEGER NOT NULL,
	model_id 		INTEGER NOT NULL,
	information_set TIMESTAMP,
	svn_repository 	VARCHAR(80),
	svn_revision	INTEGER,
	CONSTRAINT run_info_ibfk_1 FOREIGN KEY (run_id)
		REFERENCES run_table(run_id) ON DELETE CASCADE,
	CONSTRAINT run_info_ibfk_2 FOREIGN KEY (model_id)
		REFERENCES model_references(model_id) ON DELETE CASCADE,
	PRIMARY KEY (run_id),
    UNIQUE (run_id)
    )ENGINE = INNODB;
