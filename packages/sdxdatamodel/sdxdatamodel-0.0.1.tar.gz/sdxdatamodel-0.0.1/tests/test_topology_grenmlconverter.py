import unittest

import sdxdatamodel.parsing
import sdxdatamodel.topologymanager

from sdxdatamodel.validation.topologyvalidator import TopologyValidator
from sdxdatamodel.parsing.topologyhandler import TopologyHandler
from sdxdatamodel.topologymanager.manager import TopologyManager
from sdxdatamodel.topologymanager.grenmlconverter import GrenmlConverter
from sdxdatamodel.parsing.exceptions import DataModelException


TOPOLOGY_AMLIGHT = './tests/data/amlight.json'

class TestTopologyGRENMLConverter(unittest.TestCase):

    def setUp(self):
        self.manager = TopologyManager()  # noqa: E501
        self.handler = self.manager.handler
        self.handler.topology_file_name(TOPOLOGY_AMLIGHT)
        self.handler.import_topology()

    def tearDown(self):
        pass

    def testGrenmlConverter(self):
        try:
            print("Test Topology Converter")
            print(self.handler.topology)
            converter = GrenmlConverter(self.handler.topology)
            converter.read_topology()
            print(converter.get_xml_str())
        except DataModelException as e:
            print(e)
            return False      
        return True