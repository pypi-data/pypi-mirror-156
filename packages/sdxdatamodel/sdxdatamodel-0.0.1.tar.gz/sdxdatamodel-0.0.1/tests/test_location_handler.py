import unittest

from sdxdatamodel.parsing.locationhandler import LocationHandler
from sdxdatamodel.parsing.exceptions import DataModelException

location = './tests/data/location.json'

class TestPortHandler(unittest.TestCase):

    def setUp(self):
        self.handler = LocationHandler()  # noqa: E501
    def tearDown(self):
        pass

    def testImportLocation(self):
        try:
            print("Test Location")
            self.handler.import_location(location)
            print(self.handler.location)
        except DataModelException as e:
            print(e)
            return False      
        return True

if __name__ == '__main__':
    unittest.main()