import unittest
import json
from networkx import MultiGraph, Graph
import networkx as nx

from sdxdatamodel import parsing
from sdxdatamodel import topologymanager

from sdxdatamodel import validation
from sdxdatamodel.validation.topologyvalidator import TopologyValidator
from sdxdatamodel.parsing.topologyhandler import TopologyHandler
from sdxdatamodel.topologymanager.manager import TopologyManager
from sdxdatamodel.topologymanager.temanager import TEManager
from sdxdatamodel.parsing.exceptions import DataModelException

TOPOLOGY = "./tests/data/sdx.json"
CONNECTION = "./tests/data/test_request.json"

class TestTopologyManager(unittest.TestCase):

    def setUp(self):
        with open(TOPOLOGY, 'r', encoding='utf-8') as t:
            topology_data = json.load(t)
        with open(CONNECTION, 'r', encoding='utf-8') as c:
            connection_data = json.load(c)
            
        self.temanager = TEManager(topology_data, connection_data)

    def tearDown(self):
        pass

    def testGenerateSolverInput(self):
        print("generate networkx graph of the topology")
        graph=self.temanager.graph
        
        print(graph.nodes[0])
        print(graph.edges)

        print("Test Convert Connection To Topology")
        connection=self.temanager.generate_connection_te()
        print(connection)

