# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

from .format_entry import FormatEntry
from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class RegularExpressionFormatEntry(FormatEntry):
    """
    The Regular Expression masking format gives the flexibility to use regular
    expressions to search for sensitive data in a column of Large Object data
    type (LOB), and replace the data with a fixed string, fixed number, null
    value, or SQL expression. It can also be used for columns of VARCHAR2 type
    to mask parts of strings. To learn more, check Regular Expressions in the
    Data Safe documentation.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new RegularExpressionFormatEntry object with values from keyword arguments. The default value of the :py:attr:`~oci.data_safe.models.RegularExpressionFormatEntry.type` attribute
        of this class is ``REGULAR_EXPRESSION`` and it should not be changed.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param type:
            The value to assign to the type property of this RegularExpressionFormatEntry.
            Allowed values for this property are: "DELETE_ROWS", "DETERMINISTIC_SUBSTITUTION", "DETERMINISTIC_ENCRYPTION", "DETERMINISTIC_ENCRYPTION_DATE", "FIXED_NUMBER", "FIXED_STRING", "LIBRARY_MASKING_FORMAT", "NULL_VALUE", "POST_PROCESSING_FUNCTION", "PRESERVE_ORIGINAL_DATA", "RANDOM_DATE", "RANDOM_DECIMAL_NUMBER", "RANDOM_DIGITS", "RANDOM_LIST", "RANDOM_NUMBER", "RANDOM_STRING", "RANDOM_SUBSTITUTION", "REGULAR_EXPRESSION", "SHUFFLE", "SQL_EXPRESSION", "SUBSTRING", "TRUNCATE_TABLE", "USER_DEFINED_FUNCTION"
        :type type: str

        :param description:
            The value to assign to the description property of this RegularExpressionFormatEntry.
        :type description: str

        :param regular_expression:
            The value to assign to the regular_expression property of this RegularExpressionFormatEntry.
        :type regular_expression: str

        :param replace_with:
            The value to assign to the replace_with property of this RegularExpressionFormatEntry.
        :type replace_with: str

        """
        self.swagger_types = {
            'type': 'str',
            'description': 'str',
            'regular_expression': 'str',
            'replace_with': 'str'
        }

        self.attribute_map = {
            'type': 'type',
            'description': 'description',
            'regular_expression': 'regularExpression',
            'replace_with': 'replaceWith'
        }

        self._type = None
        self._description = None
        self._regular_expression = None
        self._replace_with = None
        self._type = 'REGULAR_EXPRESSION'

    @property
    def regular_expression(self):
        """
        **[Required]** Gets the regular_expression of this RegularExpressionFormatEntry.
        The pattern that should be used to search for data.


        :return: The regular_expression of this RegularExpressionFormatEntry.
        :rtype: str
        """
        return self._regular_expression

    @regular_expression.setter
    def regular_expression(self, regular_expression):
        """
        Sets the regular_expression of this RegularExpressionFormatEntry.
        The pattern that should be used to search for data.


        :param regular_expression: The regular_expression of this RegularExpressionFormatEntry.
        :type: str
        """
        self._regular_expression = regular_expression

    @property
    def replace_with(self):
        """
        **[Required]** Gets the replace_with of this RegularExpressionFormatEntry.
        The value that should be used to replace the data matching the regular
        expression. It can be a fixed string, fixed number, null value, or
        SQL expression.


        :return: The replace_with of this RegularExpressionFormatEntry.
        :rtype: str
        """
        return self._replace_with

    @replace_with.setter
    def replace_with(self, replace_with):
        """
        Sets the replace_with of this RegularExpressionFormatEntry.
        The value that should be used to replace the data matching the regular
        expression. It can be a fixed string, fixed number, null value, or
        SQL expression.


        :param replace_with: The replace_with of this RegularExpressionFormatEntry.
        :type: str
        """
        self._replace_with = replace_with

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
