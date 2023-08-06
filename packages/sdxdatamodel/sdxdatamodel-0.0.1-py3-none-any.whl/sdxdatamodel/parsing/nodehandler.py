import json
from sdxdatamodel.models.node import Node
from .exceptions import MissingAttributeException

class NodeHandler():

    """"
    Handler for parsing the connection request descritpion in json 
    """

    def __init__(self):
        super().__init__()
        self.node = None

    def import_node_data(self, data):
        try:
            id = data['id']
            name=data['name']
            short_name=data['short_name']
            location=data['location']
            ports=data['ports']
            p_a=None
            if 'private_attributes' in data.keys():
                p_a=data['private_attributes']
        except KeyError as e:
            raise MissingAttributeException(e.args[0],e.args[0])

        node=Node(id=id, name=name, short_name=short_name, location=location, ports=ports, private_attributes=p_a)

        return node
    
    def import_node(self,file):
        with open(file, 'r', encoding='utf-8') as data_file:
            data = json.load(data_file)
            self.node = self.import_node_data(data)

    def get_node(self):
        return self.node
