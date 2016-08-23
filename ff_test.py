import unittest
from ff import Graph

class TestGraph(unittest.TestCase):
    def test_create(self):
        g = Graph(5)
        g.nodeAt(0,0).capacityIs(1)
        g.nodeAt(4,4).flowIs(3)
        g.nodeAt(3,2).residualIs(100)
        g.nodeAt(3,2).costIs(2)
        print g
        self.assertEqual(g.nodeAt(0,0).getCapacity(), 1)
        self.assertEqual(g.nodeAt(4,4).getFlow(), 3)
        self.assertEqual(g.nodeAt(3,2).getResidual(), 100)
        self.assertEqual(g.nodeAt(3,2).getCost(), 2)

class TestFF(unittest.TestCase):
    def setUp(self):
        self.g = Graph(6)
        self.g.nodeAt(0,1).capacityIs(16).costIs(100)
        self.g.nodeAt(0,2).capacityIs(13).costIs(2)
        self.g.nodeAt(1,2).capacityIs(10).costIs(3)
        self.g.nodeAt(1,3).capacityIs(12).costIs(100)
        self.g.nodeAt(2,1).capacityIs(4).costIs(5)
        self.g.nodeAt(2,4).capacityIs(14).costIs(1)
        self.g.nodeAt(3,2).capacityIs(9).costIs(7)
        self.g.nodeAt(3,5).capacityIs(20).costIs(100)
        self.g.nodeAt(4,3).capacityIs(7).costIs(9)
        self.g.nodeAt(4,5).capacityIs(4).costIs(1)

    def test_ff(self):
        flow = self.g.fordFulkerson(0, 5)
        print "max possible flow is:" , flow

if __name__ == '__main__':
    unittest.main()
