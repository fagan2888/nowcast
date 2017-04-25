

SELECT DISTINCT period_date 
FROM data_series_v
WHERE year(period_date) > 1950
AND abs(month(period_date)/3 - round(month(period_date)/3) ) < 1e-8
ORDER BY period_date;

SELECT DISTINCT period_date 
FROM data_series_v
WHERE year(period_date) > 1990
ORDER BY period_date;

SELECT DISTINCT vendor_key FROM data_series_v;

SELECT period_date,
  MAX(IF(vendor_key = 'uscons1146', value, NULL)) AS 'uscons1146'
FROM data_series_v
WHERE year(period_date) > 1990
GROUP BY period_date;


SELECT period_date,
  MAX(IF(vendor_key = 'uscons1156', value, NULL)) AS 'uscons1156'
FROM data_series_v
WHERE year(period_date) > 1990
GROUP BY period_date;

SELECT period_date,
  MAX(IF(vendor_key = 'usfcst0074', value, NULL)) AS 'usfcst0074'
FROM data_series_v
WHERE year(period_date) > 1990
GROUP BY period_date;

SELECT period_date,
  MAX(IF(vendor_key = 'usfcst1745', value, NULL)) AS 'usfcst1745'
FROM data_series_v
WHERE year(period_date) > 1990
GROUP BY period_date;


SELECT period_date,
  MAX(IF(vendor_key = 'usfcst1810', value, NULL)) AS 'usfcst1810'
FROM data_series_v
WHERE year(period_date) > 1990
GROUP BY period_date;

