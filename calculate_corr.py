# calculate corr value(not sigma)
import os

import pandas as pd
import pandas_datareader as pdr
import numpy as np
import pymysql
import json

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

    if mycursor.rowcount == 0:
        print('No stock data exists.')
    else:
        with conn.cursor() as cursor:
            history_data = []
            stock1 = stocks[0]
            symbol1 = stock1[3].lower().replace(".", "_")
            stock1_table_name = symbol1 + "_histories"
            cursor.execute("SELECT close FROM " + stock1_table_name)
            if cursor.rowcount > 0:
                for j in range(cursor.rowcount):
                    # history_data[j] = []
                    history_row = {}
                    for stock in stocks:
                        history_row[stock[3].lower()] = 0
                    # print(history_row)
                    history_data.append(history_row)
            for stock in stocks:
                symbol = stock[3].lower().replace(".", "_")
                stock_table_name = symbol + "_histories"
                cursor.execute("SELECT close FROM " + stock_table_name)
                histories = cursor.fetchall()
                history_row = {}
                for index, history in enumerate(histories):
                    try:
                        history_data[index][stock[3].lower()] = history[0]
                    except Exception as e:
                        print("Error in setting data for ", index, "::", stock[3].lower(), ":", str(e))
                    finally:
                        pass  # Added pass statement after finally
                # print(history_data)
                    # history_row[stock[3].lower()] = history[0]
                # history_data.append({stock1[3].lower(): history_row})
                # history_data.append(history_row)


            df = pd.DataFrame(history_data)
            corr_matrix = df.corr()
            # print(corr_matrix.loc['1721.jp', '7203.jp'])
            cursor.execute("SHOW TABLES LIKE 'nkx_corr_coefficients'")

            if cursor.rowcount == 0:
                cursor.execute("CREATE TABLE `nkx_corr_coefficients` ( `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT, `stock1_id` bigint UNSIGNED, `stock2_id` bigint UNSIGNED, `value` float NULL, PRIMARY KEY (`id`) );")
            else:
                cursor.execute("DELETE FROM `nkx_corr_coefficients`")

            for i in range(0, len(stocks) - 1):
                for j in range(i + 1, len(stocks)):
                    corr_value = corr_matrix.loc[stocks[i][3].lower(), stocks[j][3].lower()]
                    cursor.execute("INSERT INTO nkx_corr_coefficients (stock1_id, stock2_id, value) VALUES (%s, %s, %s)", (stocks[i][0], stocks[j][0], corr_value))

                # start_date = "2008-01-04"
                # symbol = stock[3].lower()
                # table_name = symbol.replace(".", "_") + "_histories"
                # end_date = datetime.now().strftime('%Y-%m-%d')
                # cursor.execute("SHOW TABLES LIKE '" + table_name + "'")
                # if cursor.rowcount == 0:
                #     cursor.execute("CREATE TABLE `" + table_name + "` ( `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT, `date` date NULL, `open` float NULL, `high` float NULL, `low` float NULL, `close` float NULL, `volume` float NULL, PRIMARY KEY (`id`) );")
                # else:
                #     cursor.execute("SELECT `date` from " + table_name + " order by `date` desc limit 1")
                #     if cursor.rowcount != 0:
                #         last_date_object = cursor.fetchone()[0]
                #         # last_date_object = datetime.strptime(last_date_string, "%m/%d/%Y")
                #         start_date_object = last_date_object + timedelta(days=1)
                #         start_date = start_date_object.strftime('%Y-%m-%d')
                    
                # try:
                #     if start_date != "":
                #         df = web.DataReader(stock[3], 'stooq', start_date, end_date)
                #     else:
                #         df = web.DataReader(stock[3], 'stooq')
                #     for index, row in df.iterrows():
                #         cursor.execute("INSERT INTO " + table_name + " (date, open, high, low, close, volume) VALUES (%s, %s, %s, %s, %s, %s)", (index.date(), row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))
                #     print(symbol + " data was inserted successfully.")
                # except Exception as e:
                #     print("Error in fetching data for", symbol, ":", str(e))
                # finally:
                #     pass  # Added pass statement after finally
        conn.commit()
    conn.close