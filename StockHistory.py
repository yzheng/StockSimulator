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
import traceback

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
            #print "Obtained stock info from DB " + stockId
            return [self.extractStockInfo(record[0][0], record[0][1:])]
        else:
            url = self.assembleUrl(stockId, month, day, year, market)
            res = self.getHistoryStockData(stockId, url)
            #print "Obtained stock info from Yahoo " + stockId
            return res

    def extractStockInfo(self, stockId, stockInfo):
        stockDetail = {}
        stockDetail["date"] = stockInfo[0]
        stockDetail["open"]  = stockInfo[1]  #开盘
        stockDetail["high"]    = stockInfo[2]  #最高
        stockDetail["low"]    = stockInfo[3]  #最低
        stockDetail["close"] = stockInfo[4]  #收盘
        stockDetail["volume"] = stockInfo[5]  #交易量
        stockDetail["adj_close"] = stockInfo[6] #收盘adj价格
        stockDetail["code"] = stockId      #代码
        return stockDetail

    def getHistoryStockData(self, stockId, dataurl):
            result = []
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
                for stockQuote in stockQuotes:
                    stockInfo = stockQuote.split(",")
                    if len(stockInfo) == 7 and stockInfo[0]!='Date':
                        if not self.stockExitsInDate(stockId, stockInfo[0]):
                           stockDetail  = self.extractStockInfo(stockId, stockInfo)
                           self.dbOperation.insert_record(
                             stockDetail["code"],
                             stockDetail["date"],
                             stockDetail["open"],
                             stockDetail["high"],
                             stockDetail["low"],
                             stockDetail["close"],
                             stockDetail["volume"],
                             stockDetail["adj_close"]
                            )
                           result.append(stockDetail)
            except Exception as err:
                print ">>>>>> Exception: " + str(dataurl) + " " + str(err)
                traceback.print_exc()
            else:
                return result
            finally:
                None


    """def assembleUrl(self, stock_code, month, day, year, market):
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
    """
    def assembleUrl(self, stockId, month, day, year, market):
        dataUrl =  "http://ichart.yahoo.com/table.csv?"
        dataUrl += "s="  + str(stockId)
        if (market == "SZ"):
            dataUrl += ".SZ"
        if (market == "SS"):
            dataUrl += ".SS"
        dataUrl += "&d=" + str(month-1)
        dataUrl += "&e=" + str(day)
        dataUrl += "&f=" + str(year)
        dataUrl += "&a=" + str(month-1)
        dataUrl += "&b=" + str(day)
        dataUrl += "&c=" + str(year)
        dataUrl += "&g=d"
        return dataUrl

    def assembleUrlTest(self, stockId, month, day, year, market):
        #dataUrl =  "http://finance.yahoo.com/d/quotes.csv?e=.csv&"
        dataUrl =  "http://ichart.yahoo.com/table.csv?"
        dataUrl += "s="  + "USDJPY"
        dataUrl += "&d=" + str(month-1)
        dataUrl += "&e=" + str(day)
        dataUrl += "&f=" + str(year)
        dataUrl += "&a=" + str(month-1)
        dataUrl += "&b=" + str(day)
        dataUrl += "&c=" + str(year)
        dataUrl += "&g=d"
        print dataUrl
        return dataUrl


def main():
        "main function"
        #dbOperator.connDB()
        #get_stock_history()
        sh = StockHistory();
        print sh.getStockClosingPrice("600000", 2, 18, 2011, "SS")
        print sh.getStockClosingPrice("600000", 6, 28, 2016, "SS")
        #dbOperator.closeDB()
if __name__ == '__main__':
        main()
