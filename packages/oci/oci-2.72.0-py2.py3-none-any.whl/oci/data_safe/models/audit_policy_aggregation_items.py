# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class AuditPolicyAggregationItems(object):
    """
    Details of audit profile aggregation items.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new AuditPolicyAggregationItems object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param dimensions:
            The value to assign to the dimensions property of this AuditPolicyAggregationItems.
        :type dimensions: oci.data_safe.models.AuditPolicyDimensions

        :param count:
            The value to assign to the count property of this AuditPolicyAggregationItems.
        :type count: int

        """
        self.swagger_types = {
            'dimensions': 'AuditPolicyDimensions',
            'count': 'int'
        }

        self.attribute_map = {
            'dimensions': 'dimensions',
            'count': 'count'
        }

        self._dimensions = None
        self._count = None

    @property
    def dimensions(self):
        """
        Gets the dimensions of this AuditPolicyAggregationItems.

        :return: The dimensions of this AuditPolicyAggregationItems.
        :rtype: oci.data_safe.models.AuditPolicyDimensions
        """
        return self._dimensions

    @dimensions.setter
    def dimensions(self, dimensions):
        """
        Sets the dimensions of this AuditPolicyAggregationItems.

        :param dimensions: The dimensions of this AuditPolicyAggregationItems.
        :type: oci.data_safe.models.AuditPolicyDimensions
        """
        self._dimensions = dimensions

    @property
    def count(self):
        """
        Gets the count of this AuditPolicyAggregationItems.
        Total count of aggregated metric.


        :return: The count of this AuditPolicyAggregationItems.
        :rtype: int
        """
        return self._count

    @count.setter
    def count(self, count):
        """
        Sets the count of this AuditPolicyAggregationItems.
        Total count of aggregated metric.


        :param count: The count of this AuditPolicyAggregationItems.
        :type: int
        """
        self._count = count

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
