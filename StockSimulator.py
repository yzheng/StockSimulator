#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import sys
import StockHistory as sh
import traceback

SHistory = sh.StockHistory()

def getYearMonthDay(date):
    year = date/10000
    month = (date - year*10000)/100
    day = (date - year * 10000 - month*100)
    return (year, month, day)

def formatDate(date):
    year,month,day = getYearMonthDay(date)
    return str(year) + "/" + str(month) + "/" + str(day)

def normalizeStockId(stockId):
    slen = len(stockId)
    if (slen < 6):
        for i in range (0, 6-slen):
            stockId = '0' + stockId
    return stockId

def getOneDayStockClose(stockId, month, day, year, market):
    slen = len(stockId)
    if stockId == "562":
        stockId = "166"
    if stockId == "000562":
        stockId = "000166"
    stockId = normalizeStockId(stockId)
    res = SHistory.getStockClosingPrice(stockId, month, day, year, market)
    if res == None:
        print stockId
        return 1
    else:
        res = float(res[0]['close'])
    return res
class BalanceSheetTimeSeries:
    def __init__(self):
        self.balanceSheets = []
        self.balanceSheetsDate = []

    def add(self, bSheet):
        self.balanceSheetsDate.append(bSheet.getDate())
        self.balanceSheets.append(bSheet)

    def ifExist(self, date):
        return date in self.balanceSheetsDate

    def buildBalanceSheet(self, date):
        bs = BalanceSheet(date)
        if len(self.balanceSheets) > 0:
            bs = copy.deepcopy(self.balanceSheets[-1])
            bs.setDate(date)
        self.add(bs)
        return bs

    def getDateRange(self):
        return (min(self.balanceSheetsDate), max(self.balanceSheetsDate))

    def getBalanceSheet(self, date):
        if date not in self.balanceSheetsDate:
            raise Exception("trying to retrieve a balance sheet not existing")
        return self.balanceSheets[self.balanceSheetsDate.index(date)]

    def calcBalances(self, startDate, endDate):
        for date in self.balanceSheetsDate:
            if date >= startDate and date <= endDate:
                self.balanceSheets[self.balanceSheetsDate.index(date)].calcBalance()

    def getStockBalance(self, date):
        if date not in self.balanceSheetsDate:
            raise Exception("Trying to retrieve a balance sheet not existing")
        return self.balanceSheets[self.balanceSheetsDate.index(date)].getStockBalance()

    def getCashBalance(self, date):
        if date not in self.balanceSheetsDate:
            raise Exception("Trying to retrieve a balance sheet not existing")
        return self.balanceSheets[self.balanceSheetsDate.index(date)].getCashBalance()

    def printCashBalances(self, startDate, endDate):
        for date in self.balanceSheetsDate:
            result = formatDate(date) + "\t"
            if date >= startDate and date <= endDate:
                cash = self.getCashBalance(date)
                result += "cash"+"\t"+str(cash) + "\n"
            sys.stdout.write(result)


    def printBalances(self, startDate, endDate):
        print "date\tcash\t109247238\tA525260141\tTotalStock\tTotalAsset\tSHA300\n"
        result = ""
        for date in self.balanceSheetsDate:
            result = formatDate(date) + "\t"
            if date >= startDate and date <= endDate:
                cash = self.getCashBalance(date)
                result += str(cash) + "\t"
                stockBalancePerAccount = self.getStockBalance(date)
                totalStocks = 0
                for s in stockBalancePerAccount.keys():
                    if s == '0': continue
                    totalStocks += stockBalancePerAccount[s]
                    result +="%.2f\t"%(stockBalancePerAccount[s])
                result += "%.2f\t%.2f\n"%(totalStocks, totalStocks + cash)
                year, month, day = getYearMonthDay(date)
                #result += str(getOneDayStockClose('000300', month, day, year, "SS")) + "\n"
            sys.stdout.write(result)

class BalanceSheet:
    def __init__(self, date):
        self.date = date
        self.accounts = {} #account id to a list of stock id
        self.stocks = {} #stock id, number of stocks
        self.stockIdMarketMap = {} #stock id, stock type
        self.cash = 0
        self.stockPriceMap = {}
        self.stockBalancePerAccount = {}
        self.totalStockBalance = 0

    def debugPrint(self):
        print "---debug---"
        print "BalanceSheet"
        print self.date
        print self.accounts
        print self.stocks
        print self.cash
        print self.stockPriceMap
        print self.stockBalancePerAccount
        print self.totalStockBalance
        print "-----------"
    def setDate(self, date):
        self.date = date

    def getYearMonthDay(self, date):
        year = date/10000
        month = (date - year * 10000)/100
        day = (date - year * 10000 - month*100)
        return (year, month, day)

    def getStockPrice(self):
        #self.stockPriceMap = {}
        for stockId in self.stocks:
            (year, month, day) = self.getYearMonthDay(self.date)
            market = self.stockIdMarketMap[stockId]
            try:
                price = getOneDayStockClose(stockId, month, day, year, market)
                self.stockPriceMap[stockId] = price
            except:
                traceback.print_exc()
                if (stockId in self.stockPriceMap):
                    print "using default price set by purchase/sell " + stockId + " " + str(month) + " " + str(day) + " " + str(year)
                else:
                    print "price Error " + stockId + " "+str(month) + " " + str(day) + " " + str(year)

    def calcBalance(self):
        self.getStockPrice()
        self.totalStockBalance = 0;
        self.stockBalancePerAccount = {}
        for accountId in self.accounts:
            total = 0
            for stockId in self.accounts[accountId]:
                if stockId not in self.stockPriceMap:
                    raise Exception( "StockId not in stockPriceMap " + stockId + " date:" + str(self.date))
                else:

                    subTotal = self.stockPriceMap[stockId] * self.stocks[stockId]
                    print "stockId: %s, price: %f, num:%ld, subtotal:%ld"%( stockId, self.stockPriceMap[stockId], self.stocks[stockId], subTotal)
                    total += subTotal
            self.stockBalancePerAccount[accountId] = total
            self.totalStockBalance += total
        return self.totalStockBalance

    def getStockBalance(self):
        return self.stockBalancePerAccount

    def getCashBalance(self):
        return self.cash

    def getDate(self):
        return self.date

    def addStockToAccount(self, accountId, stockId):
        if (accountId in self.accounts):
            self.accounts[accountId].append(stockId)
        else:
            self.accounts[accountId] = [];
            self.accounts[accountId].append(stockId)

    def removeStockFromAccount(self, accountId, stockId):
        if (not accountId in self.accounts):
            raise Exception("accountId (%s) not in accounts"%(accountId))
        if (stockId not in self.accounts[accountId]):
            raise Exception("trying to remove a stock (%s) that is not in account %s"%(stockId, accountId))
        else:
            self.accounts[accountId].remove(stockId)

    def buyStock(self, accountId, stockId, num, purchasePrice,
                 transactionFee, tax, commission, otherFees, transferFee, market, totalAmount):
        stockId = normalizeStockId(stockId)
        if (stockId == "126011"): return
        if (stockId in self.stocks):
            self.stocks[stockId] += num
        else:
            self.stocks[stockId] = num
            #make sure we only add stockId to account once
            self.addStockToAccount(accountId, stockId)
        #since transaction fee is already caluclated in purchasePrice, we don't double count here
        self.stockIdMarketMap[stockId] = market
        #self.cash -= (purchasePrice*num + tax + commission + otherFees + transferFee)
        self.cash += totalAmount
        self.stockPriceMap[stockId] = purchasePrice #default price
        print stockId + " Price:" + str(self.stockPriceMap[stockId])
        print "buy " + stockId + " " + str(num) + " at: " + str(purchasePrice) + " on:" + str(self.date)

    def sellStock(self, accountId, stockId, num, sellPrice, transactionFee, tax, commission, otherFees, transferFee,
        totalAmount):
        stockId = normalizeStockId(stockId)
        print "sell"
        print ("Sellling: %s, %s, %ld"%(accountId, stockId, num))
        if (stockId == "126011"): return
        if (stockId in self.stocks):
            self.stocks[stockId] += num
            if self.stocks[stockId] == 0:
                del self.stocks[stockId]
                self.removeStockFromAccount(accountId, stockId)
            else:
                self.stockPriceMap[stockId] = sellPrice #default price
        else:
            raise Exception("Trying to sell stock that is not already bought " + stockId)
        #self.cash += -1.0*sellPrice*num
        #self.cash -= (tax + commission + otherFees + transferFee)
        self.cash += totalAmount
        print "sell " + stockId + " " + str(num) + " at: " + str(sellPrice)

    def transferStock(self, accountId, stockId, num, purchasePrice,
                 transactionFee, tax, commission, otherFees, transferFee, market, totalAmount):
        #Same as buy, except that we don't set default price
        stockId = normalizeStockId(stockId)
        if (stockId == "126011"): return
        if (stockId in self.stocks):
            self.stocks[stockId] += num
        else:
            self.stocks[stockId] = num
            #make sure we only add stockId to account once
            if (accountId != ""):
                self.addStockToAccount(accountId, stockId)
        #since transaction fee is already caluclated in purchasePrice, we don't double count here
        self.stockIdMarketMap[stockId] = market
        #self.cash -= (purchasePrice*num + tax + commission + otherFees + transferFee)
        self.cash += totalAmount
        print "Transfer " + stockId + " " + str(num)



class dataSchema:
    def __init__(self, cols):
        self.colDef = {  "成交日期": 0,
                         "证券代码": 1,
                         "操作": 2,
                         "发生金额":3,
                         "资金余额":4,
                         "摘要":5,
                         "成交数量":6,
                         "成交均价":7,
                         "成交金额":8,
                         "交易费用":9,
                         "印花税":10,
                         "其他费用":11,
                         "成交编号":12,
                         "股东帐户":13,
                         "币种":14,
                         "佣金":15,
                         "过户费":16
        }
        self.date            = long(cols[self.colDef["成交日期"]])
        self.stockId         = cols[self.colDef["证券代码"]]
        self.transactionType = cols[self.colDef["操作"]]
        self.num             = long(cols[self.colDef["成交数量"]])
        self.averagePrice    = float(cols[self.colDef["成交均价"]])
        self.transactionFee  = float(cols[self.colDef["交易费用"]])
        self.tax             = float(cols[self.colDef["印花税"]])
        self.otherFees       = float(cols[self.colDef["其他费用"]])
        self.accountId       = cols[self.colDef["股东帐户"]]
        self.commission      = float(cols[self.colDef["佣金"]])
        self.transferFee     = float(cols[self.colDef["过户费"]])
        self.operation       = cols[self.colDef["操作"]]
        self.totalAmount     = float(cols[self.colDef["发生金额"]])
        self.balance         = float(cols[self.colDef["资金余额"]])
        self.synoposis       = cols[self.colDef["摘要"]]
        self.transactionid   = cols[self.colDef["成交编号"]]
        self.currency        = cols[self.colDef["币种"]]
        if (self.accountId.startswith("A")):
            self.market = "SS"
        else:
            self.market = "SZ"

class EventGenerator:
    def __init__(self, fileName, BalanceSheetTimeSeries):
        self.fileName = fileName
        self.BTS = BalanceSheetTimeSeries

    def getBalanceSheetTimeSeries(self):
        return self.BTS

    def IterateFile(self, startDate, endDate):
        with open(self.fileName) as f:
            for line in f:
                line = line.strip()
                self.processOneLine(line, startDate, endDate)

    def processOneLine(self, data, startDate, endDate):
        cols = data.split(",")
        ds = dataSchema(cols)
        if ds.date < startDate or ds.date > endDate:
            return
        if (ds.transactionType == "转"):
            self.transactionHandler("Transfer", ds)
        if (ds.transactionType == "买"):
            self.transactionHandler("Buy", ds)
        if (ds.transactionType == "卖"):
            self.transactionHandler("Sell", ds)

    def transactionHandler(self, transactionType, dataSchemaObj):
        ds = dataSchemaObj
        balanceSheet = None
        if not self.BTS.ifExist(ds.date):
            balanceSheet = self.BTS.buildBalanceSheet(ds.date)
        else:
            balanceSheet = self.BTS.getBalanceSheet(ds.date)
        if transactionType == "Buy":
            balanceSheet.buyStock (ds.accountId, ds.stockId, ds.num, ds.averagePrice,
                               ds.transactionFee, ds.tax, ds.commission, ds.otherFees, ds.transferFee, ds.market,
                               ds.totalAmount)
        if transactionType == "Sell":
            balanceSheet.sellStock (ds.accountId, ds.stockId, ds.num, ds.averagePrice,
                               ds.transactionFee, ds.tax, ds.commission, ds.otherFees, ds.transferFee, ds.totalAmount)
        if transactionType == "Transfer":
             balanceSheet.transferStock (ds.accountId, ds.stockId, ds.num, ds.averagePrice,
                               ds.transactionFee, ds.tax, ds.commission, ds.otherFees, ds.transferFee, ds.market,
                               ds.totalAmount)




#main class
def main():
    fileName = "../stockmining/data/duizhangRAW2-3.csv"
    bts = BalanceSheetTimeSeries()
    evg = EventGenerator(fileName, bts)
    evg.IterateFile(20070101, 200151231)
    bst = evg.getBalanceSheetTimeSeries()
    dateRange = bst.getDateRange()
    bst.printCashBalances(dateRange[0], dateRange[1])
    bst.calcBalances(dateRange[0], dateRange[1])
    bst.printBalances(dateRange[0], dateRange[1])
    SHistory.closeDB()

if __name__=="__main__":
    main()
