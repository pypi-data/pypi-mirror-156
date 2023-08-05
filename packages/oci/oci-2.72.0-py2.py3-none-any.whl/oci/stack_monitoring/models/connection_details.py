# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class ConnectionDetails(object):
    """
    Connection details to connect to the database. HostName, protocol, and port should be specified.
    """

    #: A constant which can be used with the protocol property of a ConnectionDetails.
    #: This constant has a value of "TCP"
    PROTOCOL_TCP = "TCP"

    #: A constant which can be used with the protocol property of a ConnectionDetails.
    #: This constant has a value of "TCPS"
    PROTOCOL_TCPS = "TCPS"

    def __init__(self, **kwargs):
        """
        Initializes a new ConnectionDetails object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param protocol:
            The value to assign to the protocol property of this ConnectionDetails.
            Allowed values for this property are: "TCP", "TCPS", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type protocol: str

        :param port:
            The value to assign to the port property of this ConnectionDetails.
        :type port: int

        :param connector_id:
            The value to assign to the connector_id property of this ConnectionDetails.
        :type connector_id: str

        :param service_name:
            The value to assign to the service_name property of this ConnectionDetails.
        :type service_name: str

        :param db_unique_name:
            The value to assign to the db_unique_name property of this ConnectionDetails.
        :type db_unique_name: str

        :param db_id:
            The value to assign to the db_id property of this ConnectionDetails.
        :type db_id: str

        """
        self.swagger_types = {
            'protocol': 'str',
            'port': 'int',
            'connector_id': 'str',
            'service_name': 'str',
            'db_unique_name': 'str',
            'db_id': 'str'
        }

        self.attribute_map = {
            'protocol': 'protocol',
            'port': 'port',
            'connector_id': 'connectorId',
            'service_name': 'serviceName',
            'db_unique_name': 'dbUniqueName',
            'db_id': 'dbId'
        }

        self._protocol = None
        self._port = None
        self._connector_id = None
        self._service_name = None
        self._db_unique_name = None
        self._db_id = None

    @property
    def protocol(self):
        """
        **[Required]** Gets the protocol of this ConnectionDetails.
        Protocol used in DB connection string when connecting to external database service.

        Allowed values for this property are: "TCP", "TCPS", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The protocol of this ConnectionDetails.
        :rtype: str
        """
        return self._protocol

    @protocol.setter
    def protocol(self, protocol):
        """
        Sets the protocol of this ConnectionDetails.
        Protocol used in DB connection string when connecting to external database service.


        :param protocol: The protocol of this ConnectionDetails.
        :type: str
        """
        allowed_values = ["TCP", "TCPS"]
        if not value_allowed_none_or_none_sentinel(protocol, allowed_values):
            protocol = 'UNKNOWN_ENUM_VALUE'
        self._protocol = protocol

    @property
    def port(self):
        """
        **[Required]** Gets the port of this ConnectionDetails.
        Listener Port number used for connection requests.


        :return: The port of this ConnectionDetails.
        :rtype: int
        """
        return self._port

    @port.setter
    def port(self, port):
        """
        Sets the port of this ConnectionDetails.
        Listener Port number used for connection requests.


        :param port: The port of this ConnectionDetails.
        :type: int
        """
        self._port = port

    @property
    def connector_id(self):
        """
        Gets the connector_id of this ConnectionDetails.
        Database connector Identifier


        :return: The connector_id of this ConnectionDetails.
        :rtype: str
        """
        return self._connector_id

    @connector_id.setter
    def connector_id(self, connector_id):
        """
        Sets the connector_id of this ConnectionDetails.
        Database connector Identifier


        :param connector_id: The connector_id of this ConnectionDetails.
        :type: str
        """
        self._connector_id = connector_id

    @property
    def service_name(self):
        """
        **[Required]** Gets the service_name of this ConnectionDetails.
        Service name used for connection requests.


        :return: The service_name of this ConnectionDetails.
        :rtype: str
        """
        return self._service_name

    @service_name.setter
    def service_name(self, service_name):
        """
        Sets the service_name of this ConnectionDetails.
        Service name used for connection requests.


        :param service_name: The service_name of this ConnectionDetails.
        :type: str
        """
        self._service_name = service_name

    @property
    def db_unique_name(self):
        """
        Gets the db_unique_name of this ConnectionDetails.
        UniqueName used for database connection requests.


        :return: The db_unique_name of this ConnectionDetails.
        :rtype: str
        """
        return self._db_unique_name

    @db_unique_name.setter
    def db_unique_name(self, db_unique_name):
        """
        Sets the db_unique_name of this ConnectionDetails.
        UniqueName used for database connection requests.


        :param db_unique_name: The db_unique_name of this ConnectionDetails.
        :type: str
        """
        self._db_unique_name = db_unique_name

    @property
    def db_id(self):
        """
        Gets the db_id of this ConnectionDetails.
        dbId of the database


        :return: The db_id of this ConnectionDetails.
        :rtype: str
        """
        return self._db_id

    @db_id.setter
    def db_id(self, db_id):
        """
        Sets the db_id of this ConnectionDetails.
        dbId of the database


        :param db_id: The db_id of this ConnectionDetails.
        :type: str
        """
        self._db_id = db_id

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
