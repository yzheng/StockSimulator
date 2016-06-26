#-*- coding: UTF-8 -*- 
'''
Created on 2015-3-1
@author: Casey
'''
import urllib
import re
import sys
#from setting import params
import urllib2
#from db import *
#dbOperator = DBOperator()
#table = "stock_quote_yahoo"
'''查找指定日期股票流量'''
def isStockExitsInDate(table, stock, date):
    sql = "select * from " + table + " where code = '%d' and date='%s'" % (stock, date)
    n = dbOperator.execute(sql) 
    if n >= 1:
        return True 
def getHistoryStockData(code, dataurl):
    try:
        r = urllib2.Request(dataurl)
        try:
            stdout = urllib2.urlopen(r, data=None, timeout=3)
        except Exception,e:
            print ">>>>>> Exception: " +str(e)
            return None
        #stdoutInfo = stdout.read().decode(params.codingtype).encode('utf-8')
        stdoutInfo = stdout.read().decode().encode('utf-8')
        tempData = stdoutInfo.replace('"', '')
        stockQuotes = []
        if tempData.find('404') == -1:
            stockQuotes = tempData.split("\n")
        stockDetail = {}
        for stockQuote in stockQuotes:
            stockInfo = stockQuote.split(",")
            if len(stockInfo) == 7 and stockInfo[0]!='Date':
                #if not isStockExitsInDate(table, code, stockInfo[0]):
                   stockDetail["date"] = stockInfo[0]
                   stockDetail["open"]  = stockInfo[1]  #开盘
                   stockDetail["high"]    = stockInfo[2]  #最高
                   stockDetail["low"]    = stockInfo[3]  #最低
                   stockDetail["close"] = stockInfo[4]  #收盘
                   stockDetail["volume"] = stockInfo[5]  #交易量
                   stockDetail["adj_close"] = stockInfo[6] #收盘adj价格
                   stockDetail["code"] = code        #代码
                   #dbOperator.insertIntoDB(table, stockDetail) 
        result = stockDetail
    except Exception as err:
        print ">>>>>> Exception: " + str(dataurl) + " " + str(err)
    else:
        return result
    finally:
        None

def get_one_stock_one_day_history(stock_code, month, day, year):
    dataUrl = "http://ichart.yahoo.com/table.csv?s=%d.SS&a=%d&b=%d&c=%d&d=%d&e=%d&f=%d&g=d"%(stock_code, month-1, day,
    year, month-1, day, year)
    return getHistoryStockData(stock_code, dataUrl)

def get_one_stock_one_day_close(stock_code, month, day, year):
    return float(get_one_stock_one_day_history(stock_code, month, day, year)['close'])

def main():
    "main function"
    #dbOperator.connDB()
    #get_stock_history()
    print get_one_stock_one_day_close(600000, 8, 24, 2007)
    #dbOperator.closeDB()
if __name__ == '__main__':
    main()
