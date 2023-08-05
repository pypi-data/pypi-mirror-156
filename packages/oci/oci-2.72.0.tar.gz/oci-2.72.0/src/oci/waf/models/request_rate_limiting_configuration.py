# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class RequestRateLimitingConfiguration(object):
    """
    Rate limiting configuration.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new RequestRateLimitingConfiguration object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param period_in_seconds:
            The value to assign to the period_in_seconds property of this RequestRateLimitingConfiguration.
        :type period_in_seconds: int

        :param requests_limit:
            The value to assign to the requests_limit property of this RequestRateLimitingConfiguration.
        :type requests_limit: int

        :param action_duration_in_seconds:
            The value to assign to the action_duration_in_seconds property of this RequestRateLimitingConfiguration.
        :type action_duration_in_seconds: int

        """
        self.swagger_types = {
            'period_in_seconds': 'int',
            'requests_limit': 'int',
            'action_duration_in_seconds': 'int'
        }

        self.attribute_map = {
            'period_in_seconds': 'periodInSeconds',
            'requests_limit': 'requestsLimit',
            'action_duration_in_seconds': 'actionDurationInSeconds'
        }

        self._period_in_seconds = None
        self._requests_limit = None
        self._action_duration_in_seconds = None

    @property
    def period_in_seconds(self):
        """
        **[Required]** Gets the period_in_seconds of this RequestRateLimitingConfiguration.
        Evaluation period in seconds.


        :return: The period_in_seconds of this RequestRateLimitingConfiguration.
        :rtype: int
        """
        return self._period_in_seconds

    @period_in_seconds.setter
    def period_in_seconds(self, period_in_seconds):
        """
        Sets the period_in_seconds of this RequestRateLimitingConfiguration.
        Evaluation period in seconds.


        :param period_in_seconds: The period_in_seconds of this RequestRateLimitingConfiguration.
        :type: int
        """
        self._period_in_seconds = period_in_seconds

    @property
    def requests_limit(self):
        """
        **[Required]** Gets the requests_limit of this RequestRateLimitingConfiguration.
        Requests allowed per evaluation period.


        :return: The requests_limit of this RequestRateLimitingConfiguration.
        :rtype: int
        """
        return self._requests_limit

    @requests_limit.setter
    def requests_limit(self, requests_limit):
        """
        Sets the requests_limit of this RequestRateLimitingConfiguration.
        Requests allowed per evaluation period.


        :param requests_limit: The requests_limit of this RequestRateLimitingConfiguration.
        :type: int
        """
        self._requests_limit = requests_limit

    @property
    def action_duration_in_seconds(self):
        """
        Gets the action_duration_in_seconds of this RequestRateLimitingConfiguration.
        Duration of block action application in seconds when `requestsLimit` is reached. Optional and can be 0 (no block duration).


        :return: The action_duration_in_seconds of this RequestRateLimitingConfiguration.
        :rtype: int
        """
        return self._action_duration_in_seconds

    @action_duration_in_seconds.setter
    def action_duration_in_seconds(self, action_duration_in_seconds):
        """
        Sets the action_duration_in_seconds of this RequestRateLimitingConfiguration.
        Duration of block action application in seconds when `requestsLimit` is reached. Optional and can be 0 (no block duration).


        :param action_duration_in_seconds: The action_duration_in_seconds of this RequestRateLimitingConfiguration.
        :type: int
        """
        self._action_duration_in_seconds = action_duration_in_seconds

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
