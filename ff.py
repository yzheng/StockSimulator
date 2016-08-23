#Python implementation of Fordfulkerson Algorithm
import sys
import heapq

class GraphNode:
    def __init__(self):
        self.capacity = 0
        self.flow = 0
        self.residual = 0
        self.cost = 0
    def getCapacity(self):
        return self.capacity
    def getFlow(self):
        return self.flow
    def getResidual(self):
        return self.residual
    def getCost(self):
        return self.cost
    def setCapacity(self, cap):
        self.capacity = cap
        return self

    def setFlow(self, flow):
        self.flow = flow
        return self

    def setResidual(self, residual):
        self.residual=residual
        return self

    def setCost(self, cost):
        self.cost = cost
        return self

    def __str__(self):
        return "(" + ",".join([ str(x) for x in [self.capacity, self.flow, self.residual, self.cost]]) + ")"

    def __repr__(self):
        return self.__str__()

class Graph:
    def __init__(self, numNodes):
        self.numNodes = numNodes
        self.graph = [[GraphNode() for x in range(numNodes)] for y in range(numNodes)]
    def __str__(self):
        result = ''
        for i in range(self.numNodes):
            for j in range(self.numNodes):
                result +=  '\t'.join([ str(x) for x in [self.graph[i][j]]])
            result += '\n'
        return result

    def __repr__(self):
        return self.__str__()

    def getNumNodes(self):
        return self.numNodes

    def nodeAt(self, row, col):
        return self.graph[row][col]

    def findAugmentedPath_dijkstra(self, s, t, parent):
        assert(s==0)
        V = self.getNumNodes()
        cost = [ sys.maxint for x in range(V)]
        cost[s] = 0
        pq = [(0,s)]
        visited = [False for x in range(V)]
        visited[s] = True

        while len(pq)>0:
            front = heapq.heappop(pq)
            d = front[0]
            u = front[1]
            if  d == cost[u] :
                for  j in range(V):
                    v = self.graph[u][j]
                    if self.graph[u][j].getResidual() > 0 and \
                        cost[u] + v.getCost() < cost[j] :
                            cost[j] = cost[u] + v.getCost()
                            heapq.heappush(pq, (cost[j], j))
                            parent[j] = u
                            visited[j] = True
        return visited[t]==True

    def minCostMaxFlow(self):
        return self.fordFulkerson(0, self.getNumNodes() - 1)

    def findPath(self, s, t, parent):
        return self.findAugmentedPath_dijkstra(s, t, parent)

    def fordFulkerson(self, s, t):
        print "In fordFulkerson:"
        print "start:", s
        print "end:", t
        V = self.getNumNodes()
        for u in range(V):
            for v in range(V):
                self.graph[u][v].setResidual(self.graph[u][v].getCapacity())
        parent = [ 0 for x in range(V)]
        maxFlow = 0
        while(self.findPath(s, t, parent)):
            pathFlow = sys.maxint;
            v = t
            print v,"<-",
            while (v != s):
                u = parent[v]
                print u,"<-",
                pathFlow = min(pathFlow, self.graph[u][v].getResidual())
                v = parent[v]
            print
            v = t
            while (v != s):
                u = parent[v]
                self.graph[u][v].setResidual(self.graph[u][v].getResidual() - pathFlow)
                self.graph[v][u].setResidual(self.graph[v][u].getResidual() + pathFlow)

                self.graph[u][v].setFlow(self.graph[u][v].getFlow() + pathFlow)
                self.graph[v][u].setFlow(self.graph[v][u].getFlow() - pathFlow)
                v = parent[v]
            maxFlow += pathFlow
        return maxFlow
