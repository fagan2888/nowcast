-- Model: Soft indicators
INSERT INTO model_references (model_name, target_country_id, target_variable_id, model_type, created_by)
VALUES
    ('ms_dfm_softdata', 184, 39, 1, 'lsimonsen')
ON duplicate key update model_id = model_id, model_name = model_name;

-- Model Hyper Parameters
INSERT INTO model_controls (model_id, control_id, control_values)
VALUES
    (5, 1, 1), -- plag
    (5, 2, 12), -- hor
    (5, 3, 1), -- qlag
    (5, 4, 1), -- Nx
    (5, 6, 2), -- high (std)
    (5, 7, 2) -- low (std)
ON DUPLICATE KEY UPDATE model_id = model_id, control_id = control_id;

INSERT INTO
    model_indicators (model_id, indicator_id, transformation_code, presentation_code)
VALUES
    (5,  1, 0, 0), -- PMI Manufacturing (ISM)
    (5,  2, 0, 0), -- PMI Non-Manufacturing (ISM)
    (5,  3, 0, 0), -- Chicago Business Surveys Barometer (ISM)
    (5,  4, 4, 0), -- Consumer confidence Index (Conference Board)
    (5,  5, 4, 0), -- Consumer Sentiment Index (University of Michigan)
    (5,  6, 0, 0), -- Businees outlook Survey Manufacturing (Philidelphia Fed)
    (5, 55, 0, 0),
    (5, 56, 0, 0),
    (5, 57, 0, 0),
    (5, 58, 0, 0),
    (5, 59, 0, 0),
    (5, 60, 0, 0),
    (5, 61, 0, 0),
    (5, 62, 0, 0),
    (5, 63, 0, 0),
    (5, 39, 6, 6) -- Real Gross Domestic Product
ON DUPLICATE KEY UPDATE model_id = model_id, indicator_id = indicator_id, transformation_code=transformation_code, presentation_code=presentation_code;
