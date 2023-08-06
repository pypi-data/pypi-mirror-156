import unittest

from sdxdatamodel.parsing.nodehandler import NodeHandler
from sdxdatamodel.parsing.exceptions import DataModelException

node = './tests/data/node.json'

class TestNodeHandler(unittest.TestCase):

    def setUp(self):
        self.handler = NodeHandler()  # noqa: E501
    def tearDown(self):
        pass

    def testImportNode(self):
        try:
            print("Test node")
            self.handler.import_node(node)
            print(self.handler.node)
        except DataModelException as e:
            print(e)
            return False      
        return True

if __name__ == '__main__':
    unittest.main()