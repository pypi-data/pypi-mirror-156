# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class OperationsInsightsWarehouses(object):
    """
    Logical grouping used for Operations Insights Warehouse operations.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new OperationsInsightsWarehouses object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param operations_insights_warehouses:
            The value to assign to the operations_insights_warehouses property of this OperationsInsightsWarehouses.
        :type operations_insights_warehouses: object

        """
        self.swagger_types = {
            'operations_insights_warehouses': 'object'
        }

        self.attribute_map = {
            'operations_insights_warehouses': 'operationsInsightsWarehouses'
        }

        self._operations_insights_warehouses = None

    @property
    def operations_insights_warehouses(self):
        """
        Gets the operations_insights_warehouses of this OperationsInsightsWarehouses.
        Operations Insights Warehouse Object.


        :return: The operations_insights_warehouses of this OperationsInsightsWarehouses.
        :rtype: object
        """
        return self._operations_insights_warehouses

    @operations_insights_warehouses.setter
    def operations_insights_warehouses(self, operations_insights_warehouses):
        """
        Sets the operations_insights_warehouses of this OperationsInsightsWarehouses.
        Operations Insights Warehouse Object.


        :param operations_insights_warehouses: The operations_insights_warehouses of this OperationsInsightsWarehouses.
        :type: object
        """
        self._operations_insights_warehouses = operations_insights_warehouses

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
