

CREATE VIEW data_series_v AS SELECT t4.iso_alpha_2, t2.vendor_key, t2.indicator_info, t1.value, t1.period_date, t1.release_date, t1.next_release, t1.latest, t1.vintage, t3.frequency  FROM data t1 LEFT JOIN (indicators t2) ON  (t1.indicator_id = t2.indicator_id) LEFT JOIN(release_frequencies t3) ON (t3.frequency_id = t1.frequency_id) LEFT JOIN (master_country t4) USING(country_id)
