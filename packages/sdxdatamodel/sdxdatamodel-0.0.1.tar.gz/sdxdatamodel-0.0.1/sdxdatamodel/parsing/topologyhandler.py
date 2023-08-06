import json
from sdxdatamodel.models.topology import Topology
from .exceptions import MissingAttributeException

MANIFEST_FILE = None

class TopologyHandler():

    """"
    Handler for parsing the topology descritpion in json 
    """

    def __init__(self,topology_filename=None):
        super().__init__()
        self.topology_file = topology_filename
        self.topology = None

    def topology_file_name(self,topology_filename=None):
        self.topology_file = topology_filename

    def import_topology(self):
        try:
            with open(self.topology_file, 'r', encoding='utf-8') as data_file:
                data = json.load(data_file)
                self.import_topology_data(data)
        except (IOError, FileNotFoundError) as e:
            print(e)

    def import_topology_data(self, data):
        try:
            id = data['id']
            name=data['name']
            service = None
            if 'domain_service' in data.keys():
                service=data['domain_service']
            version=data['version']
            time_stamp=data['time_stamp']
            nodes=data['nodes']
            links=data['links']
        except KeyError as e:
            raise MissingAttributeException(e.args[0],e.args[0])

        self.topology=Topology(id=id, name=name, domain_service = service, version=version, time_stamp=time_stamp, nodes=nodes, links=links)

        return self.topology

    def get_topology(self):
        return self.topology
