#!/bin/usr/python3
import numpy as np
import pandas as pd
import datetime
import mysql.connector
import sys
import logging
from math import log
import sys
import configparser

## Own Modules
import logging
from msp_Logging import mspLog
if __name__ == "__main__":
    mspLog(name="msDatabase")


class msDbInterface(object):
    def __init__(self, user, password, host, db_name):
        self.user = user
        self.password = password
        self.db_name = db_name
        self.host = host
        self.cnx = mysql.connector.connect(user = self.user, password = self.password, host = self.host , database = self.db_name)
        self.cnx.autocommit = True
        logging.info('Opening connection to database: ' + self.db_name + ' on server ' + self.host)
        self.cursor = self.cnx.cursor(buffered = True)

    def connect(self):
        try:
            if not self.cnx.is_connected():
                self.cnx = mysql.connector.connect(user = self.user, password = self.password, host = self.host , database = self.db_name)
                self.cnx.autocommit = True
                self.cursor = self.cnx.cursor(buffered = True)
                logging.info('Connection not opened on init. Opening connection to database: {0} on server {1}'.format(self.db_name, self.host))
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.error(err)
                raise
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.error(err)
                raise
            else:
                logging.error(err)
                raise error.with_traceback(sys.exc_info()[2])

    def getConn(self):
        return self.cnx

    def run_query(self, query:str, arguments:list=None):
        try:
            self.cursor.execute(query, arguments)
            results = self.cursor.fetchall()
            return pd.DataFrame(results, columns=[i[0] for i in self.cursor.description])

        except Exception as e:
            raise e

    def close(self):
        if self.cnx.is_connected():
            logging.info('Closing connection to database: ' + self.db_name + 'on server' + self.host)
            self.cnx.close()

    def __del__(self):
        if self.cnx.is_connected():
            #logging.info('Closing connection to database: ' + self.db_name + 'on server' + self.host)
            self.cnx.close()


class msMBDbInterface(msDbInterface):
    def __init__(self, user, password, host, db_name):
        msDbInterface.__init__(self, user, password, host, db_name)
        self.user = user
        self.password = password
        self.db_name = db_name
        self.host = host
        logging.info('Initializing cursor....')
        self.close()
        self.connect()
        self.cursor = self.cnx.cursor(buffered = True)

    #def __del__(self):
    #    logging.info('closing cursor.....')
    #    self.cursor.close()

    def indicatorResultChange(self, indicator, num_prev_results):
       try:
           query = 'SELECT run_id FROM output_run_table ORDER BY timestamp desc LIMIT %s'
           self.cursor.execute(query, [num_prev_results,])
           run_ids = pd.DataFrame(self.cursor.fetchall(), columns = ['run_id'])
           min_id = run_ids['run_id'].min()
           query = '''SELECT t1.period_date, t1.mean_forecast, t2.vendor_key, t2.indicator_short_info, t3.forecast_type, t1.run_id, t6.presentation_unit
                FROM output_forecast_data AS t1 LEFT JOIN (data_indicators AS t2) ON (t2.indicator_id = t1.indicator_id)
                LEFT JOIN (meta_forecast_types AS t3) ON (t3.forecast_type_id = t1.forecast_type_id)
                LEFT JOIN (meta_presentation_units AS t6) ON (t2.indicator_presentation = t6.unit_id)
                where t1.run_id >= %s and t2.vendor_key = %s ORDER BY period_date asc;'''
           self.cursor.execute(query, [str(min_id), indicator,])
           results = pd.DataFrame(self.cursor.fetchall(), columns = ['Period Date', 'mean_forecast', 'vendor_key', 'indicator_short_info', 'forecast_type', 'Run Number', 'presentation_unit'])
           table = pd.pivot_table(results,values='mean_forecast', index='Period Date', columns = ['Run Number'])
           col_name = 'Change(r' + str(run_ids.iloc[0,:].values[0]) + ',r' + str(run_ids.iloc[1,:].values[0]) +')'
           #table[col_name] = 100 * (table.iloc[:, -1].values - table.iloc[:, -2].values) / table.iloc[:, -2].values
           table[col_name] = table.iloc[:, -1].values - table.iloc[:, -2].values
           return table
       except:
           print ("Error retrieving change in indicator updatese:", sys.exc_info()[0])
           raise

    def next_release_date(self):
        logging.info("Retrieving next release date")
        query = '''SELECT IF(convert_tz(min(next_release), 'UTC', 'Europe/London') IS NULL, NOW(), convert_tz(min(next_release), 'UTC', 'Europe/London')) AS next_release
        FROM (select indicator_id,
        IF(min(next_release) = '1900-01-01', STR_TO_DATE('3000-01-01 00:00', '%Y-%m-%d %H:%i'), max(next_release)) as
        next_release FROM data_values GROUP BY indicator_id) AS release_times WHERE next_release > '1900-01-01 00:00:00';'''
        self.cursor.execute(query)
        time = self.cursor.fetchone()
        return time

    def download_ts_data(self):
        try:
            query = '''SELECT t2.vendor_key, t2.indicator_short_info, t1.period_date, t1.value,
                    t1.latest,t2.indicator_presentation, t3.presentation_unit, t4.frequency FROM data_values AS t1
                    JOIN (indicators t2) ON  (t1.indicator_id = t2.indicator_id) JOIN (meta_presentation_units AS t3)
                    ON (t2.indicator_presentation = t3.unit_id) JOIN (release_frequencies t4) ON
                    (t2.frequency_id = t4.frequency_id)  WHERE t1.latest = true and t1.period_date >= (NOW()
                    - INTERVAL 10 YEAR);'''
            self.cursor.execute(query)
            all_latest_data = self.cursor.fetchall()

            return all_latest_data
        except:
            print("Error in downloading latest data", sys.exc_info()[0])
            raise

    def format_presentation_data(self):
        try:
            ts_data = self.download_ts_data()
            return ts_data
        except:
            print("Error in formatting series data", sys.exc_info()[0])
            raise

    def return_latest_run_id(self):
          query = '''SELECT if(max(run_id) IS NULL, 0, max(run_id)) AS maxRun FROM output_run_table;'''
          self.cursor.execute(query)
          max_r_id = self.cursor.fetchone();
          return max_r_id

    def return_last_result_indicators(self):
        try:
            query = '''SELECT max(run_id) FROM output_run_table;'''
            self.cursor.execute(query)
            max_r_id = self.cursor.fetchone();
            query = '''SELECT DISTINCT t2.vendor_key FROM output_forecast_data t1 JOIN (indicators t2) ON (t2.indicator_id = t1.indicator_id) WHERE run_id = %s;'''
            self.cursor.execute(query, (max_r_id[0], ))
            indicators = self.cursor.fetchall()
            return indicators
        except:
            print("Error selecting max run result number", sys.exc_info()[0])
            raise

    def tbl_columns(self, table_name):
        try:
            column_list = []
            query = """SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s;"""
            logging.info('retrieving table structure from ' + table_name)
            self.cursor.execute(query, (self.db_name, table_name))
            for column_name, in self.cursor:
                column_list.append(str(column_name))
        except:
            print ("Unexpected error:", sys.exc_info()[0])
            raise
        return column_list

    def return_available_series(self):
        try:
            query = '''SELECT vendor_key FROM data_indicators;'''
            self.cursor.execute(query)
            series = self.cursor.fetchall()
            return list(series)
        except:
            print ("Unexpected error retrieving available series:", sys.exc_info()[0])
            raise

    def find_incorrect_release_dates(self):
        try:
            query = '''SELECT DISTINCT t2.vendor_key FROM data_values AS t1 JOIN (data_indicators AS t2) ON (t1.indicator_id = t2.indicator_id) WHERE t1.latest = true AND t1.next_release = '1900-01-01';'''
            self.cursor.execute(query)
            indicators = self.cursor.fetchall()
            return indicators
        except:
            print ("Unexpected error finding incorrect release dates: ", sys.exc_info()[0])
            raise

    def fix_incomplete_indicator(self, incomplete_indicator, next_release_date):
        logging.info("Fixing Incomplete indicator")
        try:
            query = '''SELECT indicator_id FROM data_indicators WHERE vendor_key = %s;'''
            self.cursor.execute(query, (str(incomplete_indicator[0]),))
            indicator_id = int(self.cursor.fetchone()[0])
            query = '''UPDATE data_values SET next_release = %s WHERE indicator_id = %s AND latest = true and next_release = '1900-01-01';'''
            self.cursor.execute(query, (datetime.datetime.strftime(next_release_date, '%Y-%m-%d %H:%M'), str(indicator_id), ))
            self.cnx.commit()
            return True
        except:
            print ("Unexpected error correcting next release dates: ", sys.exc_info()[0])
            raise

    def available_updates(self):
        logging.info("Retrieving available updates")
        query = '''SELECT d1.vendor_key FROM data_indicators AS d1
            LEFT JOIN (SELECT t2.vendor_key FROM (SELECT
            indicator_id, if(min(next_release) = '1900-01-01',
            STR_TO_DATE('3000-01-01 00:00', '%Y-%m-%d %H:%i'),
            max(next_release)) AS next_release
            FROM data_values GROUP BY indicator_id) AS release_times
            LEFT JOIN data_indicators AS t2 ON t2.indicator_id = release_times.indicator_id
            WHERE convert_tz(release_times.next_release, 'UTC', 'Europe/London') <= now()
            ) AS d2 ON d1.vendor_key = d2.vendor_key
            LEFT JOIN (SELECT t4.vendor_key
            FROM data_values AS t3 RIGHT JOIN data_indicators AS t4
            ON t3.indicator_id = t4.indicator_id
            WHERE t3.indicator_id IS NULL) AS d3
            ON d1.vendor_key = d3.vendor_key
            LEFT JOIN data_sources AS d3
			ON d1.provider_id = d3.source_id
            WHERE source_name = 'MB'
            AND d2.vendor_key IS NOT NULL OR d3.vendor_key IS NOT NULL
            ;'''

        self.cursor.execute(query)
        vendor_keys = list(self.cursor.fetchall())
        logging.info("Complete")
        return vendor_keys

    def releasedIndicatorChange(self, indicators):
        try:
            query  = """SELECT tt2.vendor_key, t2.indicator_short_info, t1.value, t1.period_date, t6.presentation_unit AS unit, t3.frequency
                    FROM data_values AS t1 LEFT JOIN (data_indicators AS t2) ON  (t1.indicator_id = t2.indicator_id)
                    LEFT JOIN (meta_presentation_units AS t6) ON (t2.indicator_presentation = t6.unit_id)
                    LEFT JOIN (meta_release_frequencies AS t3) ON (t2.frequency_id = t3.frequency_id)"""

            base = 't2.vendor_key = '
            ind_str = ''
            for indicator in indicators:
                ind_str = ind_str + base + "'" + str(indicator) + "' " + ' OR '
            ind_str = ind_str[:-4]
            query += '\n\tWHERE t1.latest = true AND t1.period_date >= (NOW() - INTERVAL 2 YEAR) AND \n\t('  +  ind_str + ')\n\tORDER BY t1.period_date asc;'

            self.cursor.execute(query)
            data = pd.DataFrame(self.cursor.fetchall(), columns = ['vendor_key', 'indicator_short_info', 'value', 'period_date', 'unit', 'frequency'])

            query  = "SELECT\n\tt2.vendor_key, t1.period_date, t1.mean_forecast AS Forecast"
            query += "\nFROM\n\toutput_forecast_data AS t1\nLEFT JOIN\n\tdata_indicators AS t2 ON (t1.indicator_id = t2.indicator_id)"
            ind_str = ""
            for indicator in indicators:
                ind_str = ind_str + base + "'" + str(indicator) + "' " + ' OR '
            ind_str = ind_str[:-4]
            query += "\nWHERE\n\t({0})".format(ind_str)
            query += "\nAND\n\tt1.run_id = (SELECT max(run_id)-1 FROM output_forecast_data);"
            self.cursor.execute(query)
            forecast = pd.DataFrame(self.cursor.fetchall(), columns = ['vendor_key', 'period_date', 'Forecast'])

            results = pd.DataFrame()
            data['Transformed'] = np.nan
            units = data['unit'].unique()

            frames = []
            for indicator in indicators:
                tmp = data[data['vendor_key'] == indicator]
                unit = tmp.unit.iloc[0]
                freq = tmp.frequency.iloc[0]
                if unit == "%":
                    data.ix[data['vendor_key'] == indicator, 'Transformed'] = tmp.value
                if unit == "Annual Rate (%)":
                    data.ix[data['vendor_key'] == indicator, 'Transformed'] =  100 * tmp.value.pct_change(periods=12)
                if unit == "Index":
                    data.ix[data['vendor_key'] == indicator, 'Transformed'] = tmp.value
                if unit == "QoQ SAAR (%)":
                    if freq == "q":
                        data.ix[data['vendor_key'] == indicator, 'Transformed'] = 400 * ((tmp.value.apply(lambda x: log(x))) - (tmp.value.shift(1).apply(lambda x: log(x))))
                    if freq == "m":
                        data.ix[data['vendor_key'] == indicator, 'Transformed'] = 400 * ((tmp.value.apply(lambda x: log(x))) - (tmp.value.shift(3).apply(lambda x: log(x))))
                if unit == "QoQ, AR (%)":
                    if freq == "q":
                        data.ix[data['vendor_key'] == indicator, 'Transformed'] = 400 * ((tmp.value.apply(lambda x: log(x))) - (tmp.value.shift(1).apply(lambda x: log(x))))
                    if freq == "m":
                        data.ix[data['vendor_key'] == indicator, 'Transformed'] = 400 * ((tmp.value.apply(lambda x: log(x))) - (tmp.value.shift(3).apply(lambda x: log(x))))
                if unit == "y_{t,i}":
                    data.ix[data['vendor_key'] == indicator, 'Transformed'] = tmp.value

                FILTER = (data['vendor_key'] == indicator)
                maxDate = data[FILTER]["period_date"].max()

                frames.append(data[FILTER & (data["period_date"] == maxDate)][['vendor_key', 'indicator_short_info', 'value', 'Transformed', 'period_date', 'unit']])
            results = pd.concat(frames)
            results = pd.merge(results, forecast, on=['vendor_key', 'period_date'], how='left')
            #print(results)
            #results.replace([np.inf, -np.inf], np.nan, inplace=True)
            #results.fillna(0, inplace=True)

            return results
        except:
           print ("Error retrieving change in indicator updatese:", sys.exc_info()[0])
           raise

    def upload_mb_data(self, timeseries, indicator_key, current_release, next_release):
        try:
            table_name = 'data_values'
            df = pd.DataFrame(columns = self.tbl_columns(table_name))
            df['value'] = pd.Series(timeseries.Values)
            #Formatting the date here from a Pytime object to a string
            df['period_date'] = pd.Series(
                [t.replace(tzinfo=None) for t in timeseries.DatesAtEndOfPeriod]
                ).apply(lambda x: datetime.datetime.strftime(datetime.datetime(x.year, x.month, x.day, x.hour, x.minute), '%Y-%m-%d %H:%M'))

            query = '''SELECT indicator_id FROM data_indicators WHERE vendor_key = %s'''
            self.cursor.execute(query, (indicator_key,))
            indicator_id = int(self.cursor.fetchone()[0])
            df['indicator_id'] = indicator_id

            df['latest'] = True
            df['release_date'] = datetime.datetime.strftime(datetime.datetime(current_release.year, current_release.month, current_release.day, current_release.hour, current_release.minute), '%Y-%m-%d %H:%M')
            release_date = datetime.datetime.strftime(datetime.datetime(current_release.year, current_release.month, current_release.day, current_release.hour, current_release.minute), '%Y-%m-%d %H:%M')
            df['next_release'] = datetime.datetime.strftime(datetime.datetime(next_release.year, next_release.month, next_release.day, next_release.hour, next_release.minute), '%Y-%m-%d %H:%M')
            next_release = datetime.datetime.strftime(datetime.datetime(next_release.year, next_release.month, next_release.day, next_release.hour, next_release.minute), '%Y-%m-%d %H:%M')

            #df.drop('created_at', axis=1, inplace=True)
            #df.drop('changed_at', axis=1, inplace=True)
            logging.info('Finished creating formatted dataframe')
            # Check if any data exists for this indicator
            query = '''SELECT vintage FROM data_values WHERE indicator_id = %s LIMIT 1'''
            self.cursor.execute(query, (indicator_id,))

            if any(np.isnan(df["value"])):
                missingObservations = df.ix[np.isnan(df["value"]), :].copy()
                df = df.ix[np.isfinite(df["value"]), :]
            else:
                missingObservations = None

            if self.cursor.rowcount == 0:
                df['vintage'] = 1
                query = '''INSERT INTO data_values (indicator_id, value, period_date, release_date, next_release, latest, vintage)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON duplicate key update
                        indicator_id = indicator_id, period_date = period_date, next_release = VALUES(next_release), release_date = release_date, latest = True, value = value, vintage = vintage;'''

                df_to_tuple = [tuple((indicator_id, row["value"], row["period_date"], release_date, next_release, True, 1)) for index, row in df.iterrows()]
                self.cursor.executemany(query, df_to_tuple)

                self.cnx.commit()
                logging.info('No data exists for indicator, inserting new data with vintage 1')
            else:
                # If it exists then we need to ensure the vintage is incremented. If this is a new release date this is fine, if not further logic is required.
                # If there is already data there for this indicator and release date we return
                query = '''SELECT * FROM data_values WHERE indicator_id = %s AND release_date = %s '''
                self.cursor.execute(query, (indicator_id, df['release_date'][0],))
                if self.cursor.rowcount > 0:
                    logging.info("Nothing to be done, data exists in Db")
                    return
                query = '''select max(release_date) from data_values where indicator_id = %s '''
                self.cursor.execute(query, (indicator_id,))
                row = self.cursor.fetchone()
                logging.info('Data exists for indicator, checking dates and vintage')
                # If we have a release date before the last release date we need to insert this restrospectively and change the vintages of a later date accordingly
                if pd.to_datetime(row) > pd.to_datetime(df['release_date'][0]):
                    query = '''INSERT INTO data_values (indicator_id, value, period_date, release_date, next_release, latest, vintage)
                        SELECT %s, %s, %s, %s, %s, %s, (SELECT ifnull((SELECT MIN(vintage) FROM data_values WHERE indicator_id = %s AND period_date = %s AND release_date > %s), -1))
                        ON duplicate key UPDATE
                         indicator_id = indicator_id, period_date = period_date, next_release = VALUES(next_release), release_date = release_date, latest = True, value = value, vintage = vintage'''
                    #df_to_tuple = [tuple(x) for x in df[['indicator_id', 'value', 'period_date', 'release_date', 'next_release', 'latest']].values]
                    df_to_tuple = [tuple((indicator_id, row["value"], row["period_date"], release_date, next_release, True)) for index, row in df.iterrows()]
                    self.cursor.executemany(query, df_to_tuple)
                    self.cnx.commit()
                    query = '''select period_date,release_date from data_values where release_date = %s'''
                    self.cursor.execute(query,  (df['release_date'][0],))
                    query_tuple = self.cursor.fetchall()
                    query = '''UPDATE data_values SET vintage = vintage + 1 WHERE period_date = %s AND release_date > %s'''
                    logging.info('Inserting data retrospectively, current release date not latest date. Incrementing vintages after')
                    self.cursor.executemany(query, query_tuple)
                    self.cnx.commit()
                elif pd.to_datetime(row) <= pd.to_datetime(df['release_date'][0]):
                    query = '''SELECT indicator_id, period_date, MAX(vintage) FROM data_values WHERE indicator_id = %s GROUP BY period_date'''
                    self.cursor.execute(query, (indicator_id,))
                    rows = self.cursor.fetchall()
                    df['vintage'] = pd.DataFrame(rows)[2] + 1
                    df['vintage'] = df['vintage'].fillna(1)
                    query = '''INSERT INTO data_values(indicator_id, value, period_date, release_date, next_release, latest, vintage)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON duplicate key UPDATE
                        indicator_id = indicator_id, period_date = period_date, next_release = VALUES(next_release), release_date = release_date, latest = True, value = value, vintage = vintage;'''
                    df_to_tuple = [tuple((indicator_id, row["value"], row["period_date"], release_date, next_release, True, row['vintage'])) for index, row in df.iterrows()]
                    #df_to_tuple = [tuple(x) for x in df.values]
                    logging.info('Adding latest vintages')
                    self.cursor.executemany(query, df_to_tuple)
                    self.cnx.commit()
                else:
                    logging.info('Unhandled release date')

                query = '''UPDATE data_values SET latest = FALSE WHERE latest = TRUE AND indicator_id = %s'''
                self.cursor.execute(query, ( indicator_id,))
                self.cnx.commit();
                query = '''SELECT indicator_id, period_date, MAX(vintage) FROM data_values WHERE indicator_id = %s GROUP BY period_date'''
                self.cursor.execute(query, (indicator_id,))
                query_tuple = self.cursor.fetchall()
                query = '''UPDATE data_values SET latest = True WHERE indicator_id = %s AND period_date = %s AND vintage = %s'''
                logging.info('Ensuring latest vintage is linked with its correct latest flag')
                self.cursor.executemany(query, query_tuple)
                self.cnx.commit()

            return missingObservations
        except:
            msg = "Unexpected error: {0}".format(sys.exc_info()[0])
            logging.error(msg)
            raise

if __name__ == "__main__":
    print("main file")
    config = configparser.ConfigParser()
    config.read('/repos/Nowcast/config/configNowcasting.ini')
    db = msMBDbInterface(user=config['DATABASE_DEV']['db_user'],
                        password=config['DATABASE_DEV']['db_password'],
                        host=config['DATABASE_DEV']['db_host'],
                        db_name=config['DATABASE_DEV']['db_name'])
    vendor_key = db.available_updates()
    print(vendor_key)
    print("Is cnx connected:", db.cnx.is_connected())
    #print("Is cnx connected:", db.cursor.is_open())
