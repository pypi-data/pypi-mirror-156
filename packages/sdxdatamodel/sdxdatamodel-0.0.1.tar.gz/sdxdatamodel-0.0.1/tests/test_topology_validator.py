import unittest

import sdxdatamodel.parsing

from sdxdatamodel.validation.topologyvalidator import TopologyValidator
from sdxdatamodel.parsing.topologyhandler import TopologyHandler
from sdxdatamodel.parsing.exceptions import DataModelException

TOPOLOGY_AMLIGHT = './tests/data/amlight.json'
TOPOLOGY_AMPATH = './tests/data/ampath.json'
TOPOLOGY_SAX = './tests/data/sax.json'
TOPOLOGY_ZAOXI = './tests/data/zaoxi.json'

class TestTopologyValidator(unittest.TestCase):

    def setUp(self):
        self.handler = TopologyHandler(TOPOLOGY_ZAOXI)
        self.validator = TopologyValidator()  

    def tearDown(self):
        pass

    def testTopology(self):
        try:
            print("Import Topology:")
            self.handler.import_topology()
            self.validator.set_topology(self.handler.topology)
            self.validator.is_valid()
            print(self.handler.topology)
        except DataModelException as e:
            print(e)
            return False
        return True

if __name__ == '__main__':
    unittest.main()