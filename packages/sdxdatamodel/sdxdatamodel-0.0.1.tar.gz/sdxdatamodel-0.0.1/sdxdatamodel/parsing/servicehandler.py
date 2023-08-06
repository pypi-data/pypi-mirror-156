import json
from sdxdatamodel.models.service import Service
from .exceptions import MissingAttributeException

class ServiceHandler():

    """"
    Handler for parsing the connection request descritpion in json 
    """

    def __init__(self):
        super().__init__()
        self.service = None

    def import_service_data(self, data):
        try:
            owner=data['owner']
            m_c=None;p_s=None;p_url=None;vendor=None;p_a=None
            if 'monitoring_capability' in data.keys():
                m_c = data['monitoring_capability']
            if 'provisioning_system' in data.keys():
                p_s=data['provisioning_system']
            if 'provisioning_url' in data.keys():
                p_url=data['provisioning_url']
            if 'vendor' in data.keys():
                vendor=data['vendor']
            if 'private_attributes' in data.keys():
                p_a=data['private_attributes']
        except KeyError as e:
            raise MissingAttributeException(e.args[0],e.args[0])

        service=Service(monitoring_capability=m_c, owner=owner, private_attributes=p_a, provisioning_system=p_s, provisioning_url=p_url, vendor=vendor)
        
        return service
    
    def import_service(self,file):
        with open(file, 'r', encoding='utf-8') as data_file:
            data = json.load(data_file)
            self.service = self.import_service_data(data)

    def get_service(self):
        return self.service
