import json
from sdxdatamodel.models.link import Link
from .exceptions import MissingAttributeException

class LinkHandler():

    """"
    Handler for parsing the connection request descritpion in json 
    """

    def __init__(self):
        super().__init__()
        self.link = None

    def import_link_data(self, data):
        try:
            id = data['id']
            name=data['name']
            short_name=data['short_name']
            ports=data['ports']
            
            n=None;timestamp=None;t_b=None;a_b=None;latency=None;p_l=None;p_a=None;avai=None;m_p=None
            if 'nni' in data.keys():
                n=bool(data['nni']) 
            if 'time_stamp' in data.keys():
                timestamp=data['time_stamp']
            if 'bandwidth' in data.keys():
                t_b=data['bandwidth']
            if 'residual_bandwidth' in data.keys():
                a_b=data['residual_bandwidth']
            if 'latency' in data.keys():
                latency=data['latency']
            if 'packet_loss' in data.keys():
                p_l=data['packet_loss']
            if 'private_attributes' in data.keys():
                p_a=data['private_attributes']
            if 'availability' in data.keys():
                avai=data['availability']
            if 'measurement_period' in data.keys():
                m_p=data['measurement_period']
        except KeyError as e:
            raise MissingAttributeException(e.args[0],e.args[0])

        link=Link(id=id, name=name, short_name=short_name, ports=ports, nni=n, bandwidth=t_b, residual_bandwidth=a_b, 
            latency=latency, packet_loss=p_l, availability=avai, private_attributes=p_a, time_stamp=timestamp, measurement_period=m_p)

        return link
    
    def import_link(self,file):
        with open(file, 'r', encoding='utf-8') as data_file:
            data = json.load(data_file)
            self.link = self.import_link_data(data)

    def get_link(self):
        return self.link
