-- Script to create a table for Indicators
-- Indicator_id | vendor_indicator_ident | indicator_info | 

CREATE TABLE IF NOT EXISTS indicators ( indicator_id serial PRIMARY KEY,
                                       provider_id INTEGER NOT NULL, 
                                       vendor_key VARCHAR (25) NOT NULL,
                                       country_id INTEGER NOT NULL,
                                       indicator_info TEXT);
                                       
                                       