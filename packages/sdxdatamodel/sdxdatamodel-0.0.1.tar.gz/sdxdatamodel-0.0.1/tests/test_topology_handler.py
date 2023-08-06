import unittest

from sdxdatamodel.parsing.topologyhandler import TopologyHandler
from sdxdatamodel.parsing.exceptions import DataModelException

TOPOLOGY_AMLIGHT = './tests/data/amlight.json'

class TestTopologyHandler(unittest.TestCase):

    def setUp(self):
        self.handler = TopologyHandler(TOPOLOGY_AMLIGHT) 
        self.handler.import_topology()
    def tearDown(self):
        pass

    def testImportTopology(self):
        try:
            print("Test Topology")
            print(self.handler.topology)
        except DataModelException as e:
            print(e)
            return False      
        return True

    def testImportTopologyNodes(self):
        print("Test Nodes: at least one:")
        nodes=self.handler.topology.nodes
        if nodes==None or len(nodes)==0:
            print("Nodes are empty")
            return False
        print(nodes[0])  
        return True

    def testImportTopologyLinks(self):
        print("Test Links: at least one")
        links=self.handler.topology.links
        if links==None or len(links)==0:
            print("Links are empty")
            return False
        print(links[0])  
        return True

if __name__ == '__main__':
    unittest.main()