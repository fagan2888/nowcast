SELECT vendor_key, max(release_date), max(next_release)
FROM data_series_v 
wHERE vintage=1
GROUP BY vendor_key;

