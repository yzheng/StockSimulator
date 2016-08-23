#-*- coding: UTF-8 -*-
from datetime import datetime
import sys
from ff import Graph

def getDateDifferenceInSeconds(date1, date2):
        d1 = datetime.strptime(str(date1), "%Y%m%d")
        d2 = datetime.strptime(str(date2), "%Y%m%d")
        delta =  d2 - d1
        return delta.total_seconds()

class Match:
    def __init__(self):
        self.quantity = 0
        self.stockId = ''
        self.discription = ''
        self.dateAcquired = 0
        self.dateSold = 0
        self.salesPrice = 0
        self.cost = 0
        self.expenseSale = 0
        self.capitalGain = 0
        self.isLongTerm = False
        self.totalNum = 0


    def set(self,
        quantity,
        stockId,
        discription,
        dateAcquired,
        dateSold,
        salesPrice,
        cost,
        expenseSale,
        totalNum
        ) :
            self.quantity = quantity
            self.stockId = stockId
            self.discription = discription
            self.dateAcquired = dateAcquired
            self.dateSold = dateSold
            self.salesPrice = salesPrice
            self.cost = cost
            self.expenseSale = expenseSale
            self.totalNum = totalNum
            print  quantity, discription
            self.capitalGain = (salesPrice - cost)*quantity - expenseSale
            if(getDateDifferenceInSeconds(dateAcquired, dateSold) > 365*24*60*60):
                self.isLongTerm = True

    def __str__(self):
        return '\t'.join([ str(x) for x in
        [self.quantity,
         self.stockId,
         self.discription,
         self.dateAcquired,
         self.dateSold,
         self.salesPrice,
         self.cost,
         self.expenseSale,
         self.capitalGain,
         self.isLongTerm,
         self.totalNum]])



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
        self.dividendInfo = {}
        self.matchedBuySell = []
        self.shouldSkip = [str(x) for x in [704028, 126011, 580019]]
    def processOneLine(self, data):
        cols = data.split(",")
        ds = dataSchema(cols)
        #if ds.stockId == '':
        #    return
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
            if (ds.synopsis.startswith("股息入帐") or
                ds.synopsis.startswith("批量") ):
                if ds.stockId not in self.dividendInfo:
                    self.dividendInfo[ds.stockId] = []
                self.dividendInfo[ds.stockId].append(ds)
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

    def getDividend(self):
        print '\t'.join(['stockId', 'date', 'totalAmount', 'Description'])
        for stockId, dividends in self.dividendInfo.iteritems():
           for item in dividends:
              print '\t'.join([ str(x) for x in [stockId,
                          item.date,
                          item.totalAmount,
                          item.synopsis
                          ]])

    def IterateFile(self, file_name):
        with open(file_name) as f:
            for line in f:
                line = line.strip()
                self.processOneLine(line)

    def matchTransactions(self):
        currentBuyItem = 0
        for stockId, sellItems in self.sellInfo.iteritems():
           if stockId != "600000":
               continue
           buyItems = self.buyInfo[stockId]
           #self.match(sellItems, buyItems)
           self.optimalMatch(sellItems, buyItems)

    def genMatch(self, quantity, buyDs, sellDs, totalNum):
        m = Match()
        m.set(quantity,
              sellDs.stockId,
              sellDs.synopsis,
              buyDs.date,
              sellDs.date,
              sellDs.averagePrice,
              buyDs.averagePrice,
              (sellDs.commission + sellDs.transferFee + sellDs.otherFees + sellDs.transactionFee + sellDs.tax) * quantity*1.0/totalNum,
              totalNum
              )
        #print "Matched: ", m
        self.matchedBuySell.append(m)

    def printHeader(self):
        print '\t'.join([
        "quantity",
        "stockId",
        "discription",
        "dateAcquired",
        "dateSold",
        "salesPrice",
        "cost",
        "expenseSale",
        "capitalGain",
        "isLongTerm",
        "TotalNum"
        ])

    def printOutMatched(self):
        self.printHeader()
        for items in self.matchedBuySell:
            print items
    def possibleMatch(self, buyItem, sellItem):
        return sellItem.date >= buyItem.date

    def getTax(self, buyItem, sellItem):
        priceDiff = sellItem.totalAmount - buyItem.totalAmount
        dateSold = sellItem.date
        dateAcquired = buyItem.date
        if (getDateDifferenceInSeconds(dateAcquired, dateSold) > 365*24*60*60):
            return 0.15*priceDiff
        else:
            return 0.25*priceDiff

    def getCost(self, buyItem, sellItem):
        cost = self.getTax(buyItem, sellItem)
        if cost > 0:
            return cost
        else:
            return 0
    def createBipartiteGraph(self, sellItems, buyItems):
        graphSize = len(buyItems) + len(sellItems) + 2
        graph = Graph(graphSize)
        #build cap constraints for edges from source to buy Items
        sourcePos = 0
        startOfBuy = 1
        startOfSell = 1 + len(buyItems)
        endPos = 1 + len(buyItems) + len(sellItems)
        #build cap constraints for eduges from buy items to end
        for i in range(startOfBuy, startOfSell):
            graph.nodeAt(0, i).setCapacity(abs(buyItems[i-1].num))
        #build cost edges between buy and sell items
        for j in range(startOfSell, endPos):
            graph.nodeAt(j, endPos).setCapacity(abs(sellItems[j-startOfSell].num))

        for i in range(startOfBuy, startOfSell):
            for j in range(startOfSell, endPos):
                if self.possibleMatch(buyItems[i-1],
                                      sellItems[j-startOfSell]):
                    unitTaxCost = self.getCost(buyItems[i-1],
                                              sellItems[j-startOfSell])
                    graph.nodeAt(i,j).setCost(unitTaxCost).setCapacity(sys.maxint)
        return (graph, startOfBuy, startOfSell, endPos)

    def interpreteGraph(self, graph, startOfBuy, startOfSell, endPos, buyItems, sellItems):
        for i in range(startOfBuy, startOfSell):
            for j in range(startOfSell, endPos):
                n = graph.nodeAt(i,j)
                #print n.getFlow()
                if n.getFlow() > 0:
                    self.genMatch(n.getFlow(), buyItems[i-1], sellItems[j-startOfSell], graph.nodeAt(j, endPos).getCapacity())


    def optimalMatch(self, sellItems, buyItems):
        print "sellItems: ", len(sellItems)
        print "buyItems: ", len(buyItems)
        (graph, startOfBuy, startOfSell, endPos) = self.createBipartiteGraph(sellItems, buyItems)
        print "Graph created:", startOfBuy, startOfSell, endPos
        print graph
        graph.minCostMaxFlow()
        print "after match"
        print graph
        self.interpreteGraph(graph, startOfBuy, startOfSell, endPos, buyItems, sellItems)

    def match(self, sellItems, buyItems):
        s = 0
        b = 0
        for x in sellItems:
            setattr(x, "totalNum", abs(x.num))
 
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
                              sellItems[s],
                              sellItems[s].totalNum
                             )
                buyItems[b].num -= sellItems[s].num
                sellItems[s].num = 0
                s += 1
            elif sellItems[s].num == buyItems[b].num:
                self.genMatch(buyItems[b].num,
                              buyItems[b],
                              sellItems[s],
                              sellItems[s].totalNum
                             )
                buyItems[b].num -= sellItems[s].num
                sellItems[s].num = 0
                s += 1
                b += 1
            else: #sellItems[s].num > buyItems[b].num
                self.genMatch(buyItems[b].num,
                              buyItems[b],
                              sellItems[s],
                              sellItems[s].totalNum
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
   #sr.getDividend()

if __name__ == "__main__":
    main()
