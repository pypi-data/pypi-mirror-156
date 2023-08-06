import json
from sdxdatamodel.models.location import Location
from .exceptions import MissingAttributeException

class LocationHandler():

    """"
    Handler for parsing the connection request descritpion in json 
    """

    def __init__(self):
        super().__init__()
        self.location = None

    def import_location_data(self, data):
        try:
            addr=None;long=None;lat=None
            if 'address' in data.keys():
                addr = data['address']
            if 'latitude' in data.keys():
                long=data['latitude']
            if 'longitude' in data.keys():
                lat=data['longitude']
        except KeyError as e:
            raise MissingAttributeException(e.args[0],e.args[0])

        location=Location(address=addr, longitude=long, latitude=lat)
        
        return location
    
    def import_location(self,file):
        with open(file, 'r', encoding='utf-8') as data_file:
            data = json.load(data_file)
            self.location = self.import_location_data(data)

    def get_location(self):
        return self.location
