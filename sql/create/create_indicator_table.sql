-- Script to create a table for Indicators
-- Indicator_id | vendor_key| frequency_id |  country_id | indicator_info| type of data

CREATE TABLE IF NOT EXISTS indicators ( indicator_id 			INTEGER NOT NULL AUTO_INCREMENT,
										provider_id 			INTEGER NOT NULL,
										vendor_key 				VARCHAR (25) NOT NULL,
										frequency_id 			INTEGER NOT NULL,
										country_id 				INTEGER NOT NULL,
										indicator_short_info 	TEXT NOT NULL,
										indicator_info 			TEXT,
                                        indicator_type			INTEGER NOT NULL,
                                        indicator_presentation	INTEGER NOT NULL,
										PRIMARY KEY (indicator_id),
										CONSTRAINT indicators_ibfk_1 FOREIGN KEY (provider_id)
											REFERENCES data_provider (provider_id) ON DELETE CASCADE,
										CONSTRAINT indicators_ibfk_2 FOREIGN KEY (frequency_id)
											REFERENCES release_frequencies (frequency_id),
										CONSTRAINT indicators_ibfk_3 FOREIGN KEY (country_id)
											REFERENCES master_country(country_id) ON DELETE CASCADE,
										CONSTRAINT indicators_ibfk_4 FOREIGN KEY(indicator_type)
											REFERENCES indicator_types(indicator_type_id),
										CONSTRAINT indicators_ibfk_5 FOREIGN KEY(indicator_presentation)
											REFERENCES presentation_units(unit_id),
										UNIQUE KEY vendor_ix (vendor_key)
                                        ) ENGINE=INNODB;


select * from indicators;

INSERT INTO indicators (provider_id, vendor_key, frequency_id, country_id, indicator_short_info, indicator_info, indicator_type, indicator_presentation) VALUES
	(1, 'ussurv1055',  7, 184, 'Manufacturing PMI', 'United States, Business Surveys, ISM, Report on Business, Manufacturing, Purchasing Managers Index', 1, 1),
	(1, 'ussurv1044',  7, 184, 'Non Manufacturing PMI','United States, Business Surveys, ISM, Report on Business, Non-Manufacturing, Purchasing Managers Index', 1, 1),
	(1, 'ussurv1363',  7, 184, 'Business Surveys ISM Chicago','United States, Business Surveys, ISM Chicago, Chicago Business Barometer, Business Barometer, SA', 1, 5),
	(1, 'ussurv1459',  7, 184, 'Consumer Sentiment Index','United States, Consumer Surveys, Conference Board, Consumer Confidence Index, Total, Total, SA', 1, 5),
	(1, 'ussurv0354',  7, 184, 'Consumer Sentiment Index','United States, Consumer Surveys, University of Michigan, Consumer Sentiment, Consumer Sentiment Index', 1, 1),
	(1, 'ussurv1102',  7, 184, 'Business Outlook Survey Manufacturing','United States, Business Surveys, Federal Reserve Bank of Philadelphia, Business Outlook Survey, Manufacturing, Current General Activity, Diffusion, SA', 1, 1),
	(1, 'uslama1135',  7, 184, 'Hours Worked Average Weekly','United States, Productivity, Costs & Hours Worked, Hours Worked, Average Weekly, Production & Non-Supervisory Employees, Total Private, SA', 2, 2),
	(1, 'uslama1849',  7, 184, 'Unemployment','United States, Unemployment, CPS, 16 Years & Over, Rate, SA', 2, 6),
	(1, 'uslama1060',  7, 184, 'Employment Non Farm Payroll','United States, Employment, CES, Nonfarm, Payroll, Total, SA', 2, 2),
	(1, 'ustrad0070',  7, 184, 'Retail Sales','United States, Domestic Trade, Retail Trade, Retail Sales, Total, Calendar Adjusted, SA, USD', 3, 2),
	(1, 'uspric2156',  7, 184, 'Consumer Price Index','United States, Consumer Price Index, All Urban Consumers, U.S. City Average, All Items, SA', 4, 3),
	(1, 'uscons1156',  7, 184, 'Construction Started Residential','United States, Construction by Status, Construction Started, Residential, New Privately Owned, Total, SA, AR', 3, 2),
	(1, 'uscons1146',  7, 184, 'Construction by Status','United States, Construction by Status, Permits, Residential, National, New Privately Owned, Total, SA, AR', 3, 2),
	(1, 'usprod1022',  7, 184, 'Industrial Production','United States, Industrial Production, Total, SA, Index', 3, 2),
	(1, 'usprod1501',  7, 184, 'Unfilled Orders Durable Goods','United States, Unfilled Orders, Durable Goods, Total, All, SA, USD', 3, 2),
	(1, 'usprod1385',  7, 184, 'New Orders Durable Goods','United States, New Orders, Durable Goods, Total, All, SA, USD', 3, 2),
	(1, 'usprod0805',  7, 184, 'Manufacturing Inventories','United States, Manufacturers Inventories, Total, Durable Goods, All, All, Current Prices, SA, USD', 3, 2),
	(1, 'usprod1071',  7, 184, 'Capacity Utilisation','United States, Capacity Utilization, Percent of Capacity, SA', 3, 6),
	(1, 'usnaac0591',  7, 184, 'Personal Consumption Expenditures','United States, Expenditure Approach, Personal Consumption Expenditures, Total, Constant Prices, SA, Index', 4, 2),
	(1, 'usnaac0169', 10, 184, 'Real Gross Domestic Product','United States, Gross Domestic Product, Total, Constant Prices, SA, Chained, AR, USD', 5, 4)
ON duplicate key update indicator_id = indicator_id, vendor_key = vendor_key;


INSERT INTO indicators (provider_id, vendor_key, frequency_id, country_id, indicator_short_info, indicator_info, indicator_type, indicator_presentation) VALUES
	(1, 'usfcst0074',  7, 184,'Anxious Index','Anxious Index', 6, 5),
	(1, 'usfcst1745',  7, 184, 'Median Real GDP Growth rates','Real GDP Philidelphia Fed Survey of Professional Forecasters (median)', 6, 5),
	(1, 'usfcst1810',  7, 184, 'Mean Real GDP Growth Rates', 'Real GDP Philidelphia Fed Survey of Professional Forecasters (mean)', 6, 5),
	(1, 'usfcst2473',  7, 184, 'Atlanta Fed GDPnow 2017-Q2', 'Atlanta Fed GDPnow 2017-Q2 Mean Real GDP Growth rates (SAAR)', 6, 5),
	(1, 'usfcst1847',  7, 184, 'Atlanta Fed GDPnow 2017-Q1', 'Atlanta Fed GDPnow 2017-Q1 Mean Real GDP Growth rates (SAAR)', 6, 5),
	(1, 'usfcst1884',  7, 184, 'Atlanta Fed GDPnow 2016-Q4', 'Atlanta Fed GDPnow 2016-Q4 Mean Real GDP Growth rates (SAAR)', 6, 5),
	(1, 'usfcst1841',  7, 184, 'Atlanta Fed GDPnow 2016-Q3', 'Atlanta Fed GDPnow 2016-Q3 Mean Real GDP Growth rates (SAAR)', 6, 5),
	(1, 'usfcst1469',  7, 184, 'Atlanta Fed GDPnow 2016-Q2', 'Atlanta Fed GDPnow 2016-Q2 Mean Real GDP Growth rates (SAAR)', 6, 5),
	(1, 'usfcst0819',  7, 184, 'Atlanta Fed GDPnow 2016-Q1', 'Atlanta Fed GDPnow 2016-Q1 Mean Real GDP Growth rates (SAAR)', 6, 5),
	(1, 'usfcst0803',  7, 184, 'Atlanta Fed GDPnow 2015-Q4', 'Atlanta Fed GDPnow 2015-Q4 Mean Real GDP Growth rates (SAAR)', 6, 5),
    (1, 'usfcst0139', 7, 184, 'NY Fed GDP Nowcast Q2-2017', 'NY Fed GDP Nowcast Q2-2017', 6, 5),
	(1, 'usfcst1969', 7, 184, 'NY Fed GDP Nowcast Q1-2017', 'NY Fed GDP Nowcast Q1-2017', 6, 5)
ON duplicate key update indicator_id = indicator_id, vendor_key = vendor_key;

INSERT INTO indicators (provider_id, vendor_key, frequency_id, country_id, indicator_info, indicator_short_info, indicator_type, indicator_presentation) VALUES
	(1, 'ussurv1000', 7, 184, 'Business Surveys, Federal Reserve Bank of New York, Empire State Manufacturing Survey, Current General Activity, Index, SA', 'Empire State Index, current activity',1,1),
	(1, 'ussurv1010', 7, 184, 'Business Surveys, Federal Reserve Bank of New York, Empire State Manufacturing Survey, Future General Activity, Index, SA', 'Empire State Index, Future Activity',1,1),
	(1, 'ussurv3900', 7, 184,  'Diffusion Indexes for Current Conditions, Business Activity', 'NY Fed Business Leaders Business Activity index',1,1),
	(1, 'ussurv3904', 7, 184, 'Diffusion Indexes for Future Conditions, Business Activity', 'NY Fed Business Leaders Business Future Activity',1,1),
	(1, 'ussurv1102', 7, 184, 'United States, Business Surveys, Federal Reserve Bank of Philidelphia, Business Outlook Survey, Manufacturing, Current, General Activity, Diffusion, SA', 'Manufacturing Businesss Outlook Survey, General Acitvity',1,1),
	(1, 'markit_3y_pmiusmanmepm', 7, 184, 'Markit PMI Manufacturing Index',	'Markit PMI Manufacturing Index',1,1),
	(1, 'ussurv1066', 7, 184, 'United States, Business Surveys, Federal Reserve Bank of Richmond, Fifth District Survey of Manufacturing Activity, Current Conditions, Manufacturing Index, SA', 'Richmond Fed Manufacturing Index',1,1),
	(1, 'ussurv1306', 7, 184, 'Federal Reserve Bank of Richmond, Fifth District Survey of Service Sector Activity, Service-Sector Indicator, Revenues, SA	Richmond Fed Services Index', 'Kansas City Fed Manufacturing Index	Kansas City Fed Manufacturing Index',1,1),
	(1, 'markit_3y_pmiussermeobu', 7, 184,	'United States, Business Surveys, Markit, Services, Services PMI Business Activity Index', 'Markit PMI Services', 1,1),
	(1, 'usnaac3029', 7, 184, 'Income Approach, Total, Disposable Personal Income, Total, Constant Prices, SA, Chained, AR, USD', 'Disposable Personal Income (real)', 4,3),
	(1, 'usnaac33303', 7, 184, 'United States, Expenditure Approach, Personal Consumption Expenditures, Durable Goods, Total, SA, AR, USD', 'PCE Durable Goods (nominal)', 4,3),
	(1, 'usnaac33308', 7, 184, 'PCE Nondurable Goods', 'PCE Nondurable Goods (nominal)', 4,3),
	(1, 'usnaac33313', 7, 184, 'United States, Expenditure Approach, Personal Consumption Expenditres, Services, Total,  SA, AR, USD', 'PCE Services, nominal', 4,3),
	(1, 'usnaac0699', 7, 184, 'United States, Expenditure Approach, Personal Consumption Expenditres, Durable, Real, Total, Chained, SA, AR, USD', 'PCE Durable (real)', 4,3),
	(1, 'usnaac0844', 7, 184, 'United States, Expenditure Approach, Personal Consumption Expenditres, Services, Real, Total, Chained, SA, AR, USD', 'PCE Services, real', 4,3),
	(1, 'usnaac0766', 7, 184, 'United States, Expenditure Approach, Personal Consumption Expenditres, Non-Durable, Real, Total, Chained, SA, AR, USD', 'PCE Non-Durable (real)', 4,3),
	(1, 'uscons2380', 7, 184, 'Construction Finances, Private, Residential, Total, SA, AR, USCB, Spending', 'Residential Construction Spending (nominal)', 4,3),
	(1, 'ustrad1967', 7, 184, 'United States, Foreign Trade,  Bureau of Economic Analysis, Export of Goods & Services, Total, Current Prices, SA, AR, USD', 'Goods Exports',3,3),
	(1, 'ustrad1990', 7, 184, 'United States, Foreign Trade,  Bureau of Economic Analysis, Import of Goods & Services, Total, Current Prices, SA, AR, USD', 'Goods Imports',3,3),
	(1, 'ustrad0801', 7, 184, 'Domestic Trade, Retail Trade, Retail & Food Service Sale, Constant Prices, SA, Chained USD', 'Real Retail Sales and Food Service',3,3),
	(1, 'ustrad0350', 7, 184, 'United States, Domestic trade, Manufacturing & Trade, Sales, Total Business, Constant Prices,  SA, Chained, USD', 'Manufacturing Sales (real)',3,3),
	(1, 'ustrad0401', 7, 184, 'Inventories, Calendar Adjusted, SA, USD', 'Inventories',3,3),
	(1, 'ustrad1020', 7, 184, 'Sales, Calendar Adjusted, SA, USD', 'Whole Sales',3,3),
	(1, 'uslama4486', 7, 184, 'United States, Socio-Demographic Labour Force Statistics, Civilian Labour Force Participation Rate, Women & Men, 16 Years & Over, SA', 'Employment Participation Rate',2,1),
	(1, 'uspric0005', 7, 184, 'United States, Personal Consumption Expenditures, Services Price Index, SA', 'PCE Price Index',4,3)
ON duplicate key update indicator_id = indicator_id, vendor_key = vendor_key;
