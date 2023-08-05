# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class AuditEventAggregationItems(object):
    """
    Details of audit events aggregation items.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new AuditEventAggregationItems object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param display_name:
            The value to assign to the display_name property of this AuditEventAggregationItems.
        :type display_name: str

        :param metric_name:
            The value to assign to the metric_name property of this AuditEventAggregationItems.
        :type metric_name: str

        :param time_started:
            The value to assign to the time_started property of this AuditEventAggregationItems.
        :type time_started: datetime

        :param time_ended:
            The value to assign to the time_ended property of this AuditEventAggregationItems.
        :type time_ended: datetime

        :param count:
            The value to assign to the count property of this AuditEventAggregationItems.
        :type count: int

        :param dimensions:
            The value to assign to the dimensions property of this AuditEventAggregationItems.
        :type dimensions: oci.data_safe.models.AuditEventAggregationDimensions

        """
        self.swagger_types = {
            'display_name': 'str',
            'metric_name': 'str',
            'time_started': 'datetime',
            'time_ended': 'datetime',
            'count': 'int',
            'dimensions': 'AuditEventAggregationDimensions'
        }

        self.attribute_map = {
            'display_name': 'displayName',
            'metric_name': 'metricName',
            'time_started': 'timeStarted',
            'time_ended': 'timeEnded',
            'count': 'count',
            'dimensions': 'dimensions'
        }

        self._display_name = None
        self._metric_name = None
        self._time_started = None
        self._time_ended = None
        self._count = None
        self._dimensions = None

    @property
    def display_name(self):
        """
        Gets the display_name of this AuditEventAggregationItems.
        Display Name of aggregation field.


        :return: The display_name of this AuditEventAggregationItems.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """
        Sets the display_name of this AuditEventAggregationItems.
        Display Name of aggregation field.


        :param display_name: The display_name of this AuditEventAggregationItems.
        :type: str
        """
        self._display_name = display_name

    @property
    def metric_name(self):
        """
        **[Required]** Gets the metric_name of this AuditEventAggregationItems.
        Name of the aggregation.


        :return: The metric_name of this AuditEventAggregationItems.
        :rtype: str
        """
        return self._metric_name

    @metric_name.setter
    def metric_name(self, metric_name):
        """
        Sets the metric_name of this AuditEventAggregationItems.
        Name of the aggregation.


        :param metric_name: The metric_name of this AuditEventAggregationItems.
        :type: str
        """
        self._metric_name = metric_name

    @property
    def time_started(self):
        """
        **[Required]** Gets the time_started of this AuditEventAggregationItems.
        The time at which the aggregation started.


        :return: The time_started of this AuditEventAggregationItems.
        :rtype: datetime
        """
        return self._time_started

    @time_started.setter
    def time_started(self, time_started):
        """
        Sets the time_started of this AuditEventAggregationItems.
        The time at which the aggregation started.


        :param time_started: The time_started of this AuditEventAggregationItems.
        :type: datetime
        """
        self._time_started = time_started

    @property
    def time_ended(self):
        """
        **[Required]** Gets the time_ended of this AuditEventAggregationItems.
        The time at which the aggregation ended.


        :return: The time_ended of this AuditEventAggregationItems.
        :rtype: datetime
        """
        return self._time_ended

    @time_ended.setter
    def time_ended(self, time_ended):
        """
        Sets the time_ended of this AuditEventAggregationItems.
        The time at which the aggregation ended.


        :param time_ended: The time_ended of this AuditEventAggregationItems.
        :type: datetime
        """
        self._time_ended = time_ended

    @property
    def count(self):
        """
        **[Required]** Gets the count of this AuditEventAggregationItems.
        Total count of aggregated value.


        :return: The count of this AuditEventAggregationItems.
        :rtype: int
        """
        return self._count

    @count.setter
    def count(self, count):
        """
        Sets the count of this AuditEventAggregationItems.
        Total count of aggregated value.


        :param count: The count of this AuditEventAggregationItems.
        :type: int
        """
        self._count = count

    @property
    def dimensions(self):
        """
        Gets the dimensions of this AuditEventAggregationItems.

        :return: The dimensions of this AuditEventAggregationItems.
        :rtype: oci.data_safe.models.AuditEventAggregationDimensions
        """
        return self._dimensions

    @dimensions.setter
    def dimensions(self, dimensions):
        """
        Sets the dimensions of this AuditEventAggregationItems.

        :param dimensions: The dimensions of this AuditEventAggregationItems.
        :type: oci.data_safe.models.AuditEventAggregationDimensions
        """
        self._dimensions = dimensions

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
