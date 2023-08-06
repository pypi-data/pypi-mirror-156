import unittest

from sdxdatamodel.parsing.linkhandler import LinkHandler
from sdxdatamodel.parsing.exceptions import DataModelException

link = './tests/data/link.json'

class TestLinkHandler(unittest.TestCase):

    def setUp(self):
        self.handler = LinkHandler()  # noqa: E501
    def tearDown(self):
        pass

    def testImportLink(self):
        try:
            print("Test Link")
            self.handler.import_link(link)
            print(self.handler.link)
        except DataModelException as e:
            print(e)
            return False      
        return True

if __name__ == '__main__':
    unittest.main()