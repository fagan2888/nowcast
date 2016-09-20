-- insert into data (indicator_id,value, start_date, end_date, release_date, next_date, latest, vintage ) 
-- SELECT ind_table.indicator_id,1.12E+13, from indicators ind_table where ind_table.vendor_key = 'usnaac0169'

CREATE TABLE IF NOT EXISTS release_frequencies(freq_id SERIAL PRIMARY KEY, frequency INTERVAL NOT NULL, frequency_text TEXT NOT NULL);

DO $$
BEGIN
	IF NOT EXISTS (SELECT 1 from release_frequencies) THEN 
	INSERT INTO release_frequencies (frequency, frequency_text) VALUES 
						('1 day', 'daily'),
                        ('1 week', 'weekly'),
                        ('2 weeks', 'bi-weekly'),
                        ('1 month', 'monthly'),
                        ('2 months', 'bi-monthly'),
                        ('3 months', 'quarterly'),
                        ('6 months', 'bi-annually'),
                        ('1 year', 'yearly');
ELSE
	RAISE NOTICE 'TABLE EXISTS WITH ELEMENTS. ENTER NEW ENTRIES MANUALLY';
END IF;
END $$;