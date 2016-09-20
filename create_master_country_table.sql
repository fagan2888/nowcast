-- Database: postgres
-- Create table for all country  

CREATE TABLE IF NOT EXISTS master_country ( country_id serial PRIMARY KEY,
                             country_name varchar (50) NOT NULL,
                             iso_alpha_2 varchar(2) NOT NULL,
                             iso_alpha_3 varchar(3) NOT NULL,
                             iso_number int NOT NULL ) ;

INSERT INTO master_country (country_name, iso_alpha_2, iso_alpha_3, iso_number) VALUES ('Afghanistan', 'AF', 'AFG', 4)