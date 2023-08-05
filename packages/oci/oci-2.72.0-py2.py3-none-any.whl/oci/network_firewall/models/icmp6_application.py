# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

from .application import Application
from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class Icmp6Application(Application):
    """
    ICMP6 Application used on the firewall policy rules.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new Icmp6Application object with values from keyword arguments. The default value of the :py:attr:`~oci.network_firewall.models.Icmp6Application.type` attribute
        of this class is ``ICMP6`` and it should not be changed.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param type:
            The value to assign to the type property of this Icmp6Application.
        :type type: str

        :param icmp_type:
            The value to assign to the icmp_type property of this Icmp6Application.
        :type icmp_type: int

        :param icmp_code:
            The value to assign to the icmp_code property of this Icmp6Application.
        :type icmp_code: int

        """
        self.swagger_types = {
            'type': 'str',
            'icmp_type': 'int',
            'icmp_code': 'int'
        }

        self.attribute_map = {
            'type': 'type',
            'icmp_type': 'icmpType',
            'icmp_code': 'icmpCode'
        }

        self._type = None
        self._icmp_type = None
        self._icmp_code = None
        self._type = 'ICMP6'

    @property
    def icmp_type(self):
        """
        **[Required]** Gets the icmp_type of this Icmp6Application.
        The value of the ICMP6 message Type field as defined by `RFC 4443`__.

        __ https://www.rfc-editor.org/rfc/rfc4443.html#section-2.1


        :return: The icmp_type of this Icmp6Application.
        :rtype: int
        """
        return self._icmp_type

    @icmp_type.setter
    def icmp_type(self, icmp_type):
        """
        Sets the icmp_type of this Icmp6Application.
        The value of the ICMP6 message Type field as defined by `RFC 4443`__.

        __ https://www.rfc-editor.org/rfc/rfc4443.html#section-2.1


        :param icmp_type: The icmp_type of this Icmp6Application.
        :type: int
        """
        self._icmp_type = icmp_type

    @property
    def icmp_code(self):
        """
        Gets the icmp_code of this Icmp6Application.
        The value of the ICMP6 message Code (subtype) field as defined by `RFC 4443`__.

        __ https://www.rfc-editor.org/rfc/rfc4443.html#section-2.1


        :return: The icmp_code of this Icmp6Application.
        :rtype: int
        """
        return self._icmp_code

    @icmp_code.setter
    def icmp_code(self, icmp_code):
        """
        Sets the icmp_code of this Icmp6Application.
        The value of the ICMP6 message Code (subtype) field as defined by `RFC 4443`__.

        __ https://www.rfc-editor.org/rfc/rfc4443.html#section-2.1


        :param icmp_code: The icmp_code of this Icmp6Application.
        :type: int
        """
        self._icmp_code = icmp_code

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
