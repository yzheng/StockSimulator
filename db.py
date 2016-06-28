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
        cursor.execute('''CREATE TABLE IF NOT EXISTS STOCK (stockid varchar(20) primary key, date varchar(20), closingprice varchar(20))
        ''')

    def select_stock(self, stockId, date):
        cursor = self.conn.cursor()
        cursor.execute('select * from STOCK where stockid=? and date=?',(stockId, date))
        values = cursor.fetchall()
        return values

    def insert_record(self, stockId, date, closingPrice ):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO STOCK  values (?,?,?)''', (stockId, date, closingPrice))
        self.conn.commit()
