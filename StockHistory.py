#-*- coding: UTF-8 -*- 
'''
Created on 2015-3-1
@author: Casey, yzheng
'''
import urllib
import re
import sys
import urllib2
import db
import datetime

class StockHistory:
    def __init__(self):
        self.dbOperation = None
        self.initializeDB()

    def initializeDB(self):
        self.dbOperation = db.DBOperation('../test.db')
        self.dbOperation.create_table_if_not_exists()

    def closeDB(self):
        self.dbOperation.close()

    def stockExitsInDate(self, stockId, date):
        values = self.dbOperation.select_stock(stockId, date)
        if len(values) >= 1:
            return True

    def getStockClosingPrice(self, stockId, month, day, year, market):
        dt = datetime.date(year, month, day)
        record = self.dbOperation.select_stock(stockId, dt.isoformat())
        if (len(record) > 0):
            return record[0]
        else:
            url = self.assembleUrl(stockId, month, day, year, market)
            return self.getHistoryStockData(stockId, url)

    def getHistoryStockData(self, stockId, dataurl):
            try:
                r = urllib2.Request(dataurl)
                try:
                    stdout = urllib2.urlopen(r, data=None, timeout=3)
                except Exception,e:
                    print ">>>>>> Exception: " +str(e)
                    return None
                stdoutInfo = stdout.read().decode().encode('utf-8')
                tempData = stdoutInfo.replace('"', '')
                stockQuotes = []
                if tempData.find('404') == -1:
                    stockQuotes = tempData.split("\n")
                stockDetail = {}
                for stockQuote in stockQuotes:
                    stockInfo = stockQuote.split(",")
                    if len(stockInfo) == 7 and stockInfo[0]!='Date':
                        if not self.stockExitsInDate(stockId, stockInfo[0]):
                           stockDetail["date"] = stockInfo[0]
                           stockDetail["open"]  = stockInfo[1]  #开盘
                           stockDetail["high"]    = stockInfo[2]  #最高
                           stockDetail["low"]    = stockInfo[3]  #最低
                           stockDetail["close"] = stockInfo[4]  #收盘
                           stockDetail["volume"] = stockInfo[5]  #交易量
                           stockDetail["adj_close"] = stockInfo[6] #收盘adj价格
                           stockDetail["code"] = stockId        #代码
                           self.dbOperation.insert_record(stockDetail["code"], stockDetail["date"], stockDetail["close"])
                result = stockDetail
            except Exception as err:
                print ">>>>>> Exception: " + str(dataurl) + " " + str(err)
            else:
                return result
            finally:
                None


    def assembleUrl(self, stock_code, month, day, year, market):
        #if whitelist(stock_code, month, day, year):
        #601600 20080103 problem
        dataUrlSZ = "http://ichart.yahoo.com/table.csv?s=%s.SZ&a=%d&b=%d&c=%d&d=%d&e=%d&f=%d&g=d"%(stock_code, month-1, day,
        year, month-1, day, year)
        dataUrlSS = "http://ichart.yahoo.com/table.csv?s=%s.SS&a=%d&b=%d&c=%d&d=%d&e=%d&f=%d&g=d"%(stock_code, month-1, day,
        year, month-1, day, year)
        if (market == "SZ"):
            dataUrl = dataUrlSZ
        if (market == "SS"):
            dataUrl = dataUrlSS
        return dataUrl

def main():
        "main function"
        #dbOperator.connDB()
        #get_stock_history()
        sh = StockHistory();
        print sh.getStockClosingPrice("601600", 6, 24, 2015, "SS")
        #dbOperator.closeDB()
if __name__ == '__main__':
        main()
