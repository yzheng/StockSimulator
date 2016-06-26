import copy
import sys
import StockHistory as sh

def getOneDayStockClose(stockId, month, day, year):
    sh.get_one_stock_one_day_close(stockId, month, day, year)

class BalanceSheetTimeSeries:
    def __init__(self):
        self.balanceSheets = []
        self.balanceSheetsDate = []

    def add(self, balanceSheet):
        self.balanceSheetsDate.append(balanceSheet.getDate())
        self.balanceSheets.append(balanceSheet)

    def ifExist(self, date):
        return date in balanceSheetsDate

    def buildBalanceSheet(self, date):
        bs = BalanceSheet(date)
        if len(self.balanceSheets) > 0:
            bs = copy.deepcopy(self.balanceSheets[:-1])
        self.add(bs)
        return bs

    def getDateRange(self):
        return (min(self.balanceSheetsDate), max(self.balanceSheetsDate))

    def getBalanceSheet(self, date):
        if date not in balanceSheetsDate:
            raise Exception("trying to retrieve a balance sheet not existing")
        return self.balanceSheets[self.balanceSheetsDate.index(date)]

    def calcBalances(self, startDate, endDate):
        for date in self.balanceSheetsDate:
            if date >= startDate and date <= endDate:
                self.balanceSheets[self.balanceSheetsDate.index(date)].calcBalance()

    def getStockBalance(self, date):
        if date not in balanceSheetsDate:
            raise Exception("Trying to retrieve a balance sheet not existing")
        self.balanceSheets[self.balanceSheetsDate.index(date)].getStockBalance()

    def getCashBalance(self, date):
        if date not in balanceSheetsDate:
            raise Exception("Trying to retrieve a balance sheet not existing")
        self.balanceSheets[self.balanceSheetsDate.index(date)].getCashBalance()


    def printBalances(self, startDate, endDate):
        for date in self.balanceSheetsDate:
            result = ""
            if date >= startDate and date <= endDate:
                cash = self.getCashBalance(date)
                result += cash + "\t"
                stocks = self.getStockBalance(date)
                for s in stocks:
                    result += s + "\t" + str(stocks[s]) + "\t"
                result += "\n"
            sys.stdout.write(result)

class BalanceSheet:
    def __init__(self, date):
        self.date = date
        self.accounts = {} #account id to a list of stock id
        self.stocks = {} #stock id, number of stocks
        self.cash = 0
        self.stockPriceMap = {}
        self.stockBalancePerAccount = {}
        self.totalStockBalance = 0
    def getYearMonthDay(self, date):
        year = date/10000
        month = (date - year * 10000)/100
        day = (date - year * 10000 - month*100)
        return (year, month, day)

    def getStockPrice(self):
        self.stockPriceMap = {}
        for stockId in self.stocks:
            (year, month, day) = self.getYearMonthDay(self.date)
            price = getOneDayStockClose(stockId, month, day, year)
            self.stockPriceMap[stockId] = price

    def calcBalance():
        self.getStockPrice()
        self.totalStockBalance = 0;
        self.totalBalancePerAccount = {}
        for accountId in accounts:
            total = 0
            for stockId in accounts[accountId]:
                if stockId not in stockPriceMap:
                    raise Exception ("StockId not in stockPriceMap")
                total += stockPriceMap[stockId] * stocks[stockId]
            self.totalBalancePerAccount[accountId] = total
            self.totalStockBalance += total
        return self.totalStockBalance

    def getStockBalance():
        return self.totalBalancePerAccount

    def getCashBalance():
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
            raise Exception("accountId not in accounts")
        if (stockId not in self.accounts[accountId]):
            raise Exception("trying to remove a stock that is not in account")
        else:
            self.accounts[accountId].remove(stockId)

    def buyStock(self, accountId, stockId, num, purchasePrice,
                 transactionFee, tax, commission, otherFees, transferFee):
        if (stockId in self.stocks):
            self.stocks[stockId] += num
        else:
            self.stocks[stockId] = num
            #make sure we only add stockId to account once
            self.addStockToAccount(accountId, stockId)
        #since tax is already caluclated in purchasePrice, we don't double count here
        self.cash -= (purchasePrice*num + commission + otherFees + transferFee)

   def sellStock(self, accountId, stockId, num, sellPrice, transactionFee, tax, commission, otherFees, transferFee):
        if (stockId in self.stocks):
            self.stocks[stockId] -= num
            if self.stocks[stockId] == 0:
                del self.stocks[stockId]
                removeStockFromAccount(accountId, stockId)
        else:
            raise Exception("Trying to sell stock that is not already bought")
        self.cash += sellPrice*num
        #since tax is already caluclated in sellPrice, we don't double count here
        self.cash -= (commission + otherFees + transferFee)

    def transfer(self, cashAmount):
        self.cash += cashAmount

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
        self.accounId        = cols[self.colDef["股东帐户"]]
        self.commission      = float(cols[self.colDef["佣金"]])
        self.transferFee     = float(cols[self.colDef["过户费"]])
        self.operation       = cols[self.colDef["操作"]]
        self.totalAmount     = float(cols[self.colDef["发生金额"]])
        self.balance         = float(cols[self.colDef["资金余额"]])
        self.synoposis       = cols[self.colDef["摘要"]]
        self.transactionid   = cols[self.colDef["成交编号"]]
        self.currency        = cols[self.colDef["币种"]]


class EventGenerator:
    def __init__(self, fileName, BalanceSheetTimeSeries):
        self.fileName = fileName
        self.BTS = BalanceSheetTimeSeries

    def getBalanceSheetTimeSeries(self):
        return self.BTS

    def IterateFile(self, startDate, endDate):
        with open(self.fileName) as f:
            data = f.read()
            processOneLine(data, startDate, endDate)

    def processOneLine(self, data, startDate, endDate):
        cols = data.split(",")
        ds = dataSchema(cols)
        if ds.date < startDate or ds.date > endDate:
            return
        if (ds.transactionType == "转"):
            self.transactionHander("Transfer", ds)
        if (ds.transactionType == "买"):
            self.transactionHandler("Buy", ds)
        if (ds.transactionType == "卖"):
            self.transactionHandler("Sell", ds)

    def transactionHandler(self, transactionType, dataSchemaObj):
        ds = dataSchemaObj
        balanceSheet = None
        if not self.BTS.ifExisit(date):
            balanceSheet = self.BTS.buildBalanceSheet(date)
        else:
            balanceSheet = self.BTS.getBalanceSheet(date)
        if transactionType == "Buy":
            balanceSheet.buyStock (ds.accountId, ds.stockId, ds.num, ds.averagePrice,
                               ds.transactionFee, ds.tax, ds.commission, ds.otherFees, ds.transferFee)
        if transactionType == "Sell":
            balanceSheet.sellStock (ds.accountId, ds.stockId, ds.num, ds.averagePrice,
                               ds.transactionFee, ds.tax, ds.commission, ds.otherFees, ds.transferFee)
        if transactionType == "Transfer":
            balanceSheet.transfer (ds.totalAmount)



#main class
def main():
    fileName = "~/DevPj/stockmining/data/duizhangRAW2.csv"
    bts = BalanceSheetTimeSeries()
    evg = EventGenerator(bts, fileName)
    evg.IterateFile(20070101, 20071231)
    bst = evg.getBalanceSheetTimeSeries()
    dateRange = bst.getDateRange()
    bst.calcBalances(dateRange[0], dateRange[1])
    bst.printBalances(dateRange[0], dateRange[1])
