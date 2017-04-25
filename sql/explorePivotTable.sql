


SET @sql = NULL;gdp_fcst_over_all_runs_min_col_vgdp_fcst_over_all_runs_min_col_v
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

