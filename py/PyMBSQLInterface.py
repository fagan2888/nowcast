import numpy as np
import pandas as pd
import datetime
import mysql.connector
import win32com.client
import sys




class Ms_Db:
    cnx = None
    def __init__(user, password, host, database):
        try:
            self.cnx = mysql.connector.connect(user = user, password = password, host = host , database = database)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logger.error(err)
                raise   
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logger.error(err)
                raise   
            else:
                raise error.with_traceback(sys.exc_info()[2])

    def add_mb_data(dataseries, indicator_key, current_release, next_release):
        cursor = cnx.cursor(buffered = True)
                
    def tbl_requirements():


indicator = 'ussurv1459'

try:
    cnx = mysql.connector.connect(user = 'dbuser', password = 'Melbourne2016', host =   'mslinuxdb01' , database = 'economic_database')
    cursor = cnx.cursor(buffered = True)
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)

try:
    list = []
    query = """SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'economic_database' AND TABLE_NAME = 'data';"""
    cursor.execute(query)
    for column_name, in cursor:
        list.append(str(column_name))

    ts =  pd.read_csv("U:\\My Documents\\ussurv1459_mddle.csv", infer_datetime_format = True)
    ts.columns = ['Date', 'value']
    df = pd.DataFrame(columns = list)
    df['value'] = ts['value']     
    df['period_date'] = [datetime.datetime.strftime(i, '%Y-%m-%d') for i in pd.to_datetime(pd.Series(ts['Date']), '%Y-%m-%d')]
  
    query = '''SELECT indicator_id FROM indicators where vendor_key = %s'''

    cursor = cnx.cursor(buffered = True)
    cursor.execute(query, (indicator,))
    indicator_id = int(cursor.fetchone()[0])  
        
    df['indicator_id'] = indicator_id

    query = '''SELECT frequency_id FROM indicators WHERE indicator_id = %s'''
    cursor.execute(query, ( indicator_id,))
    frequency_id = int(cursor.fetchone()[0])
    df['frequency_id'] = frequency_id
    
    df['latest'] = True
    df['release_date'] = '2016-09-01'
    df['next_release'] = '2016-10-01'
    
    # Check if any data exists for this indicator
    query = '''SELECT vintage FROM data WHERE indicator_id = %s LIMIT 1'''
    cursor.execute(query, (indicator_id,))
    if cursor.rowcount == 0:
        df['vintage'] = 1
        query = '''INSERT INTO data(indicator_id, value, period_date, frequency_id, release_date, next_release, latest, vintage) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                ON duplicate key update 
                indicator_id = indicator_id, period_date = period_date, release_date = release_date, latest = True, value = value, vintage = vintage;'''
        tuple = [tuple(x) for x in df.values]
        cursor.executemany(query, tuple)
        cnx.commit()
    else:
        # If it exists then we need to ensure the vintage is incremented. If this is a new release date this is fine, if not further logic is required. 
        # If there is already data there for this indicator and release date we return
        query = '''select * from data where indicator_id = %s and release_date = %s '''
        cursor.execute(query, (indicator_id, df['release_date'][0],))
        if cursor.rowcount > 0:
            cursor.close()
            cnx.close()
            sys.exit()

        query = '''select max(release_date) from data where indicator_id = %s '''
        cursor.execute(query, (indicator_id,))
        row = cursor.fetchone()
        # If we have a release date before the last release date we need to insert this restrospectively and change the vintages of a later date accordingly
        if pd.to_datetime(row) > pd.to_datetime(df['release_date'][0]):
            query = '''INSERT INTO data(indicator_id, value, period_date, frequency_id, release_date, next_release, latest, vintage) 
                SELECT %s, %s, %s, %s, %s, %s, %s, (select max(vintage) from data where period_date = %s and release_date > %s)
                ON duplicate key update
                 indicator_id = indicator_id, period_date = period_date, release_date = release_date, latest = True, value = value, vintage = vintage'''
            
            tuple = [tuple(x) for x in df[['indicator_id', 'value', 'period_date', 'frequency_id', 'release_date', 'next_release', 'latest', 'period_date', 'release_date']].values]
            cursor.executemany(query, tuple)
            cnx.commit()
            query = '''select period_date,release_date from data where release_date = %s'''
            cursor.execute(query,  (df['release_date'][0],))
            tuple = cursor.fetchall()
            query = ''' update data set vintage = vintage + 1 where period_date = %s and release_date > %s'''
            cursor.executemany(query, tuple)
            cnx.commit()

        elif pd.to_datetime(row) <= pd.to_datetime(df['release_date'][0]):
            query = '''select t1.vintage from data t1 left join data t2 on t1.period_date = t2.period_date and t1.vintage < t2.vintage'''
            cursor.execute(query)
            rows = cursor.fetchall()
            df['vintage'] = pd.DataFrame(rows)[0] + 1
            df['vintage'] = df['vintage'].fillna(1)
            query = '''INSERT INTO data(indicator_id, value, period_date, frequency_id, release_date, next_release, latest, vintage) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                ON duplicate key update 
                indicator_id = indicator_id, period_date = period_date, release_date = release_date, latest = True, value = value, vintage = vintage;'''
            tuple = [tuple(x) for x in df.values]
            cursor.executemany(query, tuple)
            cnx.commit()
        else:
            print("FOO")
        
    query = '''update data set latest = FALSE where indicator_id = %s'''
    cursor.execute(query, ( indicator_id,))    
    cnx.commit();    

    query = '''select t1.indicator_id, t1.period_date, t1.release_date, t1.vintage from data t1 left join data t2 on t1.period_date = t2.period_date and t1.vintage < t2.vintage;'''
    cursor.execute(query)
    tuple = cursor.fetchall()
    query = '''update data set latest = True where indicator_id = %s and period_date = %s and release_date = %s and vintage = %s'''
    cursor.executemany(query, tuple)
    cnx.commit();    
    cursor.close()
    cnx.close()

except:
    print "Unexpected error:", sys.exc_info()[0]
    raise

