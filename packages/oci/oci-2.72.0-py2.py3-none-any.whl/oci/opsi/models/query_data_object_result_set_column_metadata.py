# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class QueryDataObjectResultSetColumnMetadata(object):
    """
    Metadata of a column in a data object query result set.
    """

    #: A constant which can be used with the data_type_name property of a QueryDataObjectResultSetColumnMetadata.
    #: This constant has a value of "NUMBER"
    DATA_TYPE_NAME_NUMBER = "NUMBER"

    #: A constant which can be used with the data_type_name property of a QueryDataObjectResultSetColumnMetadata.
    #: This constant has a value of "TIMESTAMP"
    DATA_TYPE_NAME_TIMESTAMP = "TIMESTAMP"

    #: A constant which can be used with the data_type_name property of a QueryDataObjectResultSetColumnMetadata.
    #: This constant has a value of "VARCHAR2"
    DATA_TYPE_NAME_VARCHAR2 = "VARCHAR2"

    def __init__(self, **kwargs):
        """
        Initializes a new QueryDataObjectResultSetColumnMetadata object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param name:
            The value to assign to the name property of this QueryDataObjectResultSetColumnMetadata.
        :type name: str

        :param data_type_name:
            The value to assign to the data_type_name property of this QueryDataObjectResultSetColumnMetadata.
            Allowed values for this property are: "NUMBER", "TIMESTAMP", "VARCHAR2", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type data_type_name: str

        """
        self.swagger_types = {
            'name': 'str',
            'data_type_name': 'str'
        }

        self.attribute_map = {
            'name': 'name',
            'data_type_name': 'dataTypeName'
        }

        self._name = None
        self._data_type_name = None

    @property
    def name(self):
        """
        **[Required]** Gets the name of this QueryDataObjectResultSetColumnMetadata.
        Name of the column in a data object query result set.


        :return: The name of this QueryDataObjectResultSetColumnMetadata.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this QueryDataObjectResultSetColumnMetadata.
        Name of the column in a data object query result set.


        :param name: The name of this QueryDataObjectResultSetColumnMetadata.
        :type: str
        """
        self._name = name

    @property
    def data_type_name(self):
        """
        Gets the data_type_name of this QueryDataObjectResultSetColumnMetadata.
        Type of the column in a data object query result set.

        Allowed values for this property are: "NUMBER", "TIMESTAMP", "VARCHAR2", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The data_type_name of this QueryDataObjectResultSetColumnMetadata.
        :rtype: str
        """
        return self._data_type_name

    @data_type_name.setter
    def data_type_name(self, data_type_name):
        """
        Sets the data_type_name of this QueryDataObjectResultSetColumnMetadata.
        Type of the column in a data object query result set.


        :param data_type_name: The data_type_name of this QueryDataObjectResultSetColumnMetadata.
        :type: str
        """
        allowed_values = ["NUMBER", "TIMESTAMP", "VARCHAR2"]
        if not value_allowed_none_or_none_sentinel(data_type_name, allowed_values):
            data_type_name = 'UNKNOWN_ENUM_VALUE'
        self._data_type_name = data_type_name

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
