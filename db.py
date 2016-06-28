import sqlite3

class DBOperation:
    def __init__(self, fileName):
        self.conn  = sqlite3.connect(fileName)

    def close(self):
        self.conn.close()

    def drop_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''DROP TABLE IF EXISTS STOCK''')

    def create_table_if_not_exists(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS STOCK (
        stockid varchar(20),
        date varchar(20),
        openprice varchar(20),
        highprice varchar(20),
        lowprice varchar(20),
        closclosingprice varchar(20),
        volum varchar(20),
        adjclosingprice varchar(20), PRIMARY KEY(stockid, date))''')

    def select_stock(self, stockId, date):
        cursor = self.conn.cursor()
        cursor.execute('select * from STOCK where stockid=? and date=?',(stockId, date))
        values = cursor.fetchall()
        return values

    def insert_record(self, stockId, date, openprice, highprice, lowprice, closingprice, volume, adjclosingprice ):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO STOCK  values (?,?,?,?,?,?,?,?)''', (stockId, date, openprice, highprice, lowprice, closingprice, volume, adjclosingprice))
        self.conn.commit()
