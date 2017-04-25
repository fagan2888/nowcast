SELECT
	data.countryCode,
	meta.ISO_Code,
	meta.Country,
	meta.Region_geography,
	meta.Classification,
	data.period_date,
	data.DebtEquity,
	data.AssetLiability,
	data.value
FROM data_macrobond data
LEFT JOIN metadata_macrobond meta 
ON data.countryCode = meta.IMF_Code
WHERE data.freq = "quarter";
