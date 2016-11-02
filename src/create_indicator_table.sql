-- Script to create a table for Indicators
-- Indicator_id | vendor_key| frequency_id |  country_id | indicator_info| type of data 

CREATE TABLE IF NOT EXISTS indicators ( indicator_id 		INTEGER NOT NULL AUTO_INCREMENT, 
										provider_id 		INTEGER NOT NULL, 
										vendor_key 			VARCHAR (25) NOT NULL,
										frequency_id 		INTEGER NOT NULL,
										country_id 			INTEGER NOT NULL,
										indicator_short_info TEXT NOT NULL, 
										indicator_info 		TEXT, 
                                        indicator_type		INTEGER NOT NULL,
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
INSERT INTO indicators (provider_id, vendor_key, frequency_id, country_id, indicator_info, indicator_type, indicator_presentation) VALUES 
	(1, 'ussurv1055',7,184,'Manufacturing PMI','United States, Business Surveys, ISM, Report on Business, Manufacturing, Purchasing Managers Index', 1, 1),
	(1, 'ussurv1044',7,184,'Non Manufacturing PMI','United States, Business Surveys, ISM, Report on Business, Non-Manufacturing, Purchasing Managers Index', 1, 1),
	(1, 'ussurv1363',7,184,'Business Surveys ISM Chicago','United States, Business Surveys, ISM Chicago, Chicago Business Barometer, Business Barometer, SA', 1, 5),
	(1, 'ussurv1459',7,184,'Consumer Sentiment Index','United States, Consumer Surveys, Conference Board, Consumer Confidence Index, Total, Total, SA', 1, 5),
	(1, 'ussurv0354',7,184,'Consumer Sentiment Index','United States, Consumer Surveys, University of Michigan, Consumer Sentiment, Consumer Sentiment Index', 1, 1),
	(1, 'ussurv1102',7,184,'Business Outlook Survey Manufacturing','United States, Business Surveys, Federal Reserve Bank of Philadelphia, Business Outlook Survey, Manufacturing, Current General Activity, Diffusion, SA', 1, 1),
	(1, 'uslama1135',7,184,'Hours Worked Average Weekly','United States, Productivity, Costs & Hours Worked, Hours Worked, Average Weekly, Production & Non-Supervisory Employees, Total Private, SA', 2, 2),
	(1, 'uslama1849',7,184,'Unemployment','United States, Unemployment, CPS, 16 Years & Over, Rate, SA', 2, 6),
	(1, 'uslama1060',7,184,'Employment Non Farm Payroll','United States, Employment, CES, Nonfarm, Payroll, Total, SA', 2, 2),
	(1, 'ustrad0070',7,184,'Retail Sales','United States, Domestic Trade, Retail Trade, Retail Sales, Total, Calendar Adjusted, SA, USD', 3, 2),
	(1, 'uspric2156',7,184,'Consumption And Income','United States, Consumer Price Index, All Urban Consumers, U.S. City Average, All Items, SA', 4, 3),
	(1, 'uscons1156',7,184,'Construction Started Residential','United States, Construction by Status, Construction Started, Residential, New Privately Owned, Total, SA, AR', 3, 2),
	(1, 'uscons1146',7,184,'Construction by Status','United States, Construction by Status, Permits, Residential, National, New Privately Owned, Total, SA, AR', 3, 2),
	(1, 'usprod1022',7,184,'Production And Trade','United States, Industrial Production, Total, SA, Index', 3, 2),
	(1, 'usprod1501',7,184,'Unfilled Orders Durable Goods','United States, Unfilled Orders, Durable Goods, Total, All, SA, USD', 3, 2),
	(1, 'usprod1385',7,184,'New Orders Durable Goods','United States, New Orders, Durable Goods, Total, All, SA, USD', 3, 2),
	(1, 'usprod0805',7,184,'Manufacturing Inventories','United States, Manufacturers Inventories, Total, Durable Goods, All, All, Current Prices, SA, USD', 3, 2),
	(1, 'usprod1071',7,184,'Capacity Utilisation','United States, Capacity Utilization, Percent of Capacity, SA', 3, 6),
	(1, 'usnaac0591',7,184,'Personal Consumption Expenditures','United States, Expenditure Approach, Personal Consumption Expenditures, Total, Constant Prices, SA, Index', 4, 2),
	(1, 'usnaac0169',10,184,'Real Gross Domestic Product','United States, Gross Domestic Product, Total, Constant Prices, SA, Chained, AR, USD', 5, 4),
	(1, 'usfcst0074',7,184,'Anxious Index','Anxious Index', 6, 5),
	(1, 'usfcst1745',7,184,'Median Real GDP Growth rates','Median Real GDP Growth rates (SAAR)', 6, 5),
	(1, 'usfcst1810',7,184,'Mean Real GDP Growth Rates','Mean Real GDP Growth rates (SAAR)', 6, 5) ON duplicate key update indicator_id = indicator_id, vendor_key = vendor_key;
    
    
    

