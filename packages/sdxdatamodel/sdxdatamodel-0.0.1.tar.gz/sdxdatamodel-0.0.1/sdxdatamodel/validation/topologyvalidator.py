"""""
--------------------------------------------------------------------
Synopsis: A validation class to evaluate that the supplied Topology object contains expected data format
"""
from collections.abc import Iterable
from re import match

from sdxdatamodel import *
from sdxdatamodel.models import *

from sdxdatamodel.models.topology import SDX_INSTITUTION_ID, Topology
from sdxdatamodel.models.service import Service 
from sdxdatamodel.models.node import Node 
from sdxdatamodel.models.link import Link
from sdxdatamodel.models.port import Port
from sdxdatamodel.models.location import Location


ISO_FORMAT = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[-+]\d{2}:\d{2}'

class TopologyValidator:
    """
    The validation class made to validate a Topology
    """
    def __init__(self):
        self.topology = None
    
    def get_topology(self):
        return self.topology
   
    def set_topology(self, topology):
        if not isinstance(topology, Topology):
            raise ValueError('The Validator must be passed a Topology object')
        self.topology = topology
    
    def is_valid(self):
        errors = self.validate(self.topology, raise_error=False)
        for error in errors:
            print(error)
        return not bool(errors)
    def validate(self, topology=None, raise_error=True):
        if not topology and self.topology:
            topology = self.topology
        errors = self._validate_topology(topology)
        if errors and raise_error:
            raise ValueError('\n'.join(errors))
        return errors
    def _validate_topology(self, topology: Topology):
        """
        Validate that the topology provided meets the JSON schema.
        A topology must have the following:
         - It must meet object standard
         - It must have the default fields: id, name, version, time_stamp, nodes, and links
         - It must have a Primary owner assigned
         - It must have its primary owner in its institution list
         - It must have the global institution in the institution list
        :param topology: The topology being evaluated
        :return: A list of any issues in the data.
        """
        errors = []
        errors += self._validate_object_defaults(topology)

        if SDX_INSTITUTION_ID not in topology.id:
            errors.append('Global Institution must be in Topology {}'.format(topology.id))

        service = topology.get_domain_service()
        if service is not None:
            errors += self._validate_service(service, topology)
        for node in topology.get_nodes():
            errors += self._validate_node(node, topology)
        for link in topology.get_links():
            errors += self._validate_link(link, topology)

        return errors

    def _validate_service(self, service: Service, topology: Topology):
        """
        Validate that the institution provided meets the XSD standards.
        A institution must have the following:
         - It must meet object default standards.
         - It's Location values are valid
         - The Institution Type must be in the list of valid Institution types
        :param institution: The Institution being evaluated.
        :param topology: The Parent Topology.
        :return: A list of any issues in the data.
        """
        errors = []
        errors += self._validate_object_defaults(service)

        return errors

    def _validate_version(self, version, time_stamp, topology: Topology):
        """
        Validate that the version and time_stamp provided meets the ISO standards.
         - It must meet object default standards.
         - It's Location values are valid
         - The Institution Type must be in the list of valid Institution types
        :param version: The topology version.
        :param time_stamp: The topology time stamp.
        :param topology: The Parent Topology.
        :return: A list of any issues in the data.
        """     
        errors = []  
        if version:
            if not isinstance(version, str):
                errors.append(
                    '{} Version must be a String'.format(
                        topology.id,
                    )
                )
            elif not match(ISO_FORMAT, version):
                errors.append(
                    '{} Version must be datetime ISO format'.format(
                        topology.id,
                    )
                )

        if not match(ISO_FORMAT, time_stamp):
            errors.append(
                '{} time_stamp needs to be in full ISO format'.format(
                    time_stamp,
                )
            )

        return errors

    def _validate_node(self, node: Node, topology: Topology):
        """
        Validate that the node provided meets the XSD standards.
        A node must have the following:
         - It must meet object default standards.
         - It's Location values are valid
        :param node: The Node being evaluated.
        :param topology: The Parent Topology.
        :return: A list of any issues in the data.
        """
        errors = []

        errors += self._validate_object_defaults(node)
        errors += self._validate_location(node.get_location())

        return errors

    def _validate_link(self, link: Link, topology: Topology):
        """
        Validate that the link provided meets the XSD standards.
        A link must have the following:
         - It must meet object default standards.
         - A link can only connect to 2 nodes
         - The nodes that a link is connected to must be in the parent Topology's nodes list
        :param link: The Link being evaluated.
        :param topology: The Parent Topology.
        :return: A list of any issues in the data.
        """
        errors = []
        errors += self._validate_object_defaults(link)

        if len(link._ports) != 2:
            errors.append(
                'Link {} must connect between 2 ports. Currently {}'.format(
                    link.id, str(link._ports)
                )
            )
        for port in link._ports:
            if not isinstance(port, str):
                errors.append(
                    'Link {} Port {} should be a string. Not {}'.format(
                        link.id, port, port.__class__.__name__
                    )
                )
        #TODO: Check ports are in the current topology
        
        return errors

    def _validate_object_defaults(self, sdx_object):
        """
        Validate that the object provided default fields meets the XSD standards.
        The object must have the following:
         - The object must have an ID
         - The object ID must be a string
         - The object must have a name
         - The object name must be a string
         - If the object has a short name, it must be a string
         - If the object has a version, it must be a string in ISO format
         - All the additional properties on the object are proper
        :param sdx_object: The sdx Model Object being evaluated.
        :return: A list of any issues in the data.
        """
        errors = []
        if not sdx_object._id:
            errors.append('{} must have an ID'.format(sdx_object.__class__.__name__))
        if not isinstance(sdx_object._id, str):
            errors.append('{} ID must be a string'.format(sdx_object.__class__.__name__))
        if not sdx_object._name:
            errors.append(
                '{} {} must have a name'.format(
                    sdx_object.__class__.__name__, sdx_object._name,
                )
            )
        if not isinstance(sdx_object._name, str):
            errors.append(
                '{} {} name must be a String'.format(
                    sdx_object.__class__.__name__, sdx_object._name,
                )
            )

        return errors

    def _validate_location(self, location: Location, enforce_coordinates=True):
        """
        Validate that the object location fields meets the XSD standards.
        The location must have the following:
         - A location must have a longitude
         - A location's longitude muse be a floating point value
         - A location's longitude must be between -180 and -180
         - A location must have a latitude
         - A location must be a floating point value
         - A location's latitude must be between -90 and 90
         - A location's altitude must be a floating point value
         - A location's UN/LOCODE must be a string value
         - A location's address must be a string or a list of strings
        :param location: The Location Object being evaluated.
        :param enforce_coordinates: A boolean determining if longitude and latitude should be enforced
        :return: A list of any issues in the data.
        """
        errors = []
        if location.longitude is None and enforce_coordinates:
            errors.append(
                '{} {} Longitude must be set to a value'.format(
                    location.__class__.__name__, location.id,
                )
            )
        try:
            if location.longitude is not None:
                if not -180 <= float(location.longitude) <= 180:
                    errors.append(
                        '{} {} Longitude must be a value that is between -180 and 180'.format(
                            location.__class__.__name__, location.id,
                        )
                    )
        except ValueError:
            errors.append(
                '{} {} Longitude must be a value that coordinates to a Floating point value'.format(
                    location.__class__.__name__, location.id,
                )
            )

        if location.latitude is None and enforce_coordinates:
            errors.append(
                '{} {} Latitude must be set to a value'.format(
                    location.__class__.__name__, location.id
                )
            )
        try:
            if location.latitude is not None:
                if not -90 <= float(location.latitude) <= 90:
                    errors.append(
                        '{} {} Latitude must be a value that is between -90 and 90'.format(
                            location.__class__.__name__, location.id,
                        )
                    )
        except ValueError:
            errors.append(
                '{} {} Latitude must be a value that coordinates to a Floating point value'.format(
                    location.__class__.__name__, location.id,
                )
            )

        try:
            if location.latitude:
                float(location.latitude)
        except ValueError:
            errors.append(
                '{} {} Altitude must be a value that coordinates to a Floating point value'.format(
                    location.__class__.__name__, location.id,
                )
            )

        if not location.address:
            errors.append(
                '{} {} Address must exist'.format(
                    location.__class__.__name__, location._id
                )
            )
        if not type(location.address) == str:
            errors.append(
                '{} {} Address {} must be a string'.format(
                    location.__class__.__name__, location._id, location.address
                )
            )

        return errors