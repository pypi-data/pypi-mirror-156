# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class AwrHubs(object):
    """
    Logical grouping used for Awr Hub operations.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new AwrHubs object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param awr_hubs:
            The value to assign to the awr_hubs property of this AwrHubs.
        :type awr_hubs: object

        """
        self.swagger_types = {
            'awr_hubs': 'object'
        }

        self.attribute_map = {
            'awr_hubs': 'awrHubs'
        }

        self._awr_hubs = None

    @property
    def awr_hubs(self):
        """
        Gets the awr_hubs of this AwrHubs.
        Awr Hub Object.


        :return: The awr_hubs of this AwrHubs.
        :rtype: object
        """
        return self._awr_hubs

    @awr_hubs.setter
    def awr_hubs(self, awr_hubs):
        """
        Sets the awr_hubs of this AwrHubs.
        Awr Hub Object.


        :param awr_hubs: The awr_hubs of this AwrHubs.
        :type: object
        """
        self._awr_hubs = awr_hubs

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
