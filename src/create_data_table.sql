-- Script to create the data table

CREATE TABLE IF NOT EXISTS data ( indicator_id BIGINT UNSIGNED REFERENCES indicators(indicator_id),
								  value REAL NOT NULL,
								  start_date DATE NOT NULL,
								  end_date DATE NOT NULL,
								  frequency_id BIGINT UNSIGNED REFERENCES release_frequencies(frequency_id),
								  release_date DATE NOT NULL,
								  next_release DATE,
								  latest BOOLEAN NOT NULL,
								  vintage INTEGER NOT NULL);

