import numpy as np
import pandas as pd
import datetime
import mysql.connector
import win32com.client
import sys

class msDbInterface(object):
  
    def __init__(self, user, password, host, db_name):
            self.user = user
            self.password = password
            self.db_name = db_name
            self.host = host
            self.cnx = mysql.connector.connect(user = self.user, password = self.password, host = self.host , database = self.db_name)

    def connect(self):
        try: 
            if self.cnx.open:    
                self.cnx = mysql.connector.connect(user = self.user, password = self.password, host = self.host , database = self.db_name)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logger.error(err)
                raise   
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logger.error(err)
                raise   
            else:
                raise error.with_traceback(sys.exc_info()[2])
    
    def getConn(self): 
        return self.cnx

    def close(self):
        if self.cnx.open:
            self.cnx.close()
                        
    def __exit__(self, exc_type, exc_value, traceback):
        if self.cnx.open:
            self.cnx.close()

class msMBDbInterface(msDbInterface):

    def __init__(self, user, password, host, db_name):
        msDbInterface.__init__(self, user, password, host, db_name)
        self.cursor = self.cnx.cursor(buffered = True);
       
    def __exit__(self, exc_type, exc_value, traceback):
        self.cursor.close()
    
    def test(self):
        query = '''select * from data '''
        self.cursor.execute(query)
        tuple = self.cursor.fetchall()
        print(tuple)
                   
    def tbl_columns(self, table_name):
        try:
            column_list = []
            query = """SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s;"""
            self.cursor.execute(query, (self.db_name, table_name))
            for column_name, in self.cursor:
                column_list.append(str(column_name))
        except:
            print ("Unexpected error:", sys.exc_info()[0])
            raise
        return column_list
   
    def upload_mb_data(self, timeseries, indicator_key, current_release, next_release):
        try:
            global tuple
            table_name = 'data'
            df = pd.DataFrame(columns = self.tbl_columns(table_name))
            timeseries.columns = ['Date', 'value']
            df['value'] = timeseries['value'] 
            df['period_date'] = [datetime.datetime.strftime(i, '%Y-%m-%d') for i in pd.to_datetime(pd.Series(timeseries['Date']))]
            query = '''SELECT indicator_id FROM indicators where vendor_key = %s'''
            self.cursor.execute(query, (indicator_key,))
            indicator_id = int(self.cursor.fetchone()[0])  
            df['indicator_id'] = indicator_id
            query = '''SELECT frequency_id FROM indicators WHERE indicator_id = %s'''
            self.cursor.execute(query, ( indicator_id,))
            frequency_id = int(self.cursor.fetchone()[0])
            df['frequency_id'] = frequency_id
            df['latest'] = True
            df['release_date'] = current_release
            df['next_release'] = next_release
            # Check if any data exists for this indicator
            query = '''SELECT vintage FROM data WHERE indicator_id = %s LIMIT 1'''
            self.cursor.execute(query, (indicator_id,))
            if self.cursor.rowcount == 0:
                df['vintage'] = 1
                query = '''INSERT INTO data(indicator_id, value, period_date, frequency_id, release_date, next_release, latest, vintage) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                        ON duplicate key update 
                        indicator_id = indicator_id, period_date = period_date, release_date = release_date, latest = True, value = value, vintage = vintage;'''
                
                tuple = [tuple(x) for x in df.values]
                self.cursor.executemany(query, tuple)
                self.cnx.commit()
            else:
                # If it exists then we need to ensure the vintage is incremented. If this is a new release date this is fine, if not further logic is required. 
                # If there is already data there for this indicator and release date we return
                query = '''select * from data where indicator_id = %s and release_date = %s '''
                self.cursor.execute(query, (indicator_id, df['release_date'][0],))
                if self.cursor.rowcount > 0:
                    return 
                query = '''select max(release_date) from data where indicator_id = %s '''
                self.cursor.execute(query, (indicator_id,))
                row = self.cursor.fetchone()
                # If we have a release date before the last release date we need to insert this restrospectively and change the vintages of a later date accordingly
                if pd.to_datetime(row) > pd.to_datetime(df['release_date'][0]):
                    query = '''INSERT INTO data(indicator_id, value, period_date, frequency_id, release_date, next_release, latest, vintage) 
                        SELECT %s, %s, %s, %s, %s, %s, %s, (select max(vintage) from data where indicator_id = %s and period_date = %s and release_date > %s)
                        ON duplicate key update
                         indicator_id = indicator_id, period_date = period_date, release_date = release_date, latest = True, value = value, vintage = vintage'''
                    tuple = [tuple(x) for x in df[['indicator_id', 'value', 'period_date', 'frequency_id', 'release_date', 'next_release', 'latest', 'indicator_id', 'period_date', 'release_date']].values]
                    self.cursor.executemany(query, tuple)
                    self.cnx.commit()
                    query = '''select period_date,release_date from data where release_date = %s'''
                    self.cursor.execute(query,  (df['release_date'][0],))
                    tuple = self.cursor.fetchall()
                    query = ''' update data set vintage = vintage + 1 where period_date = %s and release_date > %s'''
                    self.cursor.executemany(query, tuple)
                    self.cnx.commit()
                elif pd.to_datetime(row) <= pd.to_datetime(df['release_date'][0]):
                    query = '''select indicator_id, period_date, max(vintage) from data where indicator_id = %s group by period_date'''
                    self.cursor.execute(query, (indicator_id,))
                    rows = self.cursor.fetchall()
                    df['vintage'] = pd.DataFrame(rows)[2] + 1
                    df['vintage'] = df['vintage'].fillna(1)
                    query = '''INSERT INTO data(indicator_id, value, period_date, frequency_id, release_date, next_release, latest, vintage) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                        ON duplicate key update 
                        indicator_id = indicator_id, period_date = period_date, release_date = release_date, latest = True, value = value, vintage = vintage;'''
                    tuple = [tuple(x) for x in df.values]
                    self.cursor.executemany(query, tuple)
                    self.cnx.commit()
                else:
                    print("FOO")
        
                query = '''update data set latest = FALSE where indicator_id = %s'''
                self.cursor.execute(query, ( indicator_id,))    
                self.cnx.commit();    
                query = '''select indicator_id, period_date, max(vintage) from data where indicator_id = %s group by period_date'''
                self.cursor.execute(query, (indicator_id,))
                tuple = self.cursor.fetchall()
                query = '''update data set latest = True where indicator_id = %s and period_date = %s and vintage = %s'''
                self.cursor.executemany(query, tuple)
                self.cnx.commit()   
        except:
            print ("Unexpected error:", sys.exc_info()[0])
            raise
    