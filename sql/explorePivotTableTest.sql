SELECT * FROM data_series_v LIMIT 10;

SELECT period_date,
  MAX(IF(vendor_key = 'uscons1146', value, NULL)) AS 'uscons1146'
FROM data_series_v
GROUP BY period_date;




SET @sql = NULL;
SET @@group_concat_max_len = 5000;

SELECT
  GROUP_CONCAT(DISTINCT
    CONCAT(
     'MAX(IF(vendor_key = ''',
      vendor_key,
      ''', value, NULL)) AS ',
      vendor_key
    )
  ) INTO @sql
FROM data_series_v;

SET @sql = CONCAT('SELECT period_date, ', @sql, ' FROM data_series_v GROUP BY period_date,');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;