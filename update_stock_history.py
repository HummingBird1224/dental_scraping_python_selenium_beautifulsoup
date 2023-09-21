# update stock history data to mysql database.
import os

import pandas_datareader.data as web
import pymysql
import requests
from datetime import datetime, timedelta

if __name__ == "__main__":
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='stock',
        charset='utf8mb4')
    
    mycursor = conn.cursor()
    mycursor.execute("SELECT * FROM stocks")
    stocks = mycursor.fetchall()

    proxies = {
        'http': 'http://qdeawams-1:bozpoz9ordvr@p.webshare.io:80',
        'https': 'http://qdeawams-1:bozpoz9ordvr@p.webshare.io:80'
    }

    session = requests.Session()
    session.proxies = proxies

    if mycursor.rowcount == 0:
        print('No stock data exists.')
    else:
        with conn.cursor() as cursor:
            for stock in stocks:
                start_date = "2008-01-04"
                # start_date = datetime.datetime(2008, 1, 4)
                symbol = stock[3].lower()
                table_name = symbol.replace(".", "_") + "_histories"
                end_date = datetime.now().strftime('%Y-%m-%d')
                # end_date = datetime.datetime(2023, 4, 24)
                cursor.execute("SHOW TABLES LIKE '" + table_name + "'")
                if cursor.rowcount == 0:
                    cursor.execute("CREATE TABLE `" + table_name + "` ( `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT, `date` date NULL, `open` float NULL, `high` float NULL, `low` float NULL, `close` float NULL, `volume` float NULL, PRIMARY KEY (`id`) );")
                else:
                    cursor.execute("SELECT `date` from " + table_name + " order by `date` desc limit 1")
                    if cursor.rowcount != 0:
                        last_date_object = cursor.fetchone()[0]
                        # last_date_object = datetime.strptime(last_date_string, "%m/%d/%Y")
                        start_date_object = last_date_object + timedelta(days=1)
                        start_date = start_date_object.strftime('%Y-%m-%d')
                    
                try:
                    if start_date >= end_date:
                        pass
                    else:
                        if start_date != "":
                            df = web.DataReader(stock[3], data_source='stooq', start=start_date, end=end_date, session=session)
                        else:
                            df = web.DataReader(stock[3], 'stooq')
                        print(df.head())
                        for index, row in df.iterrows():
                            cursor.execute("INSERT INTO " + table_name + " (date, open, high, low, close, volume) VALUES (%s, %s, %s, %s, %s, %s)", (index.date(), row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))
                        print(symbol + " data was inserted successfully.")
                    # df = web.DataReader(symbol, 'stooq')
                    # df = web.get_data_stooq(symbol, start_date, end_date)
                    
                except Exception as e:
                    print("Error in fetching data for", symbol, ":", str(e))
                finally:
                    pass  # Added pass statement after finally
        conn.commit()
    conn.close