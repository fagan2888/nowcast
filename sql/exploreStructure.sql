SELECT * FROM etf_blp_tickers LIMIT 10;

SELECT count(tab.ticker)
FROM 
(
SELECT DISTINCT tb1.ticker AS ticker
FROM
	etf_blp_meta AS tb1
LEFT JOIN
	etf_blp_data AS tb2
ON	tb1.ticker = tb2.ticker
WHERE tb2.ticker IS NOT NULL
) AS tab
;