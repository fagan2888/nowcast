-- DROP output tables

-- DROP Model Tables

-- DROP data tables
DROP TABLE IF EXISTS data_values CASCADE;
DROP TABLE IF EXISTS data_indicators CASCADE;
DROP TABLE IF EXISTS data_variable_id;
DROP TABLE IF EXISTS data_provider;
DROP TABLE IF EXISTS data_sources;

-- DROP meta
DROP TABLE IF EXISTS meta_control_variables;
DROP TABLE IF EXISTS meta_data_transformations;
DROP TABLE IF EXISTS meta_forecast_types;
DROP TABLE IF EXISTS meta_indicator_types;
DROP TABLE IF EXISTS meta_master_country;
DROP TABLE IF EXISTS meta_presentation_units;
DROP TABLE IF EXISTS meta_release_frequencies;
DROP TABLE IF EXISTS meta_run_type;
