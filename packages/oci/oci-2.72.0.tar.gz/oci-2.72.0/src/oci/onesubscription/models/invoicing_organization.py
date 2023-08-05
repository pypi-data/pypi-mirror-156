# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class InvoicingOrganization(object):
    """
    Organization details
    """

    def __init__(self, **kwargs):
        """
        Initializes a new InvoicingOrganization object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param name:
            The value to assign to the name property of this InvoicingOrganization.
        :type name: str

        :param number:
            The value to assign to the number property of this InvoicingOrganization.
        :type number: float

        """
        self.swagger_types = {
            'name': 'str',
            'number': 'float'
        }

        self.attribute_map = {
            'name': 'name',
            'number': 'number'
        }

        self._name = None
        self._number = None

    @property
    def name(self):
        """
        **[Required]** Gets the name of this InvoicingOrganization.
        Organization name


        :return: The name of this InvoicingOrganization.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this InvoicingOrganization.
        Organization name


        :param name: The name of this InvoicingOrganization.
        :type: str
        """
        self._name = name

    @property
    def number(self):
        """
        **[Required]** Gets the number of this InvoicingOrganization.
        Organization ID


        :return: The number of this InvoicingOrganization.
        :rtype: float
        """
        return self._number

    @number.setter
    def number(self, number):
        """
        Sets the number of this InvoicingOrganization.
        Organization ID


        :param number: The number of this InvoicingOrganization.
        :type: float
        """
        self._number = number

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
