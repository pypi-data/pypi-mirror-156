# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class PercentageOfCoresEnabledOptions(object):
    """
    Configuration options for the percentage of cores enabled.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new PercentageOfCoresEnabledOptions object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param min:
            The value to assign to the min property of this PercentageOfCoresEnabledOptions.
        :type min: int

        :param max:
            The value to assign to the max property of this PercentageOfCoresEnabledOptions.
        :type max: int

        :param default_value:
            The value to assign to the default_value property of this PercentageOfCoresEnabledOptions.
        :type default_value: int

        """
        self.swagger_types = {
            'min': 'int',
            'max': 'int',
            'default_value': 'int'
        }

        self.attribute_map = {
            'min': 'min',
            'max': 'max',
            'default_value': 'defaultValue'
        }

        self._min = None
        self._max = None
        self._default_value = None

    @property
    def min(self):
        """
        Gets the min of this PercentageOfCoresEnabledOptions.
        The minimum allowed percentage of cores enabled.


        :return: The min of this PercentageOfCoresEnabledOptions.
        :rtype: int
        """
        return self._min

    @min.setter
    def min(self, min):
        """
        Sets the min of this PercentageOfCoresEnabledOptions.
        The minimum allowed percentage of cores enabled.


        :param min: The min of this PercentageOfCoresEnabledOptions.
        :type: int
        """
        self._min = min

    @property
    def max(self):
        """
        Gets the max of this PercentageOfCoresEnabledOptions.
        The maximum allowed percentage of cores enabled.


        :return: The max of this PercentageOfCoresEnabledOptions.
        :rtype: int
        """
        return self._max

    @max.setter
    def max(self, max):
        """
        Sets the max of this PercentageOfCoresEnabledOptions.
        The maximum allowed percentage of cores enabled.


        :param max: The max of this PercentageOfCoresEnabledOptions.
        :type: int
        """
        self._max = max

    @property
    def default_value(self):
        """
        Gets the default_value of this PercentageOfCoresEnabledOptions.
        The default percentage of cores enabled.


        :return: The default_value of this PercentageOfCoresEnabledOptions.
        :rtype: int
        """
        return self._default_value

    @default_value.setter
    def default_value(self, default_value):
        """
        Sets the default_value of this PercentageOfCoresEnabledOptions.
        The default percentage of cores enabled.


        :param default_value: The default_value of this PercentageOfCoresEnabledOptions.
        :type: int
        """
        self._default_value = default_value

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
