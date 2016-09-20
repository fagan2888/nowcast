-- Script to create a table for Indicators
-- Indicator_id | vendor_indicator_ident | indicator_info | 

CREATE TABLE IF NOT EXISTS indicators ( indicator_id serial PRIMARY KEY,
                                       provider_id INTEGER REFERENCES data_provider(provider_id), 
                                       vendor_key VARCHAR (25) NOT NULL,
                                       frequency_id INTEGER REFERENCES release_frequencies(frequency_id),
                                       country_id INTEGER REFERENCES master_country(country_id),
                                       indicator_info TEXT);
                                       
DO $$
BEGIN
	IF NOT EXISTS (SELECT 1 from indicators) THEN 
	INSERT INTO indicators (provider_id, vendor_key, frequency_id, country_id, indicator_info) VALUES 
	(1, 'ussurv1055',4,184,'United States, Business Surveys, ISM, Report on Business, Manufacturing, Purchasing Managers Index'),
	(1, 'ussurv1044',4,184,'United States, Business Surveys, ISM, Report on Business, Non-Manufacturing, Purchasing Managers Index'),
	(1, 'ussurv1363',4,184,'United States, Business Surveys, ISM Chicago, Chicago Business Barometer, Business Barometer, SA'),
	(1, 'ussurv1459',4,184,'United States, Consumer Surveys, Conference Board, Consumer Confidence Index, Total, Total, SA'),
	(1, 'ussurv0354',4,184,'United States, Consumer Surveys, University of Michigan, Consumer Sentiment, Consumer Sentiment Index'),
	(1, 'ussurv1102',4,184,'United States, Business Surveys, Federal Reserve Bank of Philadelphia, Business Outlook Survey, Manufacturing, Current General Activity, Diffusion, SA'),
	(1, 'uslama1135',4,184,'United States, Productivity, Costs & Hours Worked, Hours Worked, Average Weekly, Production & Non-Supervisory Employees, Total Private, SA'),
	(1, 'uslama1849',4,184,'United States, Unemployment, CPS, 16 Years & Over, Rate, SA'),
	(1, 'uslama1060',4,184,'United States, Employment, CES, Nonfarm, Payroll, Total, SA'),
	(1, 'ustrad0070',4,184,'United States, Domestic Trade, Retail Trade, Retail Sales, Total, Calendar Adjusted, SA, USD'),
	(1, 'uspric2156',4,184,'United States, Consumer Price Index, All Urban Consumers, U.S. City Average, All Items, SA'),
	(1, 'uscons1156',4,184,'United States, Construction by Status, Construction Started, Residential, New Privately Owned, Total, SA, AR'),
	(1, 'uscons1146',4,184,'United States, Construction by Status, Permits, Residential, National, New Privately Owned, Total, SA, AR'),
	(1, 'usprod1022',4,184,'United States, Industrial Production, Total, SA, Index'),
	(1, 'usprod1501',4,184,'United States, Unfilled Orders, Durable Goods, Total, All, SA, USD'),
	(1, 'usprod1385',4,184,'United States, New Orders, Durable Goods, Total, All, SA, USD'),
	(1, 'usprod0805',4,184,'United States, Manufacturers Inventories, Total, Durable Goods, All, All, Current Prices, SA, USD'),
	(1, 'usprod1071',4,184,'United States, Capacity Utilization, Percent of Capacity, SA'),
	(1, 'bea037_76a067rx_m',4,184,'United States, BEA, Personal Income & Its Disposition, Addenda, Disposable Personal Income: Total, Billions Of Chained (2009) Dollars, SA, AR, USD'),
	(1, 'usnaac0591',4,184,'United States, Expenditure Approach, Personal Consumption Expenditures, Total, Constant Prices, SA, Index'),
	(1, 'usnaac0169',6,184,'United States, Gross Domestic Product, Total, Constant Prices, SA, Chained, AR, USD'),
	(1, 'usfcst0074',4,184,'Anxious Index'),
	(1, 'usfcst1745',4,184,'Median Real GDP Growth rates (SAAR)'),
	(1, 'usfcst1810',4,184,'Mean Real GDP Growth rates (SAAR)');
ELSE
	RAISE NOTICE 'TABLE EXISTS WITH ELEMENTS. ENTER NEW ENTRIES MANUALLY';
END IF;
END $$;  
                                       