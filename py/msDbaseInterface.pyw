import numpy as np
import pandas as pd
import datetime
import mysql.connector
import win32com.client
import sys
import logging
import msLogConfig

class msDbInterface(object):

    def __init__(self, user, password, host, db_name):
            self.user = user
            self.password = password
            self.db_name = db_name
            self.host = host
            self.cnx = mysql.connector.connect(user = self.user, password = self.password, host = self.host , database = self.db_name)
            logging.info('Opening connection to database: ' + self.db_name + ' on server ' + self.host)

    def connect(self):
        try:
            if not self.cnx.open:
                self.cnx = mysql.connector.connect(user = self.user, password = self.password, host = self.host , database = self.db_name)
                logging.info('Connection not opened on init. Opening connection to database: ' + self.db_name + 'on server' + self.host)
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

    def close(self):
        if self.cnx.open:
            logging.info('Closing connection to database: ' + self.db_name + 'on server' + self.host)
            self.cnx.close()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cnx.open:
            logging.info('Closing connection to database: ' + self.db_name + 'on server' + self.host)
            self.cnx.close()

class msMBDbInterface(msDbInterface):

    def __init__(self, user, password, host, db_name):
        msDbInterface.__init__(self, user, password, host, db_name)
        logging.info('Initializing cursor....')
        self.cursor = self.cnx.cursor(buffered = True);

    def __exit__(self, exc_type, exc_value, traceback):
        logging.info('closing cursor.....')
        self.cursor.close()

    def test(self):
        query = '''select * from data '''
        self.cursor.execute(query)
        tuple = self.cursor.fetchall()
        print(tuple)

    def test_input(self):
        try:
            logging.info("Testing input..... ")
            query = '''CREATE TABLE IF NOT EXISTS sandbox ( some_id INTEGER NOT NULL AUTO_INCREMENT,
									    input_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        some_text  TEXT,
                                        PRIMARY KEY(some_id))'''
            self.cursor.execute(query)
            query = '''INSERT INTO sandbox(some_text) VALUES("FOO")'''
            self.cursor.execute(query)
            logging.info("Testing insert")
            self.cnx.commit()
        except:
            raise
    
    def next_release_date(self):
        logging.info("Retrieving next release date")
        query = '''select min(next_release) from (select indicator_id, max(next_release) as next_release from data group by indicator_id) as release_times'''
        self.cursor.execute(query)
        time = self.cursor.fetchone()
        return time

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
            query = '''SELECT vendor_key FROM indicators'''
            self.cursor.execute(query)
            series = self.cursor.fetchall()
            return list(series)
        except:
            print ("Unexpected error retrieving available series:", sys.exc_info()[0])
            raise

    def available_updates(self):
        logging.info("Retrieving available updates")
        current_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M')
        query = '''SELECT t2.vendor_key FROM (SELECT indicator_id, MAX(next_release) AS next_release FROM data GROUP BY indicator_id) AS release_times LEFT JOIN indicators t2 ON t2.indicator_id = release_times.indicator_id WHERE release_times.next_release <= %s'''
        self.cursor.execute(query, (current_time,))
        vendor_keys = list(self.cursor.fetchall())
        logging.info("Complete")
        return vendor_keys

    def upload_mb_data(self, timeseries, indicator_key, current_release, next_release):
        try:
            table_name = 'data'
            df = pd.DataFrame(columns = self.tbl_columns(table_name))
            df['value'] = pd.Series(timeseries.Values)
            #Formatting the date here from a Pytime object to a string
            df['period_date'] = pd.Series([t.replace(tzinfo=None) for t in timeseries.DatesAtEndOfPeriod]).apply(lambda x: datetime.datetime.strftime(datetime.datetime(x.year, x.month, x.day, x.hour, x.minute), '%Y-%m-%d %H:%M'))
            query = '''SELECT indicator_id FROM indicators WHERE vendor_key = %s'''
            self.cursor.execute(query, (indicator_key,))
            indicator_id = int(self.cursor.fetchone()[0])
            df['indicator_id'] = indicator_id
            #query = '''SELECT frequency_id FROM indicators WHERE indicator_id = %s'''
            #self.cursor.execute(query, ( indicator_id,))
            #frequency_id = int(self.cursor.fetchone()[0])
            #df['frequency_id'] = frequency_id
            df['latest'] = True
            df['release_date'] = datetime.datetime.strftime(datetime.datetime(current_release.year, current_release.month, current_release.day, current_release.hour, current_release.minute), '%Y-%m-%d %H:%M')
            df['next_release'] = datetime.datetime.strftime(datetime.datetime(next_release.year, next_release.month, next_release.day, next_release.hour, next_release.minute), '%Y-%m-%d %H:%M')
            df.drop('created_at', axis=1, inplace=True)
            df.drop('changed_at', axis=1, inplace=True)
            logging.info('Finished creating formatted dataframe')
            # Check if any data exists for this indicator
            query = '''SELECT vintage FROM data WHERE indicator_id = %s LIMIT 1'''
            self.cursor.execute(query, (indicator_id,))
            if self.cursor.rowcount == 0:
                df['vintage'] = 1
                query = '''INSERT INTO data(indicator_id, value, period_date, release_date, next_release, latest, vintage)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON duplicate key update
                        indicator_id = indicator_id, period_date = period_date, release_date = release_date, latest = True, value = value, vintage = vintage;'''
                df_to_tuple = [tuple(x) for x in df.values]
                self.cursor.executemany(query, df_to_tuple)
                self.cnx.commit()
                logging.info('No data exists for indicator, inserting new data with vintage 1')
            else:
                # If it exists then we need to ensure the vintage is incremented. If this is a new release date this is fine, if not further logic is required.
                # If there is already data there for this indicator and release date we return
                query = '''SELECT * FROM data WHERE indicator_id = %s AND release_date = %s '''
                self.cursor.execute(query, (indicator_id, df['release_date'][0],))
                if self.cursor.rowcount > 0:
                    logging.info("Nothing to be done, data exists in Db")
                    return
                query = '''select max(release_date) from data where indicator_id = %s '''
                self.cursor.execute(query, (indicator_id,))
                row = self.cursor.fetchone()
                logging.info('Data exists for indicator, checking dates and vintage')
                # If we have a release date before the last release date we need to insert this restrospectively and change the vintages of a later date accordingly
                if pd.to_datetime(row) > pd.to_datetime(df['release_date'][0]):
                    query = '''INSERT INTO data(indicator_id, value, period_date, release_date, next_release, latest, vintage)
                        SELECT %s, %s, %s, %s, %s, %s, (SELECT ifnull((SELECT MIN(vintage) FROM data WHERE indicator_id = %s AND period_date = %s AND release_date > %s), -1))
                        ON duplicate key UPDATE
                         indicator_id = indicator_id, period_date = period_date, release_date = release_date, latest = True, value = value, vintage = vintage'''
                    df_to_tuple = [tuple(x) for x in df[['indicator_id', 'value', 'period_date', 'release_date', 'next_release', 'latest', 'indicator_id', 'period_date', 'release_date']].values]
                    self.cursor.executemany(query, df_to_tuple)
                    self.cnx.commit()
                    query = '''select period_date,release_date from data where release_date = %s'''
                    self.cursor.execute(query,  (df['release_date'][0],))
                    query_tuple = self.cursor.fetchall()
                    query = '''UPDATE data SET vintage = vintage + 1 WHERE period_date = %s AND release_date > %s'''
                    logging.info('Inserting data retrospectively, current release date not latest date. Incrementing vintages after')
                    self.cursor.executemany(query, query_tuple)
                    self.cnx.commit()
                elif pd.to_datetime(row) <= pd.to_datetime(df['release_date'][0]):
                    query = '''SELECT indicator_id, period_date, MAX(vintage) FROM data WHERE indicator_id = %s GROUP BY period_date'''
                    self.cursor.execute(query, (indicator_id,))
                    rows = self.cursor.fetchall()
                    df['vintage'] = pd.DataFrame(rows)[2] + 1
                    df['vintage'] = df['vintage'].fillna(1)
                    query = '''INSERT INTO data(indicator_id, value, period_date, release_date, next_release, latest, vintage)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON duplicate key UPDATE
                        indicator_id = indicator_id, period_date = period_date, release_date = release_date, latest = True, value = value, vintage = vintage;'''
                    df_to_tuple = [tuple(x) for x in df.values]
                    logging.info('Adding latest vintages')
                    self.cursor.executemany(query, df_to_tuple)
                    self.cnx.commit()
                else:
                    logging.info('Unhandled release date')

                query = '''UPDATE data SET latest = FALSE WHERE latest = TRUE AND indicator_id = %s'''
                self.cursor.execute(query, ( indicator_id,))
                self.cnx.commit();
                query = '''SELECT indicator_id, period_date, MAX(vintage) FROM data WHERE indicator_id = %s GROUP BY period_date'''
                self.cursor.execute(query, (indicator_id,))
                query_tuple = self.cursor.fetchall()
                query = '''UPDATE data SET latest = True WHERE indicator_id = %s AND period_date = %s AND vintage = %s'''
                logging.info('Ensuring latest vintage is linked with its correct latest flag')
                self.cursor.executemany(query, query_tuple)
                self.cnx.commit()
        except:
            print ("Unexpected error:", sys.exc_info()[0])
            raise
