# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

from .data_object_column_unit import DataObjectColumnUnit
from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class DataObjectRateColumnUnit(DataObjectColumnUnit):
    """
    Unit details of a data object column of RATE unit category.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new DataObjectRateColumnUnit object with values from keyword arguments. The default value of the :py:attr:`~oci.opsi.models.DataObjectRateColumnUnit.unit_category` attribute
        of this class is ``RATE`` and it should not be changed.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param unit_category:
            The value to assign to the unit_category property of this DataObjectRateColumnUnit.
            Allowed values for this property are: "DATA_SIZE", "TIME", "POWER", "TEMPERATURE", "CORE", "RATE", "FREQUENCY", "OTHER_STANDARD", "CUSTOM"
        :type unit_category: str

        :param display_name:
            The value to assign to the display_name property of this DataObjectRateColumnUnit.
        :type display_name: str

        :param numerator:
            The value to assign to the numerator property of this DataObjectRateColumnUnit.
        :type numerator: oci.opsi.models.DataObjectColumnUnit

        :param denominator:
            The value to assign to the denominator property of this DataObjectRateColumnUnit.
        :type denominator: oci.opsi.models.DataObjectColumnUnit

        """
        self.swagger_types = {
            'unit_category': 'str',
            'display_name': 'str',
            'numerator': 'DataObjectColumnUnit',
            'denominator': 'DataObjectColumnUnit'
        }

        self.attribute_map = {
            'unit_category': 'unitCategory',
            'display_name': 'displayName',
            'numerator': 'numerator',
            'denominator': 'denominator'
        }

        self._unit_category = None
        self._display_name = None
        self._numerator = None
        self._denominator = None
        self._unit_category = 'RATE'

    @property
    def numerator(self):
        """
        Gets the numerator of this DataObjectRateColumnUnit.

        :return: The numerator of this DataObjectRateColumnUnit.
        :rtype: oci.opsi.models.DataObjectColumnUnit
        """
        return self._numerator

    @numerator.setter
    def numerator(self, numerator):
        """
        Sets the numerator of this DataObjectRateColumnUnit.

        :param numerator: The numerator of this DataObjectRateColumnUnit.
        :type: oci.opsi.models.DataObjectColumnUnit
        """
        self._numerator = numerator

    @property
    def denominator(self):
        """
        Gets the denominator of this DataObjectRateColumnUnit.

        :return: The denominator of this DataObjectRateColumnUnit.
        :rtype: oci.opsi.models.DataObjectColumnUnit
        """
        return self._denominator

    @denominator.setter
    def denominator(self, denominator):
        """
        Sets the denominator of this DataObjectRateColumnUnit.

        :param denominator: The denominator of this DataObjectRateColumnUnit.
        :type: oci.opsi.models.DataObjectColumnUnit
        """
        self._denominator = denominator

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
