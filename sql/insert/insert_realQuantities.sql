
-- Model: Hard Data
INSERT INTO model_references (model_name, target_country_id, target_variable_id, model_type, created_by)
VALUES
    ('ms_dfm_realquantities', 184, 39, 1, 'lsimonsen')
ON duplicate key update model_id = model_id, model_name = model_name;

-- Model Hyper Parameters
INSERT INTO model_controls (model_id, control_id, control_values)
VALUES
    (6, 1, 1), -- plag
    (6, 2, 12), -- hor
    (6, 3, 1), -- qlag
    (6, 4, 1), -- Nx
    (6, 6, 2), -- high (std)
    (6, 7, 2) -- low (std)
ON DUPLICATE KEY UPDATE model_id = model_id, control_id = control_id;

INSERT INTO
    model_indicators (model_id, indicator_id, transformation_code, presentation_code)
VALUES
    -- Consumption (PCE): MoM
    ( 6,  23, 5, 5), -- PCE, Non-Durable, Chained, SA
    ( 6,  25, 5, 5), -- PCE, Durable, Chained, SA
    ( 6,  26, 5, 5), -- PCE, Services, Chained, SA
    ( 6,  27, 5, 5), -- PCE, Total, Chained, SA
    -- Private Disposable Income: MoM
    ( 6,  36, 5, 5), -- PCE, Total, Chained, SA
    -- Trade: Imports and Exports, MoM
    ( 2,  5, 4, 0), -- Consumer Sentiment Index (University of Michigan)
    ( 2,  6, 0, 0), -- Businees outlook Survey Manufacturing (Philidelphia Fed)
    (2, 55, 0, 0),
    (2, 56, 0, 0),
    (2, 57, 0, 0),
    (2, 58, 0, 0),
    (2, 59, 0, 0),
    (2, 60, 0, 0),
    (2, 61, 0, 0),
    (2, 62, 0, 0),
    (2, 63, 0, 0),
    -- Industrial Production: Constant Prices
    -- Quarterly Variables
    -- PCE: usnaac1137
    -- Investment, Total: usnaac1143
    -- Investment, Change in Inventories: usnaac1148
    -- Investment, Fixed Investment: usnaac1143
    -- Net Export, Total: usnaac1149
    -- Government, Total: usnaac1161 - OBS: Monthly nominal receipt and outlay data from US government....
    -- Residual: usnaac1161
    (6, 39, 6, 6) -- Real Gross Domestic Product
ON DUPLICATE KEY UPDATE model_id = model_id, indicator_id = indicator_id, transformation_code=transformation_code, presentation_code=presentation_code;
