

CREATE TABLE IF NOT EXISTS presentation_units (	unit_id				INTEGER AUTO_INCREMENT,
												presentation_unit 	VARCHAR(25),
                                                unit_info			TEXT NOT NULL,
                                                PRIMARY KEY (unit_id),
                                                UNIQUE presentation_unit_ix (presentation_unit)
                                                )ENGINE=INNODB;
                                                
INSERT INTO presentation_units (presentation_unit, unit_info) VALUES 
																('Index', 'Index based unit'),
																('QoQ, AR (%)', 'Quarter on Quarter, Annualised Rate percentage'),
																('Annual Rate (%)', 'Annual Rate change in percent'),
                                                                ('QoQ SAAR (%)', 'Quarter on Quarter Seasonally Adjusted Annual Rate'),
                                                                ('y_{t,i}', 'Raw observation'),
                                                                ('%', 'Percentage') ON DUPLICATE KEY UPDATE unit_id = unit_id,presentation_unit = presentation_unit;
                                                