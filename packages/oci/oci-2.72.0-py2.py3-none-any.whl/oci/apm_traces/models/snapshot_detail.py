# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class SnapshotDetail(object):
    """
    A generic key value pair object, which contains information such as the thread ID, thread name, and thread state.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new SnapshotDetail object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param key:
            The value to assign to the key property of this SnapshotDetail.
        :type key: str

        :param value:
            The value to assign to the value property of this SnapshotDetail.
        :type value: object

        """
        self.swagger_types = {
            'key': 'str',
            'value': 'object'
        }

        self.attribute_map = {
            'key': 'key',
            'value': 'value'
        }

        self._key = None
        self._value = None

    @property
    def key(self):
        """
        Gets the key of this SnapshotDetail.
        Name of the property.


        :return: The key of this SnapshotDetail.
        :rtype: str
        """
        return self._key

    @key.setter
    def key(self, key):
        """
        Sets the key of this SnapshotDetail.
        Name of the property.


        :param key: The key of this SnapshotDetail.
        :type: str
        """
        self._key = key

    @property
    def value(self):
        """
        Gets the value of this SnapshotDetail.
        Value of the property.


        :return: The value of this SnapshotDetail.
        :rtype: object
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Sets the value of this SnapshotDetail.
        Value of the property.


        :param value: The value of this SnapshotDetail.
        :type: object
        """
        self._value = value

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
