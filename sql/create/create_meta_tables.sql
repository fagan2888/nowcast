-- A table that stores the control variables of the Nowcasting model
--- run (1) after create_meta_tables.sql

-- Control Variables: model
CREATE TABLE IF NOT EXISTS meta_control_variables (
 	variable_id 			INTEGER NOT NULL AUTO_INCREMENT,
    variable_name			VARCHAR(20) NOT NULL,
    variable_description	TEXT,
	PRIMARY KEY             (variable_id),
    UNIQUE  KEY             meta_control_variables_ix (variable_name)
    ) ENGINE=INNODB;

INSERT INTO meta_control_variables
    (variable_name, variable_description)
VALUES
	("plag", "The lag of the idiosyncratic components"),
    ("hor", "The forecast horizon"),
    ("qlag", "The lag for the factor components"),
    ("Nx", "Number of Factors"),
    ("modelType", "The type of the model"),
    ("high", "The high range of the estimate in standard deviations"),
    ("low", "The low range of the estimate in standard deviations")
ON DUPLICATE KEY UPDATE variable_name = variable_name;


-- Release Frequencies: data
CREATE TABLE IF NOT EXISTS meta_release_frequencies (
	frequency_id 	INTEGER NOT NULL AUTO_INCREMENT,
	frequency 	    VARCHAR(2) NOT NULL ,
    frequency_text 	VARCHAR(15) NOT NULL,
    frequency_info 	TEXT NOT NULL,
    PRIMARY KEY     (frequency_id),
    UNIQUE  KEY        meta_release_frequencies_ix (frequency)
    ) ENGINE=INNODB;

INSERT INTO meta_release_frequencies
    (frequency, frequency_text, frequency_info)
VALUES
	('M', 'Minute', 'Release frequency of 1 minute/ every minute'),
	('H', 'Hourly', 'Release frequency of 1 hour'),
    ('d', 'Daily', 'Release frequency of 1 day'),
	('w', 'Weekly', 'Release frequency of 1 week'),
	('2w', 'Bi-Weekly', 'Release frequency of two weeks'),
    ('3w', 'Tri-Weekly', 'Release frequency of three weeks'),
	('m', 'Monthly', 'Release frequency of 1 month '),
	('2m', 'Bi-Monthly', 'Release frequency of 2 months'),
    ('6m', 'Half-Yearly', 'Release frequency every 6 months'),
    ('q', 'Quaterly', 'Release frequency every quarter'),
	('y', 'Yearly', 'Release frequency every year')
ON duplicate key update frequency = frequency;


-- Presentation Units: output
CREATE TABLE IF NOT EXISTS meta_presentation_units (
	unit_id				INTEGER AUTO_INCREMENT,
	presentation_unit 	VARCHAR(25),
    unit_info			TEXT NOT NULL,
    PRIMARY KEY         (unit_id),
    UNIQUE  KEY          meta_presentation_units_ix (presentation_unit)
    ) ENGINE=INNODB;

INSERT INTO meta_presentation_units
    (presentation_unit, unit_info)
VALUES
	('Index', 'Index based unit'),
	('QoQ, AR (%)', 'Quarter on Quarter, Annualised Rate percentage'),
	('Annual Rate (%)', 'Annual Rate change in percent'),
    ('QoQ SAAR (%)', 'Quarter on Quarter Seasonally Adjusted Annual Rate'),
    ('y_{t,i}', 'Raw observation'),
    ('%', 'Percentage')
ON DUPLICATE KEY UPDATE unit_id = unit_id,presentation_unit = presentation_unit;


-- Indicator Types: data
CREATE TABLE IF NOT EXISTS meta_indicator_types (
	indicator_type_id 	INTEGER AUTO_INCREMENT,
	indicator_origin	VARCHAR (50) NOT NULL,
	PRIMARY KEY        (indicator_type_id),
	UNIQUE  KEY        meta_indicator_type_ix (indicator_origin)
	) ENGINE = INNODB;

INSERT INTO meta_indicator_types
	(indicator_origin)
VALUES
	('Surveys'),
	('Labour Market'),
	('Production and Trade'),
	('Consumption and Income'),
	('Quarterly Series'),
    ('Forecast')
ON DUPLICATE KEY UPDATE indicator_origin = indicator_origin, indicator_type_id = indicator_type_id;

-- meta_data_transformations
CREATE TABLE IF NOT EXISTS meta_data_transformations (
    transformation_id           INTEGER NOT NULL PRIMARY KEY UNIQUE,
    transformation_description  varchar(50)
    ) ENGINE INNODB;


INSERT INTO meta_data_transformations
    (transformation_id, transformation_description)
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



-- Run Type
CREATE TABLE IF NOT EXISTS meta_run_type (
    run_type_id     INTEGER NOT NULL,
    run_type_name   VARCHAR(20),
    PRIMARY KEY 	(run_type_id),
    UNIQUE KEY 		meta_run_type_ix (run_type_id)
    ) ENGINE=INNODB;

INSERT INTO
    meta_run_type (run_type_id, run_type_name)
VALUES
    (1, "Development"),
    (2, "Backtesting"),
    (3, "Production")
ON DUPLICATE KEY UPDATE run_type_id = run_type_id, run_type_name = run_type_name;


-- Forecast Types
CREATE TABLE IF NOT EXISTS meta_forecast_types (
    forecast_type_id 	INTEGER NOT NULL AUTO_INCREMENT,
	forecast_type 		VARCHAR(25) NOT NULL,
    forecast_info 		TEXT,
    PRIMARY KEY 		(forecast_type_id),
    UNIQUE KEY 			meta_forecast_types_ix(forecast_type_id, forecast_type)
    ) ENGINE=INNODB;


INSERT INTO meta_forecast_types
    (forecast_type, forecast_info)
VALUES
	("Backcast", "Describing in sample observations"),
    ("Nowcast",  "Describing some in sample data"),
    ("Forecast", "Describing out of sample data")
ON DUPLICATE KEY UPDATE forecast_type_id = forecast_type_id;

-- Create table for all country  with a unique country id, name, iso characters  and iso number
-- Country_id | country_name | iso_alpha_2 (2-character ISO code) | iso_alpha_3 (3 digiti ISO code) | iso_number

CREATE TABLE IF NOT EXISTS meta_master_country (
    country_id 		INTEGER NOT NULL AUTO_INCREMENT,
	country_name 	VARCHAR(50) NOT NULL,
	iso_alpha_2 	VARCHAR(2) NOT NULL,
	iso_alpha_3 	VARCHAR(3) NOT NULL,
	iso_number 		INTEGER NOT NULL,
    PRIMARY KEY     (country_id),
    UNIQUE KEY      (country_name, iso_alpha_2, iso_alpha_3, iso_number)
    ) ENGINE=INNODB;

INSERT INTO meta_master_country (country_name, iso_alpha_2, iso_alpha_3, iso_number) VALUES
    ('Afghanistan','AF','AFG',4),
    ('Albania','AL','ALB',8),
    ('Algeria','DZ','DZA',12),
    ('Andorra','AD','AND',20),
    ('Angola','AO','AGO',24),
    ('Antigua and Barbuda','AG','ATG',28),
    ('Argentina','AR','ARG',32),
    ('Armenia','AM','ARM',51),
    ('Australia','AU','AUS',36),
    ('Austria','AT','AUT',40),
    ('Azerbaijan','AZ','AZE',31),
    ('Bahamas,The','BS','BHS',44),
    ('Bahrain','BH','BHR',48),
    ('Bangladesh','BD','BGD',50),
    ('Barbados','BB','BRB',52),
    ('Belarus','BY','BLR',112),
    ('Belgium','BE','BEL',56),
    ('Belize','BZ','BLZ',84),
    ('Benin','BJ','BEN',204),
    ('Bhutan','BT','BTN',64),
    ('Bolivia','BO','BOL',68),
    ('Bosnia and Herzegovina','BA','BIH',70),
    ('Botswana','BW','BWA',72),
    ('Brazil','BR','BRA',76),
    ('Brunei','BN','BRN',96),
    ('Bulgaria','BG','BGR',100),
    ('Burkina Faso','BF','BFA',854),
    ('Burundi','BI','BDI',108),
    ('Cambodia','KH','KHM',116),
    ('Cameroon','CM','CMR',120),
    ('Canada','CA','CAN',124),
    ('Cape Verde','CV','CPV',132),
    ('Central African Republic','CF','CAF',140),
    ('Chad','TD','TCD',148),
    ('Chile','CL','CHL',152),
    ('China, People\'s Republic of','CN','CHN',156),
    ('Colombia','CO','COL',170),
    ('Comoros','KM','COM',174),
    ('Congo,(Congo-Kinshasa)','CD','COD',180),
    ('Congo,(Congo-Brazzaville)','CG','COG',178),
    ('Costa Rica','CR','CRI',188),
    ('Cote d\'Ivoire (\'Ivory Coast)','CI','CIV',384),
    ('Croatia','HR','HRV',191),
    ('Cuba','CU','CUB',192),
    ('Cyprus','CY','CYP',196),
    ('Czech Republic','CZ','CZE',203),
    ('Denmark','DK','DNK',208),
    ('Djibouti','DJ','DJI',262),
    ('Dominica','DM','DMA',212),
    ('Dominican Republic','DO','DOM',214),
    ('Ecuador','EC','ECU',218),
    ('Egypt','EG','EGY',818),
    ('El Salvador','SV','SLV',222),
    ('Equatorial Guinea','GQ','GNQ',226),
    ('Eritrea','ER','ERI',232),
    ('Estonia','EE','EST',233),
    ('Ethiopia','ET','ETH',231),
    ('Fiji','FJ','FJI',242),
    ('Finland','FI','FIN',246),
    ('France','FR','FRA',250),
    ('Gabon','GA','GAB',266),
    ('Gambia The','GM','GMB',270),
    ('Georgia','GE','GEO',268),
    ('Germany','DE','DEU',276),
    ('Ghana','GH','GHA',288),
    ('Greece','GR','GRC',300),
    ('Grenada','GD','GRD',308),
    ('Guatemala','GT','GTM',320),
    ('Guinea','GN','GIN',324),
    ('Guinea-Bissau','GW','GNB',624),
    ('Guyana','GY','GUY',328),
    ('Haiti','HT','HTI',332),
    ('Honduras','HN','HND',340),
    ('Hungary','HU','HUN',348),
    ('Iceland','IS','ISL',352),
    ('India','IN','IND',356),
    ('Indonesia','ID','IDN',360),
    ('Iran','IR','IRN',364),
    ('Iraq','IQ','IRQ',368),
    ('Ireland','IE','IRL',372),
    ('Israel','IL','ISR',376),
    ('Italy','IT','ITA',380),
    ('Jamaica','JM','JAM',388),
    ('Japan','JP','JPN',392),
    ('Jordan','JO','JOR',400),
    ('Kazakhstan','KZ','KAZ',398),
    ('Kenya','KE','KEN',404),
    ('Kiribati','KI','KIR',296),
    ('Korea North','KP','PRK',408),
    ('Korea South','KR','KOR',410),
    ('Kuwait','KW','KWT',414),
    ('Kyrgyzstan','KG','KGZ',417),
    ('Laos','LA','LAO',418),
    ('Latvia','LV','LVA',428),
    ('Lebanon','LB','LBN',422),
    ('Lesotho','LS','LSO',426),
    ('Liberia','LR','LBR',430),
    ('Libya','LY','LBY',434),
    ('Liechtenstein','LI','LIE',438),
    ('Lithuania','LT','LTU',440),
    ('Luxembourg','LU','LUX',442),
    ('Macedonia','MK','MKD',807),
    ('Madagascar','MG','MDG',450),
    ('Malawi','MW','MWI',454),
    ('Malaysia','MY','MYS',458),
    ('Maldives','MV','MDV',462),
    ('Mali','ML','MLI',466),
    ('Malta','MT','MLT',470),
    ('Marshall Islands','MH','MHL',584),
    ('Mauritania','MR','MRT',478),
    ('Mauritius','MU','MUS',480),
    ('Mexico','MX','MEX',484),
    ('Micronesia','FM','FSM',583),
    ('Moldova','MD','MDA',498),
    ('Monaco','MC','MCO',492),
    ('Mongolia','MN','MNG',496),
    ('Montenegro','ME','MNE',499),
    ('Morocco','MA','MAR',504),
    ('Mozambique','MZ','MOZ',508),
    ('Myanmar (Burma)','MM','MMR',104),
    ('Namibia','NA','NAM',516),
    ('Nauru','NR','NRU',520),
    ('Nepal','NP','NPL',524),
    ('Netherlands','NL','NLD',528),
    ('New Zealand','NZ','NZL',554),
    ('Nicaragua','NI','NIC',558),
    ('Niger','NE','NER',562),
    ('Nigeria','NG','NGA',566),
    ('Norway','NO','NOR',578),
    ('Oman','OM','OMN',512),
    ('Pakistan','PK','PAK',586),
    ('Palau','PW','PLW',585),
    ('Panama','PA','PAN',591),
    ('Papua New Guinea','PG','PNG',598),
    ('Paraguay','PY','PRY',600),
    ('Peru','PE','PER',604),
    ('Philippines','PH','PHL',608),
    ('Poland','PL','POL',616),
    ('Portugal','PT','PRT',620),
    ('Qatar','QA','QAT',634),
    ('Romania','RO','ROU',642),
    ('Russia','RU','RUS',643),
    ('Rwanda','RW','RWA',646),
    ('Saint Kitts and Nevis','KN','KNA',659),
    ('Saint Lucia','LC','LCA',662),
    ('Saint Vincent and the Grenadines','VC','VCT',670),
    ('Samoa','WS','WSM',882),
    ('San Marino','SM','SMR',674),
    ('Sao Tome and Principe','ST','STP',678),
    ('Saudi Arabia','SA','SAU',682),
    ('Senegal','SN','SEN',686),
    ('Serbia','RS','SRB',688),
    ('Seychelles','SC','SYC',690),
    ('Sierra Leone','SL','SLE',694),
    ('Singapore','SG','SGP',702),
    ('Slovakia','SK','SVK',703),
    ('Slovenia','SI','SVN',705),
    ('Solomon Islands','SB','SLB',90),
    ('Somalia','SO','SOM',706),
    ('South Africa','ZA','ZAF',710),
    ('Spain','ES','ESP',724),
    ('Sri Lanka','LK','LKA',144),
    ('Sudan','SD','SDN',736),
    ('Suriname','SR','SUR',740),
    ('Swaziland','SZ','SWZ',748),
    ('Sweden','SE','SWE',752),
    ('Switzerland','CH','CHE',756),
    ('Syria','SY','SYR',760),
    ('Tajikistan','TJ','TJK',762),
    ('Tanzania','TZ','TZA',834),
    ('Thailand','TH','THA',764),
    ('Timor-Leste (East Timor)','TL','TLS',626),
    ('Togo','TG','TGO',768),
    ('Tonga','TO','TON',776),
    ('Trinidad and Tobago','TT','TTO',780),
    ('Tunisia','TN','TUN',788),
    ('Turkey','TR','TUR',792),
    ('Turkmenistan','TM','TKM',795),
    ('Tuvalu','TV','TUV',798),
    ('Uganda','UG','UGA',800),
    ('Ukraine','UA','UKR',804),
    ('United Arab Emirates','AE','ARE',784),
    ('United Kingdom','GB','GBR',826),
    ('United States','US','USA',840),
    ('Uruguay','UY','URY',858),
    ('Uzbekistan','UZ','UZB',860),
    ('Vanuatu','VU','VUT',548),
    ('Vatican City','VA','VAT',336),
    ('Venezuela','VE','VEN',862),
    ('Vietnam','VN','VNM',704),
    ('Yemen','YE','YEM',887),
    ('Zambia','ZM','ZMB',894),
    ('Zimbabwe','ZW','ZWE',716),
    ('Abkhazia','GE','GEO',268),
    ('China, Republic of (Taiwan)','TW','TWN',158),
    ('Nagorno-Karabakh','AZ','AZE',31),
    ('Northern Cyprus','CY','CYP',196),
    ('Pridnestrovie (Transnistria)','MD','MDA',498),
    ('Somaliland','SO','SOM',706),
    ('South Ossetia','GE','GEO',268),
    ('Ashmore and Cartier Islands','AU','AUS',36),
    ('Christmas Island','CX','CXR',162),
    ('Cocos (Keeling), Islands','CC','CCK',166),
    ('Coral Sea Islands','AU','AUS',36),
    ('Heard Island and McDonald Islands','HM','HMD',334),
    ('Norfolk Island','NF','NFK',574),
    ('New Caledonia','NC','NCL',540),
    ('French Polynesia','PF','PYF',258),
    ('Mayotte','YT','MYT',175),
    ('Saint Barthelemy','GP','GLP',312),
    ('Saint Martin','GP','GLP',312),
    ('Saint Pierre and Miquelon','PM','SPM',666),
    ('Wallis and Futuna','WF','WLF',876),
    ('French Southern and Antarctic Lands','TF','ATF',260),
    ('Clipperton Island','PF','PYF',258),
    ('Bouvet Island','BV','BVT',74),
    ('Cook Islands','CK','COK',184),
    ('Niue','NU','NIU',570),
    ('Tokelau','TK','TKL',772),
    ('Guernsey','GG','GGY',831),
    ('Isle of Man','IM','IMN',833),
    ('Jersey','JE','JEY',832),
    ('Anguilla','AI','AIA',660),
    ('Bermuda','BM','BMU',60),
    ('British Indian Ocean Territory','IO','IOT',86),
    ('British Virgin Islands','VG','VGB',92),
    ('Cayman Islands','KY','CYM',136),
    ('Falkland Islands (Islas Malvinas)','FK','FLK',238),
    ('Gibraltar','GI','GIB',292),
    ('Montserrat','MS','MSR',500),
    ('Pitcairn Islands','PN','PCN',612),
    ('Saint Helena','SH','SHN',654),
    ('South Georgia & South Sandwich Islands','GS','SGS',239),
    ('Turks and Caicos Islands','TC','TCA',796),
    ('Northern Mariana Islands','MP','MNP',580),
    ('Puerto Rico','PR','PRI',630),
    ('American Samoa','AS','ASM',16),
    ('Baker Island','UM','UMI',581),
    ('Guam','GU','GUM',316),
    ('Howland Island','UM','UMI',581),
    ('Jarvis Island','UM','UMI',581),
    ('Johnston Atoll','UM','UMI',581),
    ('Kingman Reef','UM','UMI',581),
    ('Midway Islands','UM','UMI',581),
    ('Navassa Island','UM','UMI',581),
    ('Palmyra Atoll','UM','UMI',581),
    ('U.S. Virgin Islands','VI','VIR',850),
    ('Wake Island','UM','UMI',850),
    ('Hong Kong','HK','HKG',344),
    ('Macau','MO','MAC',446),
    ('Faroe Islands','FO','FRO',234),
    ('Greenland','GL','GRL',304),
    ('French Guiana','GF','GUF',254),
    ('Guadeloupe','GP','GLP',312),
    ('Martinique','MQ','MTQ',474),
    ('Reunion','RE','REU',638),
    ('Aland','AX','ALA',248),
    ('Aruba','AW','ABW',533),
    ('Netherlands Antilles','AN','ANT',530),
    ('Svalbard','SJ','SJM',744),
    ('Australian Antarctic Territory','AQ','ATA',10),
    ('Ross Dependency','AQ','ATA',10),
    ('Peter I Island','AQ','ATA',10),
    ('Queen Maud Land','AQ','ATA',10),
    ('British Antarctic Territory','AQ','ATA',10)
ON DUPLICATE KEY UPDATE country_name = country_name, iso_alpha_2 = iso_alpha_2, iso_alpha_3 = iso_alpha_3, iso_number = iso_number;
