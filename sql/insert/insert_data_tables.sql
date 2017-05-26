

INSERT INTO data_provider
	(provider_name, provider_long_name)
VALUES
	('MB', 		'Macrobond'),
	('BLP', 	'Bloomberg'),
	('Fred', 	'St. Louis Fed Fred, US'),
	('Alfred', 	'St. Louis Fed Alfred, US'),
	('BEA', 	'Bureau of Economic Analysis, US'),
	('BLS', 	'Bureau of Labour Studies, US'),
	('EIA', 	'Energy Information Administration, US'),
	('US Census', 'U.S. Census'),
	('CEIC',	'CEIC Data'),
	('MSP', 	'Macrosynergy Partners')
ON DUPLICATE KEY UPDATE provider_name = provider_name, provider_long_name = provider_long_name;

-----------------------------------
-- Institute for Supply Management (ISM) datasets
INSERT INTO data_sources
	(source_id, source_name, source_description)
VALUES
	(1, 'ISM', 'Institute For Supply Management')
ON duplicate key update source_id = source_id;

INSERT INTO data_variable_id
    (variable_id, variable_name, variable_description, source_id, dataset, frequency_id, country_id, indicator_type, publication_lags)
VALUES
    (1, 'Manufacturing PMI', 'Manufacturing, Purchasing Managers Index', 1, 'Business Surveys', 7, 184, 1, 0),
    (2, 'Non-Manufacturing PMI', 'Non-Manufacturing, Purchasing Managers Index', 1, 'Business Surveys', 7, 184, 1, 0),
	(3, 'Business Barometer, SA', 'Chicago Business Barometer, Business Barometer, SA', 1, 'Business Surveys', 7, 184, 1, 0)
ON duplicate key update variable_id = variable_id, variable_name = variable_name;

INSERT INTO data_indicators
	(provider_id, vendor_key, variable_id)
VALUES
	(1, 'ussurv1055',  1),
	(1, 'ussurv1044',  2),
	(1, 'ussurv1363',  3)
ON duplicate key update vendor_key = vendor_key;

-----------------------------------
-- Conference Board datasets
INSERT INTO data_sources
	(source_id, source_name, source_description)
VALUES
	(2, 'Conference Board', 'The Conference Board')
ON duplicate key update source_id = source_id;

INSERT INTO data_variable_id
    (variable_id, variable_name, variable_description, source_id, dataset, frequency_id, country_id, indicator_type, publication_lags)
VALUES
	(4, 'Consumer Confidence Index, SA','Consumer Confidence Index, Total, Total, SA', 2,'Consumer Surveys', 7, 184, 1, 0)
ON duplicate key update variable_id = variable_id;

INSERT INTO data_indicators
	(provider_id, vendor_key, variable_id)
VALUES
	(1, 'ussurv1459',  4)
ON duplicate key update vendor_key = vendor_key;

-----------------------------------
-- University of Michigan
INSERT INTO data_sources
	(source_id, source_name, source_description)
VALUES
	(3, 'University of Michigan', 'University of Michigan')
ON duplicate key update source_id = source_id;

INSERT INTO data_variable_id
    (variable_id, variable_name, variable_description, source_id, dataset, frequency_id, country_id, indicator_type, publication_lags)
VALUES
	(5, 'Consumer Sentiment Index','Consumer Sentiment Index', 3, 'Consumer Surveys', 7, 184, 1, 0)
ON duplicate key update variable_id = variable_id;

INSERT INTO data_indicators
	(provider_id, vendor_key, variable_id)
VALUES
	(1, 'ussurv0354',  5)
ON duplicate key update vendor_key = vendor_key;

-----------------------------------
-- Federal Reserve Bank of Philadelphia
INSERT INTO data_sources
	(source_id, source_name, source_description)
VALUES
	(4, 'Federal Reserve Bank of Philadelphia', 'Federal Reserve Bank of Philadelphia')
ON duplicate key update source_id = source_id;

INSERT INTO data_variable_id
    (variable_id, variable_name, variable_description, source_id, dataset, frequency_id, country_id, indicator_type, publication_lags)
VALUES
	(6, 'Business Outlook Survey Manufacturing', 'Manufacturing, Current General Activity, Diffusion, SA', 4, 'Business Outlook Survey', 7, 184, 1, 0),
	(7, 'Anxious Index', 'Probability of Declie in Real GDP in the Current Quarter', 4, 'Survey of Professional Forecasters', 7,184, 6, 0)
ON duplicate key update variable_id = variable_id;

INSERT INTO data_indicators
	(provider_id, vendor_key, variable_id)
VALUES
	(1, 'ussurv1102',  6),
	(1, 'usfcst0074',  7)
ON duplicate key update vendor_key = vendor_key;


-----------------------------------
-- BLS
INSERT INTO	data_sources
	(source_id, source_name, source_description)
VALUES
	(5, 'BLS', 'United States Bureau of Labour Statistics')
ON duplicate key update source_id = source_id;

INSERT INTO data_variable_id
    (variable_id, variable_name, variable_description, source_id, dataset, frequency_id, country_id, indicator_type)
VALUES
	(8, 'Hours Worked Average Weekly', 'Hours Worked, Average Weekly, Production & Non-Supervisory Employees, Total Private, SA', 5, 'Productivity, Costs & Hours Worked', 7, 184, 2),
	(9, 'Unemployment', 'Unemployment, CPS, 16 Years & Over, Rate, SA', 5, 'Employment', 7, 184, 2),
	(10, 'Employment Non-Farm Payroll', 'Employment, CES, Nonfarm, Payroll, Total, SA', 5, 'Employment', 7, 184, 2),
	(11, 'Employment Participation Rate', 'Civilian Labour Force Participation Rate, Women & Men, 16 Years & Over, SA', 5, 'Employment', 7, 184, 2),
	(12, 'Consumer Price Index', 'Consumer Price Index, All Urban Consumers, U.S. City Average, All Items, SA', 5, 'CPI', 7, 184, 4)
ON duplicate key update variable_id = variable_id;

INSERT INTO data_indicators
	(provider_id, vendor_key, variable_id)
VALUES
	(1, 'uslama1135',  8),
	(1, 'uslama1849',  9),
	(1, 'uslama1060', 10),
	(1, 'uslama4486', 11),
	(1, 'uspric2156', 12)
ON duplicate key update vendor_key = vendor_key;

-----------------------------------
-- U.S. Census Bureau
INSERT INTO data_sources
	(source_id, source_name, source_description)
VALUES
	(6, 'U.S. Census Bureau', 'United States Census Bureau')
ON DUPLICATE KEY UPDATE source_id = source_id;

INSERT INTO data_variable_id
    (variable_id, variable_name, variable_description, source_id, dataset, frequency_id, country_id, indicator_type)
VALUES
	(13, 'Retail Sales', 'Retail Trade, Retail Sales, Total, Calendar Adjusted, SA, USD', 6, 'Domestic Trade', 7, 184, 3),
	(14, 'Whole Sales', 'Sales, Calendar Adjusted, SA, USD', 6, 'Domestic Trade', 7, 184, 3),
 	(15, 'Inventories', 'Inventories, Calendar Adjusted, SA, USD', 6, 'Domestic Trade', 7, 184, 3),
 	(16, 'Residential Construction Spending (nominal)', 'Private, Residential, Total, SA, AR, USCB, Spending', 6, 'Construction Finances', 7, 184, 4),
  	(17, 'Construction Started Residential', 'Construction Started, Residential, New Privately Owned, Total, SA, AR', 6, 'Construction by Status', 7, 184, 3),
  	(18, 'Permits, Residential, New Privately Owned, Total, SA, AR', 'Permits, Residential, National, New Privately Owned, Total, SA, AR', 6, 'Construction by Status', 7, 184, 3),
 	(19, 'Unfilled Orders Durable Goods', 'Unfilled Orders, Durable Goods, Total, All, SA, USD', 6, 'Production', 7, 184, 3),
	(20, 'New Orders Durable Goods', 'New Orders, Durable Goods, Total, All, SA, USD', 6, 'Production', 7, 184, 3),
 	(21, 'Manufacturing Inventories', 'Manufacturers Inventories, Total, Durable Goods, All, All, Current Prices, SA, USD', 6, 'Production', 7, 184, 3)
ON DUPLICATE KEY UPDATE variable_id = variable_id;

INSERT INTO data_indicators
	(provider_id, vendor_key, variable_id)
VALUES
	(1, 'ustrad0070', 13),
	(1, 'ustrad1020', 14),
	(1, 'ustrad0401', 15),
	(1, 'uscons2380', 16),
	(1, 'uscons1156', 17),
	(1, 'uscons1146', 18),
	(1, 'usprod1501', 19),
	(1, 'usprod1385', 20),
	(1, 'usprod0805', 21)
ON DUPLICATE KEY UPDATE vendor_key = vendor_key;


-------------------------------------------
-- BEA
INSERT INTO data_sources
	(source_id, source_name, source_description)
VALUES
	(7, 'BEA', 'United States Bureau of Economic Analysis')
ON duplicate key update source_id = source_id;

INSERT INTO data_variable_id
    (variable_id, variable_name, variable_description, source_id, dataset, frequency_id, country_id, indicator_type)
VALUES
	(22, 'Retail Sales', 'Retail Trade, Retail Sales, Total, Calendar Adjusted, SA, USD', 7, 'Domestic Trade', 7, 184, 3),
 	(22, 'Personal Consumption Expenditures','Personal Consumption Expenditures, Total, Constant Prices, SA, Index', 7,  'Expenditure Approach', 7, 184, 4),
 	(23, 'PCE Non-Durable, Real', 'Personal Consumption Expenditures, Non-Durable, Real, Total, Chained, SA, AR, USD', 7, 'Expenditure Approach', 7, 184, 4),
	(24, 'PCE Services, Nominal', 'Personal Consumption Expenditures, Services, Total,  SA, AR, USD', 7, 'Expenditure Approach', 7, 184, 4),
	(25, 'PCE Durable, Real', 'Personal Consumption Expenditures, Durable, Real, Total, Chained, SA, AR, USD', 7, 'Expenditure Approach', 7, 184, 4),
	(26, 'PCE Services, Real', 'Personal Consumption Expenditures, Services, Real, Total, Chained, SA, AR, USD', 7,'Expenditure Approach', 7, 184, 4),
	(27, 'Personal Consumption, Expenditures, Real', 'Personal Consumption Expenditures, Real, Total, Chained, SA, AR, USD', 7, 'Expenditure Appraoch', 7, 184, 4),
	(28, 'Manufacturing Sales, Real', 'Manufacturing & Trade, Sales, Total Business, Constant Prices,  SA, Chained, USD', 7, 'Domestic trade', 7, 184, 3),
	(29, 'Real Retail Sales and Food Service', 'Retail Trade, Retail & Food Service Sale, Constant Prices, SA, Chained USD', 7, 'Domestic Trade', 7, 184, 3),
	(30, 'Imports, Nominal', 'Import of Goods & Services, Total, Current Prices, SA, AR, USD', 7, 'Foreign Trade', 7, 184, 3),
	(31, 'Exports, Nominal', 'Export of Goods & Services, Total, Current Prices, SA, AR, USD', 7, 'Foreign Trade', 7, 184, 3),
	(32, 'PCE Service Price Index', 'Personal Consumption Expenditures, Services Price Index, SA', 7, 'Price', 7, 184, 4),
	(33, 'PCE Total Price Index', 'Personal Consumption Expenditures, Total Price Index, SA', 7,'Price', 7, 184, 4),
	(34, 'PCE Durable Goods Price Index', 'Personal Consumption Expenditures, Durable Goods Price Index, SA', 7, 'Price', 7, 184, 4),
	(35, 'PCE Non-Durable Goods Price Index', 'Personal Consumption Expenditures, Non-Durable Goods Price Index, SA', 7, 'Price', 7, 184, 4),
	(36, 'Disposable Personal Income, Real', 'Disposable Personal Income, Total, Constant Prices, SA, Chained, AR, USD', 7, 'Income Approach', 7, 184, 4),
	(37, 'PCE Durable Goods, Nominal', 'Personal Consumption Expenditures, Durable Goods, Total, SA, AR, USD', 7, 'Expenditure Approach', 7, 184, 4),
	(38, 'PCE Nondurable Goods, Nominal', 'Personal Consumption Expenditures, Non-durable Goods, Total, SA, AR, USD', 7, 'Expenditure Approach', 7, 184, 4),
	-- dataset: SNA / Quarterly National Accounts
	(39, 'Gross Domestic Product, Real', 'Gross Domestic Product, Total, Constant Prices, SA, Chained, AR, USD', 7, 'Expenditure Approach',  10, 184,  5)
ON DUPLICATE KEY UPDATE variable_id = variable_id;

INSERT INTO data_indicators
	(provider_id, vendor_key, variable_id)
VALUES
	(1, 'usnaac0591',  22),
	(1, 'usnaac0766',  23),
	(1, 'usnaac33313', 24),
	(1, 'usnaac0699',  25),
	(1, 'usnaac0844',  26),
	(1, 'usnaac0697',  27),
	(1, 'ustrad0350',  28),
	(1, 'ustrad0801',  29),
	(1, 'ustrad1990',  30),
	(1, 'ustrad1967',  31),
	(1, 'uspric0005',  32),
	(1, 'uspric0002',  33),
	(1, 'uspric0003',  34),
	(1, 'uspric0004',  35),
	(1, 'usnaac3029',  36),
	(1, 'usnaac33303', 37),
	(1, 'usnaac33308', 38),
	(1, 'usnaac0169',  39)
ON DUPLICATE KEY UPDATE vendor_key = vendor_key;


----------------------------
--- Extra U.S. Census Variables
INSERT INTO data_variable_id
    (variable_id, variable_name, variable_description, source_id, dataset, frequency_id, country_id, indicator_type)
VALUES
	(40, 'Imports, Real', 'Import, Total, Chained, Constant Prices, SA, USD', 6, 'Foreign Trade', 7, 184, 3),
	(41, 'Exports, Real', 'Export, Total, Chained, Constant Prices, SA, USD', 6, 'Foreign Trade', 7, 184, 3)
ON DUPLICATE KEY UPDATE variable_id = variable_id;

INSERT INTO data_indicators
	(provider_id, vendor_key, variable_id)
VALUES
	(1, 'ustrad1018', 40),
	(1, 'ustrad1014', 41)
ON DUPLICATE KEY UPDATE vendor_key = vendor_key;

-------------------------------
-- Federal Reserves
INSERT INTO	data_sources
	(source_id, source_name, source_description)
VALUES
	(8, 'Federal Reserves', 'United States Federal Reserves')
ON duplicate key update source_id = source_id;

INSERT INTO data_variable_id
    (variable_id, variable_name, variable_description, source_id, dataset, frequency_id, country_id, indicator_type)
VALUES
	(42, 'Industrial Production, Nominal', 'Industrial Production, Total, SA, Index', 8, 'Production', 7, 184, 3),
	(43, 'Capacity Utilisation', 'Capacity Utilization, Percent of Capacity, SA', 8, 'Production', 7, 184, 3)
ON DUPLICATE KEY UPDATE variable_id = variable_id;

INSERT INTO data_indicators
	(provider_id, vendor_key, variable_id)
VALUES
	(1, 'usprod1022', 42),
	(1, 'usprod1071', 43)
ON DUPLICATE KEY UPDATE vendor_key = vendor_key;


-------------------------------------------------------
-- Federal Reserve Bank of Philidelphia

INSERT INTO data_variable_id
    (variable_id, variable_name, variable_description, source_id, dataset, frequency_id, country_id, indicator_type)
VALUES
 	(44, 'Median Real GDP Growth rates', 'Real GDP, Current Quarter, Median', 4, 'Survey of Professional Forecasters', 10, 184, 6),
 	(45, 'Mean Real GDP Growth Rates', 'Real GDP, Current Quarter, Mean', 4, "Survey of Professional Forecasters", 10, 184, 6)
ON DUPLICATE KEY UPDATE variable_id = variable_id;

INSERT INTO data_indicators
	(provider_id, vendor_key, variable_id)
VALUES
	(1, 'usfcst1745', 44),
	(1, 'usfcst1810', 45)
ON DUPLICATE KEY UPDATE vendor_key = vendor_key;

----------------------------------------------
-- Federal Reserve Bank of Atlanta
INSERT INTO data_sources
	(source_id, source_name, source_description)
VALUES
	(9, 'Atlanta Fed', 'Federal Reserve Bank of Atlanta')
ON duplicate key update source_id = source_id;

INSERT INTO data_variable_id
    (variable_id, variable_name, variable_description, source_id, dataset, frequency_id, country_id, indicator_type)
VALUES
	(46, 'Atlanta Fed GDPnow 2017-Q2', 'Atlanta Fed GDPnow 2017-Q2 Mean Real GDP Growth rates (SAAR)', 9, 'GDPNow', 3, 184, 6),
 	(47, 'Atlanta Fed GDPnow 2017-Q1', 'Atlanta Fed GDPnow 2017-Q1 Mean Real GDP Growth rates (SAAR)', 9, 'GDPNow', 3, 184, 6),
 	(48, 'Atlanta Fed GDPnow 2016-Q4', 'Atlanta Fed GDPnow 2016-Q4 Mean Real GDP Growth rates (SAAR)', 9, 'GDPNow', 3, 184, 6),
 	(49, 'Atlanta Fed GDPnow 2016-Q3', 'Atlanta Fed GDPnow 2016-Q3 Mean Real GDP Growth rates (SAAR)', 9, 'GDPNow', 3, 184, 6),
 	(50, 'Atlanta Fed GDPnow 2016-Q2', 'Atlanta Fed GDPnow 2016-Q2 Mean Real GDP Growth rates (SAAR)', 9, 'GDPNow', 3, 184, 6),
 	(51, 'Atlanta Fed GDPnow 2016-Q1', 'Atlanta Fed GDPnow 2016-Q1 Mean Real GDP Growth rates (SAAR)', 9, 'GDPNow', 3, 184, 6),
 	(52, 'Atlanta Fed GDPnow 2015-Q4', 'Atlanta Fed GDPnow 2015-Q4 Mean Real GDP Growth rates (SAAR)', 9, 'GDPNow', 3, 184, 6)
ON DUPLICATE KEY UPDATE variable_id = variable_id;

INSERT INTO data_indicators
	(provider_id, vendor_key, variable_id)
VALUES
	(1, 'usfcst2473', 46),
	(1, 'usfcst1847', 47),
	(1, 'usfcst1884', 48),
	(1, 'usfcst1841', 49),
	(1, 'usfcst1469', 50),
	(1, 'usfcst0819', 51),
	(1, 'usfcst0803', 52)
ON DUPLICATE KEY UPDATE vendor_key = vendor_key;


----------------------------------------
-- Federal Reserve Bank of New York
INSERT INTO data_sources
	(source_id, source_name, source_description)
VALUES
	(10, 'New York Fed', 'Federal Reserve Bank of New York')
ON duplicate key update source_id = source_id;

INSERT INTO data_variable_id
    (variable_id, variable_name, variable_description, source_id, dataset, frequency_id, country_id, indicator_type)
VALUES
	(53, 'NY Fed GDP Nowcast Q2-2017', 'NY Fed GDP Nowcast Q2-2017', 10, 'NY Fed Nowcast', 3, 184, 6),
	(54, 'NY Fed GDP Nowcast Q1-2017', 'NY Fed GDP Nowcast Q1-2017', 10, 'NY Fed Nowcast', 3, 184, 6),
	(55, 'Empire State Index, current activity', 'Current General Activity, Index, SA', 10, 'Empire State Manufacturing Survey', 7, 184, 1),
	(56, 'Empire State Index, Future Activity', 'Future General Activity, Index, SA', 10, 'Empire State Manufacturing Survey', 7, 184, 1),
	(57, 'NY Fed Business Leaders Business Activity index', 'Diffusion Indexes for Current Conditions, Business Activity', 10, 'Business Leaders Survey', 7, 184, 1),
	(58, 'NY Fed Business Leaders Business Future Activity', 'Diffusion Indexes for Future Conditions, Business Activity', 10, 'Business Leaders Survey', 7, 184, 1)
ON DUPLICATE KEY UPDATE variable_id = variable_id;

INSERT INTO data_indicators
	(provider_id, vendor_key, variable_id)
VALUES
	(1, 'usfcst0139', 53),
	(1, 'usfcst1969', 54),
	(1, 'ussurv1000', 55),
	(1, 'ussurv1010', 56),
	(1, 'ussurv3900', 57),
	(1, 'ussurv3904', 58)
ON DUPLICATE KEY UPDATE vendor_key = vendor_key;


---------------------------------------
-- Federal Reserve Bank of Richmond
INSERT INTO data_sources
	(source_id, source_name, source_description)
VALUES
	(11, 'Richmond Fed', 'Federal Reserve Bank of Richmond')
ON duplicate key update source_id = source_id;

INSERT INTO data_variable_id
    (variable_id, variable_name, variable_description, source_id, dataset, frequency_id, country_id, indicator_type)
VALUES
	(59, 'Richmond Fed Manufacturing Index', 'Current Conditions, Manufacturing Index, SA', 11, 'Fifth District Survey of Manufacturing Activity', 7, 184, 1),
	(60, 'Service Sector Indicator, Revenues, SA', 'Service-Sector Indicator, Revenues, SA Richmond Fed Services Index', 11, 'Fifth District Survey of Service Sector Activity', 7, 184, 1)
ON DUPLICATE KEY UPDATE variable_id = variable_id;

INSERT INTO data_indicators
	(provider_id, vendor_key, variable_id)
VALUES
	(1, 'ussurv1066', 59),
	(1, 'ussurv1306', 60)
ON DUPLICATE KEY UPDATE vendor_key = vendor_key;

------------------------
-- IHS Markit
INSERT INTO data_sources
	(source_id, source_name, source_description)
VALUES
	(12, 'IHS Markit', 'IHS Markit')
ON duplicate key update source_id = source_id;

INSERT INTO data_variable_id
    (variable_id, variable_name, variable_description, source_id, dataset, frequency_id, country_id, indicator_type)
VALUES
	(61, 'Markit PMI Manufacturing Index', 'Markit PMI Manufacturing Index', 12, 'PMI', 7, 184, 1),
	(62, 'Markit PMI Manufacturing Index, SA', 'Markit PMI Manufacturing Index', 12, 'PMI', 7, 184, 1),
	(63, 'Markit PMI Services', 'Business Surveys, Markit, Services, Services PMI Business Activity Index', 12, 'PMI', 7, 184, 1)
ON DUPLICATE KEY UPDATE variable_name = variable_name;

INSERT INTO data_indicators
	(provider_id, vendor_key, variable_id)
VALUES
	(1, 'markit_3y_pmiusmanmepm', 61),
	(1, 'markit_3y_pmiusmanmepmu', 62),
	(1, 'markit_3y_pmiussermeobu', 63)
ON DUPLICATE KEY UPDATE vendor_key = vendor_key;
