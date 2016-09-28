import numpy as np
import pandas as pd
import datetime
import mysql.connector
import win32com.client
import sys

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

#try:
 #   conn = win32com.client.Dispatch("Macrobond.Connection")
#except:
 #   print "Unexpected error:", sys.exc_info()[0]
 #   raise

try:
    list = []
    query = """SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'economic_database' AND TABLE_NAME = 'data';"""
    cursor.execute(query)
    for column_name, in cursor:
        list.append(str(column_name))

    ts =  pd.read_csv("U:\\My Documents\\ussurv1459_new.csv", infer_datetime_format = True)
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
    
    df['latest'] = True
    df['release_date'] = '2016-09-01'
    df['next_release'] = '2016-12-01'
    
    query = '''SELECT vintage FROM data WHERE indicator_id = %s LIMIT 1'''
        
    cursor.execute(query, (indicator_id,))
    if cursor.rowcount == 0:
        df['vintage'] = 1
    else:
        query = '''select max(release_date) from data where indicator_id = %s '''
        cursor.execute(query, (indicator_id,))
        row = cursor.fetchone()
        if pd.to_datetime(row) > pd.to_datetime(df['release_date'][0]):
           print(row)
        elif pd.to_datetime(row) <= pd.to_datetime(df['release_date'][0]):
            query = '''select t1.vintage from data t1 left join data t2 on t1.period_date = t2.period_date and t1.vintage < t2.vintage'''
            cursor.execute(query)
            df['vintage'] = 2
            rows = cursor.fetchall()
            df['vintage'] = int(rows)
        else:
            print("FOO")

        query = '''select t1.release_date, t1.period_date, t1.vintage, t1.value from data t1 left join data t2 on t1.period_date = t2.period_date and t1.vintage < t2.vintage'''
        cursor.execute(query)
        df['vintage'] = 2
        rows = cursor.fetchall()
        tmp_df = pd.DataFrame(rows)
          
   
    
    df['frequency_id'] = frequency_id

    tuple = [tuple(x) for x in df.values]

    query = '''INSERT INTO data(indicator_id, value, period_date, frequency_id, release_date, next_release, latest, vintage) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                ON duplicate key update 
                indicator_id = indicator_id, period_date = period_date, release_date = release_date, latest = True, value = value, vintage = vintage;'''

    cursor.executemany(query, tuple)
    cnx.commit()
    cursor.close()
    cnx.close()
except:
    print "Unexpected error:", sys.exc_info()[0]
    raise

