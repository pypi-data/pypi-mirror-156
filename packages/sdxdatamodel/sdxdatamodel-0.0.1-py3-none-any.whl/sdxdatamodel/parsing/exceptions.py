class DataModelException(Exception):
    """
    Base exception for topology data model functions
    """
    pass

class MissingAttributeException(DataModelException):
    """
    A required attribute could not be found when parsing a model element in JSON
    """

    def __init__(self, attribute_name, expected_attribute):
        self.attribute_name = attribute_name
        self.expected_attribute = expected_attribute

    def __str__(self):
        return ("Missing attribute {} while parsing <{}>").format(
            self.expected_attribute,
            self.attribute_name,
        )

class GraphNotConnectedException(DataModelException):
    """
    The topology is not connected
    """

    def __init__(self,graph, connectivity):
        self.graph = graph
        self.connectivity = connectivity

    def __str__(self):
        return ("Graph <{}> is Not {} Connected ").format(
            self.graph,
            self.connectivity,
        )

