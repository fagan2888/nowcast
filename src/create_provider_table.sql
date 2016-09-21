-- Script to create a table for data_providers
-- provider_id | provider_name

CREATE TABLE IF NOT EXISTS data_provider(provider_id serial PRIMARY KEY,
                                      provider_name varchar(25),
                                      UNIQUE provider_ix (provider_name));
                                      
INSERT INTO data_provider(provider_name) VALUES ('MacroBond');      



