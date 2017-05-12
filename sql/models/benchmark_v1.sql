
-- Benchmark Model 1: As of 11. May 2017
-- Now-Casting Model MSP

-- Model ID
INSERT INTO model_references (model_name, target_country_id, target_indicator_id, model_type, created_by)
VALUES
    ('ms_dfm_nowcast_v1', 184, 20, 1, 'lsimonsen')
ON duplicate key update model_id = model_id, model_name = model_name;

-- Model Hyper Parameters
INSERT INTO model_controls (model_id, control_id, control_values)
VALUES
    (1, 1, 1), -- plag
    (1, 2, 12), -- hor
    (1, 3, 1), -- qlag
    (1, 4, 1), -- Nx
    (1, 6, 2), -- high (std)
    (1, 7, 2) -- low (std)
ON DUPLICATE KEY UPDATE model_id = model_id, control_id = control_id;


-- Model Variables
INSERT INTO
    model_indicators (model_id, indicator_id, transformation_code, presentation_code)
VALUES
    ( 1,  5, 4, 0), -- Consumer Sentiment Index (University of Michigan)
    ( 1,  2, 0, 0), -- PMI Non-Manufacturing (ISM)
    ( 1,  1, 0, 0), -- PMI Manufacturing (ISM)
    ( 1,  6, 0, 0), -- Businees outlook Survey Manufacturing (Philidelphia Fed)
    ( 1,  3, 0, 0), -- Chicago Business Surveys Barometer (ISM)
    ( 1,  4, 4, 0), -- Consumer confidence Index (Conference Board)
    ( 1, 10, 5, 5), -- Retail Sales (?)
    ( 1, 18, 5, 5), -- Capacity Utilisation (?)
    ( 1, 14, 5, 5), -- Industrial Production
    ( 1, 12, 5, 5), -- Construction Started Residential
    ( 1, 13, 5, 5), -- Construction Permits
    ( 1, 15, 5, 5), -- Unfiled Orders Durable Goods
    ( 1, 16, 5, 5), -- New Orders Durable Goods
    ( 1, 17, 5, 5), -- Manufacturing Inventories
    ( 1,  7, 5, 5), -- Hours Worked Average Weekly
    ( 1,  8, 5, 0), -- Unemployment
    ( 1,  9, 5, 0), -- Employment non farm payroll
    ( 1, 11, 5, 5), -- Consumer Price Index
    ( 1, 19, 5, 5), -- Personal consumption Expenditures
    ( 1, 20, 6, 6) -- Real Gross Domestic Product
	ON DUPLICATE KEY UPDATE model_id = model_id, indicator_id = indicator_id;
