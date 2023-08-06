import unittest

#import parsing

from sdxdatamodel.parsing.connectionhandler import ConnectionHandler
from sdxdatamodel.parsing.exceptions import DataModelException

CONNECTION_P2P = './tests/data/p2p.json'
#CONNECTION_P2P = './tests/data/test_connection.json'

class TestConnectionHandler(unittest.TestCase):

    def setUp(self):
        self.handler = ConnectionHandler()  # noqa: E501
    def tearDown(self):
        pass

    def testImportConnection(self):
        try:
            print("Test Connection")
            self.handler.import_connection(CONNECTION_P2P)
            print(self.handler.connection)
        except DataModelException as e:
            print(e)
            return False      
        return True

if __name__ == '__main__':
    unittest.main()