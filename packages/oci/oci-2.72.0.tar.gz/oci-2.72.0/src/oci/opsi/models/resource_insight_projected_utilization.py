# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class ResourceInsightProjectedUtilization(object):
    """
    Projected utilization(High/low) for cpu or storage
    """

    def __init__(self, **kwargs):
        """
        Initializes a new ResourceInsightProjectedUtilization object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param low:
            The value to assign to the low property of this ResourceInsightProjectedUtilization.
        :type low: list[oci.opsi.models.ResourceInsightProjectedUtilizationItem]

        :param high:
            The value to assign to the high property of this ResourceInsightProjectedUtilization.
        :type high: list[oci.opsi.models.ResourceInsightProjectedUtilizationItem]

        """
        self.swagger_types = {
            'low': 'list[ResourceInsightProjectedUtilizationItem]',
            'high': 'list[ResourceInsightProjectedUtilizationItem]'
        }

        self.attribute_map = {
            'low': 'low',
            'high': 'high'
        }

        self._low = None
        self._high = None

    @property
    def low(self):
        """
        **[Required]** Gets the low of this ResourceInsightProjectedUtilization.
        List of db ids with low usage


        :return: The low of this ResourceInsightProjectedUtilization.
        :rtype: list[oci.opsi.models.ResourceInsightProjectedUtilizationItem]
        """
        return self._low

    @low.setter
    def low(self, low):
        """
        Sets the low of this ResourceInsightProjectedUtilization.
        List of db ids with low usage


        :param low: The low of this ResourceInsightProjectedUtilization.
        :type: list[oci.opsi.models.ResourceInsightProjectedUtilizationItem]
        """
        self._low = low

    @property
    def high(self):
        """
        **[Required]** Gets the high of this ResourceInsightProjectedUtilization.
        List of db ids with high usage


        :return: The high of this ResourceInsightProjectedUtilization.
        :rtype: list[oci.opsi.models.ResourceInsightProjectedUtilizationItem]
        """
        return self._high

    @high.setter
    def high(self, high):
        """
        Sets the high of this ResourceInsightProjectedUtilization.
        List of db ids with high usage


        :param high: The high of this ResourceInsightProjectedUtilization.
        :type: list[oci.opsi.models.ResourceInsightProjectedUtilizationItem]
        """
        self._high = high

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
