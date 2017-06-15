
-- DROP (external) forecast tables
DROP TABLE IF EXISTS fcst_data;
DROP TABLE IF EXISTS fcst_tickers;
DROP TABLE IF EXISTS fcst_sources;
DROP TABLE IF EXISTS fcst_variables;

-- DROP output tables
DROP TABLE IF EXISTS output_forecast_data CASCADE;
DROP TABLE IF EXISTS output_factors CASCADE;
DROP TABLE IF EXISTS output_run_info CASCADE;
DROP TABLE IF EXISTS output_run_table CASCADE;

-- DROP Model Tables
DROP TABLE IF EXISTS model_indicators CASCADE;
DROP TABLE IF EXISTS model_controls CASCADE;
DROP TABLE IF EXISTS model_references CASCADE;
DROP TABLE IF EXISTS model_types CASCADE;

-- DROP data tables
DROP TABLE IF EXISTS data_values CASCADE;
DROP TABLE IF EXISTS data_indicators CASCADE;
DROP TABLE IF EXISTS data_variable_id CASCADE;
DROP TABLE IF EXISTS data_provider CASCADe;
DROP TABLE IF EXISTS data_sources CASCADe;

-- DROP meta
DROP TABLE IF EXISTS meta_control_variables CASCADE;
DROP TABLE IF EXISTS meta_data_transformations CASCADE;
DROP TABLE IF EXISTS meta_forecast_types CASCADE;
DROP TABLE IF EXISTS meta_indicator_types CASCADE;
DROP TABLE IF EXISTS meta_master_country CASCADE;
DROP TABLE IF EXISTS meta_presentation_units CASCADE;
DROP TABLE IF EXISTS meta_release_frequencies CASCADE;
DROP TABLE IF EXISTS meta_run_type CASCADE;
