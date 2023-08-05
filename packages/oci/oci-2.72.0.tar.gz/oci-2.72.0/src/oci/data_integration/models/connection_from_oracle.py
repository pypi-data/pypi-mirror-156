# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

from .connection import Connection
from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class ConnectionFromOracle(Connection):
    """
    The connection details for an Oracle Database data asset.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new ConnectionFromOracle object with values from keyword arguments. The default value of the :py:attr:`~oci.data_integration.models.ConnectionFromOracle.model_type` attribute
        of this class is ``ORACLEDB_CONNECTION`` and it should not be changed.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param model_type:
            The value to assign to the model_type property of this ConnectionFromOracle.
            Allowed values for this property are: "ORACLE_ADWC_CONNECTION", "ORACLE_ATP_CONNECTION", "ORACLE_OBJECT_STORAGE_CONNECTION", "ORACLEDB_CONNECTION", "MYSQL_CONNECTION", "GENERIC_JDBC_CONNECTION", "BICC_CONNECTION", "AMAZON_S3_CONNECTION", "BIP_CONNECTION"
        :type model_type: str

        :param key:
            The value to assign to the key property of this ConnectionFromOracle.
        :type key: str

        :param model_version:
            The value to assign to the model_version property of this ConnectionFromOracle.
        :type model_version: str

        :param parent_ref:
            The value to assign to the parent_ref property of this ConnectionFromOracle.
        :type parent_ref: oci.data_integration.models.ParentReference

        :param name:
            The value to assign to the name property of this ConnectionFromOracle.
        :type name: str

        :param description:
            The value to assign to the description property of this ConnectionFromOracle.
        :type description: str

        :param object_version:
            The value to assign to the object_version property of this ConnectionFromOracle.
        :type object_version: int

        :param object_status:
            The value to assign to the object_status property of this ConnectionFromOracle.
        :type object_status: int

        :param identifier:
            The value to assign to the identifier property of this ConnectionFromOracle.
        :type identifier: str

        :param primary_schema:
            The value to assign to the primary_schema property of this ConnectionFromOracle.
        :type primary_schema: oci.data_integration.models.Schema

        :param connection_properties:
            The value to assign to the connection_properties property of this ConnectionFromOracle.
        :type connection_properties: list[oci.data_integration.models.ConnectionProperty]

        :param is_default:
            The value to assign to the is_default property of this ConnectionFromOracle.
        :type is_default: bool

        :param metadata:
            The value to assign to the metadata property of this ConnectionFromOracle.
        :type metadata: oci.data_integration.models.ObjectMetadata

        :param key_map:
            The value to assign to the key_map property of this ConnectionFromOracle.
        :type key_map: dict(str, str)

        :param username:
            The value to assign to the username property of this ConnectionFromOracle.
        :type username: str

        :param password:
            The value to assign to the password property of this ConnectionFromOracle.
        :type password: str

        :param password_secret:
            The value to assign to the password_secret property of this ConnectionFromOracle.
        :type password_secret: oci.data_integration.models.SensitiveAttribute

        """
        self.swagger_types = {
            'model_type': 'str',
            'key': 'str',
            'model_version': 'str',
            'parent_ref': 'ParentReference',
            'name': 'str',
            'description': 'str',
            'object_version': 'int',
            'object_status': 'int',
            'identifier': 'str',
            'primary_schema': 'Schema',
            'connection_properties': 'list[ConnectionProperty]',
            'is_default': 'bool',
            'metadata': 'ObjectMetadata',
            'key_map': 'dict(str, str)',
            'username': 'str',
            'password': 'str',
            'password_secret': 'SensitiveAttribute'
        }

        self.attribute_map = {
            'model_type': 'modelType',
            'key': 'key',
            'model_version': 'modelVersion',
            'parent_ref': 'parentRef',
            'name': 'name',
            'description': 'description',
            'object_version': 'objectVersion',
            'object_status': 'objectStatus',
            'identifier': 'identifier',
            'primary_schema': 'primarySchema',
            'connection_properties': 'connectionProperties',
            'is_default': 'isDefault',
            'metadata': 'metadata',
            'key_map': 'keyMap',
            'username': 'username',
            'password': 'password',
            'password_secret': 'passwordSecret'
        }

        self._model_type = None
        self._key = None
        self._model_version = None
        self._parent_ref = None
        self._name = None
        self._description = None
        self._object_version = None
        self._object_status = None
        self._identifier = None
        self._primary_schema = None
        self._connection_properties = None
        self._is_default = None
        self._metadata = None
        self._key_map = None
        self._username = None
        self._password = None
        self._password_secret = None
        self._model_type = 'ORACLEDB_CONNECTION'

    @property
    def username(self):
        """
        Gets the username of this ConnectionFromOracle.
        The user name for the connection.


        :return: The username of this ConnectionFromOracle.
        :rtype: str
        """
        return self._username

    @username.setter
    def username(self, username):
        """
        Sets the username of this ConnectionFromOracle.
        The user name for the connection.


        :param username: The username of this ConnectionFromOracle.
        :type: str
        """
        self._username = username

    @property
    def password(self):
        """
        Gets the password of this ConnectionFromOracle.
        The password for the connection.


        :return: The password of this ConnectionFromOracle.
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """
        Sets the password of this ConnectionFromOracle.
        The password for the connection.


        :param password: The password of this ConnectionFromOracle.
        :type: str
        """
        self._password = password

    @property
    def password_secret(self):
        """
        Gets the password_secret of this ConnectionFromOracle.

        :return: The password_secret of this ConnectionFromOracle.
        :rtype: oci.data_integration.models.SensitiveAttribute
        """
        return self._password_secret

    @password_secret.setter
    def password_secret(self, password_secret):
        """
        Sets the password_secret of this ConnectionFromOracle.

        :param password_secret: The password_secret of this ConnectionFromOracle.
        :type: oci.data_integration.models.SensitiveAttribute
        """
        self._password_secret = password_secret

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
