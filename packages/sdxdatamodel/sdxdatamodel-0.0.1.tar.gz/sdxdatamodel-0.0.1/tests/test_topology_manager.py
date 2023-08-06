import unittest
import json
from networkx import MultiGraph, Graph
import matplotlib.pyplot as plt
import networkx as nx

from sdxdatamodel import parsing
from sdxdatamodel import topologymanager

from sdxdatamodel import validation
from sdxdatamodel.validation.topologyvalidator import TopologyValidator
from sdxdatamodel.parsing.topologyhandler import TopologyHandler
from sdxdatamodel.topologymanager.manager import TopologyManager
from sdxdatamodel.topologymanager.grenmlconverter import GrenmlConverter
from sdxdatamodel.parsing.exceptions import DataModelException


TOPOLOGY_AMLIGHT = './tests/data/amlight.json'
TOPOLOGY_SAX = './tests/data/sax.json'
TOPOLOGY_ZAOXI = './tests/data/zaoxi.json'

TOPOLOGY_png = "./tests/data/sdx.png"
TOPOLOGY_IN = "./tests/data/sdx.json"
TOPOLOGY_OUT = "./tests/data/sdx-out.json"

topology_file_list_3 = [TOPOLOGY_AMLIGHT,TOPOLOGY_ZAOXI,TOPOLOGY_SAX]
topology_file_list_update = [TOPOLOGY_ZAOXI]

link_id = "urn:ogf:network:sdx:link:amlight:A1-B2"
inter_link_id = "urn:ogf:network:sdx:link:nni:Miami-Sanpaolo"

class TestTopologyManager(unittest.TestCase):

    def setUp(self):
        self.manager = TopologyManager()  # noqa: E501

    def tearDown(self):
        pass

    def testMergeTopology(self):
        print("Test Topology Merge!")
        try:
            for topology_file in topology_file_list_3:
                with open(topology_file, 'r', encoding='utf-8') as data_file:
                    data = json.load(data_file)
                print("Adding Topology:" + topology_file)
                self.manager.add_topology(data)
            with open(TOPOLOGY_OUT, 'w') as t_file:
                json.dump(self.manager.topology.to_dict(), t_file, indent=4)    

        except DataModelException as e:
            print(e)
            return False      
        return True

    def testUpdateTopology(self):
        print("Test Topology Update!")
        try:
            self.testMergeTopology()
            for topology_file in topology_file_list_update:
                with open(topology_file, 'r', encoding='utf-8') as data_file:
                    data = json.load(data_file)
                print("Updating Topology:" + topology_file)
                self.manager.update_topology(data) 

            with open(TOPOLOGY_OUT, 'w') as t_file:
                json.dump(self.manager.topology.to_dict(), t_file, indent=4)   
            graph = self.manager.generate_graph()
            #pos = nx.spring_layout(graph, seed=225)  # Seed for reproducible layout
            nx.draw(graph,with_labels = True)
            plt.savefig(TOPOLOGY_png)  
        except DataModelException as e:
            print(e)
            return False      
        return True

    def testGrenmlConverter(self):
        try:
            print("Test Topology GRENML Converter")
            self.testMergeTopology()
            converter = GrenmlConverter(self.manager.get_topology())
            converter.read_topology()
            print(converter.get_xml_str())
        except DataModelException as e:
            print(e)
            return False      
        return True

    def testGenerateGraph(self):
        try:
            print("Test Topology Graph")
            self.testMergeTopology()
            graph = self.manager.generate_graph()
            #pos = nx.spring_layout(graph, seed=225)  # Seed for reproducible layout
            nx.draw(graph,with_labels = True)
            plt.savefig(TOPOLOGY_png)
        except DataModelException as e:
            print(e)
            return False      
        return True

    def testLinkPropertyUpdate(self):
        print("Test Topology Link Property Update!")
        try:
            self.testMergeTopology()
            self.manager.update_link_property(link_id,'latency',8)
            self.manager.update_link_property(inter_link_id,'latency',8)
            with open(TOPOLOGY_OUT, 'w') as t_file:
                json.dump(self.manager.topology.to_dict(), t_file, indent=4)
        except DataModelException as e:
            print(e)
            return False      
        return True

    def testLinkPropertyUpdateJson(self):
        print("Test Topology JSON Link Property Update!")
        try:
            with open(TOPOLOGY_IN, 'r', encoding='utf-8') as data_file:
                data = json.load(data_file)
                self.manager.update_element_property_json(data,'links',link_id,'latency',20)
            with open(TOPOLOGY_OUT, 'w') as t_file:
                json.dump(data, t_file, indent=4)
        except DataModelException as e:
            print(e)
            return False      
        return True
        


if __name__ == '__main__':
    unittest.main()
