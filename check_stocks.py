# check mysql database and see if there are stocks data or not.
# If not exists, add them to mysql database.
import os

import pandas as pd
import pymysql

if __name__ == "__main__":
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='stock',
        charset='utf8mb4')
    
    mycursor = conn.cursor()
    mycursor.execute("SELECT count(*) FROM stocks")
    count = mycursor.fetchone()[0]

    if count == 0:
        with conn.cursor() as cursor:
            for i in range(1, 4):
                url = 'https://stooq.com/t/?i=589&v=0&l=' + str(i)
                df = pd.read_html(url)[0]
                brand_names = df['Name'].to_numpy()
                symbols = df['Symbol'].to_numpy()
                length = len(brand_names)

                query = f"INSERT INTO stocks (stock_category_id, name, symbol) VALUES (%s, %s, %s)"
                
                for j in range(5, length - 2):
                    cursor.execute(query, ("1", brand_names[j], symbols[j]))
                    print(brand_names[j] + " is inserted")
            conn.commit()
        conn.close
    else:
        print('Data already exists')