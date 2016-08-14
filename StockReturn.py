#-*- coding: UTF-8 -*- 
from datetime import datetime

class Match:
    def __init__(self):
        self.quantity = 0
        self.discription = ''
        self.dateAcquired = 0
        self.dateSold = 0
        self.salesPrice = 0
        self.cost = 0
        self.expenseSale = 0
        self.capitalGain = 0
        self.isLongTerm = False

    def getDateDifferenceInSeconds(self, date1, date2):
        d1 = datetime.strptime(str(date1), "%Y%m%d")
        d2 = datetime.strptime(str(date2), "%Y%m%d")
        delta =  d2 - d1
        return delta.total_seconds()

    def set(self,
        quantity,
        discription,
        dateAcquired,
        dateSold,
        salesPrice,
        cost,
        expenseSale
        ) :
            self.quantity = quantity
            self.discription = discription
            self.dateAcquired = dateAcquired
            self.dateSold = dateSold
            self.salesPrice = salesPrice
            self.cost = cost
            self.expenseSale = expenseSale
            self.capitalGain = salesPrice * quantity - cost*quantity - expenseSale
            if(self.getDateDifferenceInSeconds(dateSold, dateAcquired) > 365*24*60*60):
                self.isLongTerm = True

    def __str__(self):
        return '\t'.join([ str(x) for x in
        [self.quantity,
         self.discription,
         self.dateAcquired,
         self.dateSold,
         self.salesPrice,
         self.cost,
         self.expenseSale,
         self.capitalGain,
         self.isLongTerm]])



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
        self.synopsis       = cols[self.colDef["摘要"]]
        self.transactionid   = cols[self.colDef["成交编号"]]
        self.currency        = cols[self.colDef["币种"]]
        if (self.accountId.startswith("A")):
            self.market = "SS"
        else:
            self.market = "SZ"

    def __str__(self):
        return '\t'.join([str(self.date),
                        self.stockId,
                        str(self.num)]
                        )
    def __repr__(self):
        return str(self)

class StockReturn:
    def __init__(self):
        self.returns = []
        self.stockIdToTransaction = {}
        self.buyInfo = {}
        self.sellInfo = {}
        self.matchedBuySell = []
        self.shouldSkip = [str(x) for x in [704028, 126011, 580019]]
    def processOneLine(self, data):
        cols = data.split(",")
        ds = dataSchema(cols)
        if ds.stockId == '':
            return
        #if ds.stockId in self.shouldSkip:
        #    return
        #print ds
        if (ds.transactionType == "转"):
            if (ds.synopsis.startswith("证券转入") or
                ds.synopsis.startswith("上市流通") or
                ds.synopsis.startswith("红股入帐") ):
                if ds.stockId in self.buyInfo:
                    self.buyInfo[ds.stockId].append(ds)
                else:
                    self.buyInfo[ds.stockId] = []
                    self.buyInfo[ds.stockId].append(ds)
        if (ds.transactionType == "买"):
            if ds.stockId in self.buyInfo:
                self.buyInfo[ds.stockId].append(ds)
            else:
                self.buyInfo[ds.stockId] = []
                self.buyInfo[ds.stockId].append(ds)
        if (ds.transactionType == "卖"):
            if ds.stockId in self.sellInfo:
                self.sellInfo[ds.stockId].append(ds)
            else:
                self.sellInfo[ds.stockId] = []
                self.sellInfo[ds.stockId].append(ds)



    def IterateFile(self, file_name):
        with open(file_name) as f:
            for line in f:
                line = line.strip()
                self.processOneLine(line)

    def matchTransactions(self):
        currentBuyItem = 0
        for stockId, sellItems in self.sellInfo.iteritems():
           #if stockId != "2018":
           #    continue
           buyItems = self.buyInfo[stockId]
           self.match(sellItems, buyItems)

    def genMatch(self, quantity, buyDs, sellDs):
        m = Match()
        m.set(quantity,
              buyDs.stockId,
              buyDs.date,
              sellDs.date,
              sellDs.averagePrice,
              buyDs.averagePrice,
              sellDs.commission + sellDs.transferFee + sellDs.otherFees
              )
        #print "Matched: ", m
        self.matchedBuySell.append(m)

    def printHeader(self):
        print '\t'.join([
        "quantity",
        "discription",
        "dateAcquired",
        "dateSold",
        "salesPrice",
        "cost",
        "expenseSale",
        "capitalGain",
        "isLongTerm"
        ])

    def printOutMatched(self):
        self.printHeader()
        for items in self.matchedBuySell:
            print items

    def match(self, sellItems, buyItems):
        s = 0
        b = 0
        while b < len(buyItems) and s < len(sellItems):
            #print "sellItems: ", sellItems
            #print "buyItems: ", buyItems
            #print "sell: ",s, "len(sellItems): ", str(len(sellItems)),  " " + str(abs(sellItems[s].num))
            #print "buy:", b, "len(buyItems): ", str(len(sellItems)), " " + str(abs(buyItems[b].num))
            sellItems[s].num = abs(sellItems[s].num)
            buyItems[b].num = abs(buyItems[b].num)
            if sellItems[s].num < buyItems[b].num:
                self.genMatch(sellItems[s].num,
                              buyItems[b],
                              sellItems[s]
                             )
                buyItems[b].num -= sellItems[s].num
                sellItems[s].num = 0
                s += 1
            elif sellItems[s].num == buyItems[b].num:
                self.genMatch(buyItems[b].num,
                              buyItems[b],
                              sellItems[s]
                             )
                buyItems[b].num -= sellItems[s].num
                sellItems[s].num = 0
                s += 1
                b += 1
            else: #sellItems[i].num > buyItems[j].num
                self.genMatch(buyItems[b].num,
                              buyItems[b],
                              sellItems[s]
                            )
                sellItems[s].num -= buyItems[b].num
                buyItems[b].num   -= buyItems[b].num
                b += 1
        assert(s == len(sellItems))

def main():

   fileName = "../stockmining/data/duizhangRAW2-3.csv"
   sr = StockReturn()
   sr.IterateFile(fileName)
   sr.matchTransactions()
   sr.printOutMatched()

if __name__ == "__main__":
    main()
