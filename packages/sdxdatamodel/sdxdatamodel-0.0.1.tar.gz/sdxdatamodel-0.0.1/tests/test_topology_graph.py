import unittest

from networkx import MultiGraph, Graph
import matplotlib.pyplot as plt
import networkx as nx

from sdxdatamodel.validation.topologyvalidator import TopologyValidator
from sdxdatamodel.parsing.topologyhandler import TopologyHandler
from sdxdatamodel.topologymanager.manager import TopologyManager
from sdxdatamodel.topologymanager.grenmlconverter import GrenmlConverter
from sdxdatamodel.parsing.exceptions import DataModelException


TOPOLOGY_AMLIGHT = './tests/data/amlight.json'
TOPOLOGY_SAX = './tests/data/sax.json'
TOPOLOGY_ZAOXI = './tests/data/zaoxi.json'

class TestTopologyGrpah(unittest.TestCase):

    def setUp(self):
        self.manager = TopologyManager()  # noqa: E501
        self.handler = self.manager.handler
        self.handler.topology_file_name(TOPOLOGY_AMLIGHT)
        self.handler.import_topology()
        self.manager.set_topology(self.handler.get_topology())

    def tearDown(self):
        pass

    def testGenerateGraph(self):
        try:
            print("Test Topology Graph")
            graph = self.manager.generate_graph()
            #pos = nx.spring_layout(graph, seed=225)  # Seed for reproducible layout
            nx.draw(graph)
            plt.savefig("./tests/data/amlight.png")
        except DataModelException as e:
            print(e)
            return False      
        return True