-- Drop previous Tables
source drop_tables.sql;

-- Recreate all tables
source create_meta_tables.sql;
source create_data_tables.sql;
source create_model_tables.sql;
source create_output_tables.sql;
