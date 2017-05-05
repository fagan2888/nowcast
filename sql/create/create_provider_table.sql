-- Script to create a table for data_providers
-- provider_id | provider_name

CREATE TABLE IF NOT EXISTS data_provider(	provider_id 	INTEGER NOT NULL AUTO_INCREMENT,
											provider_name 	VARCHAR(25),
											PRIMARY KEY (provider_id),
											UNIQUE provider_ix (provider_name)
                                            ) ENGINE=INNODB;

INSERT INTO data_provider
	(provider_name)
VALUES
	('MacroBond'),
	('Bloomberg'),
	('St. Louis Fed Fred, US'),
	('St. Louis Fed Alfred, US'),
	('BEA, US'),
	('BLS, US')
ON DUPLICATE KEY UPDATE provider_name = provider_name;
