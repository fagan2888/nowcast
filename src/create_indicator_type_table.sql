
CREATE TABLE IF NOT EXISTS indicator_types( indicator_type_id 	INTEGER AUTO_INCREMENT,
											indicator_origin	VARCHAR (50) NOT NULL,
											PRIMARY KEY(indicator_type_id),
											UNIQUE inidicator_type_ix(indicator_origin)
										)ENGINE = INNODB;
                                    
INSERT INTO indicator_types (indicator_origin) VALUES ('Surveys'),
													('Labour Market'),
													('Production and Trade'),
													('Consumption and Income'),
													('Quarterly Series'),
                                                    ('Forecast') ON DUPLICATE KEY UPDATE indicator_origin = indicator_origin, indicator_type_id = indicator_type_id;
													
                                    