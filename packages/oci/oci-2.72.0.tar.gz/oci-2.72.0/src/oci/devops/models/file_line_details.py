# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class FileLineDetails(object):
    """
    Object containing the details of a line in a file.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new FileLineDetails object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param line_number:
            The value to assign to the line_number property of this FileLineDetails.
        :type line_number: int

        :param line_content:
            The value to assign to the line_content property of this FileLineDetails.
        :type line_content: str

        """
        self.swagger_types = {
            'line_number': 'int',
            'line_content': 'str'
        }

        self.attribute_map = {
            'line_number': 'lineNumber',
            'line_content': 'lineContent'
        }

        self._line_number = None
        self._line_content = None

    @property
    def line_number(self):
        """
        **[Required]** Gets the line_number of this FileLineDetails.
        The line number.


        :return: The line_number of this FileLineDetails.
        :rtype: int
        """
        return self._line_number

    @line_number.setter
    def line_number(self, line_number):
        """
        Sets the line_number of this FileLineDetails.
        The line number.


        :param line_number: The line_number of this FileLineDetails.
        :type: int
        """
        self._line_number = line_number

    @property
    def line_content(self):
        """
        **[Required]** Gets the line_content of this FileLineDetails.
        The content of the line.


        :return: The line_content of this FileLineDetails.
        :rtype: str
        """
        return self._line_content

    @line_content.setter
    def line_content(self, line_content):
        """
        Sets the line_content of this FileLineDetails.
        The content of the line.


        :param line_content: The line_content of this FileLineDetails.
        :type: str
        """
        self._line_content = line_content

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
