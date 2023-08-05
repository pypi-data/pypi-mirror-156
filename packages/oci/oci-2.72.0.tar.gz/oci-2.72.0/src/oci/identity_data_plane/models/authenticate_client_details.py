# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class AuthenticateClientDetails(object):
    """
    AuthenticateClientDetails model.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new AuthenticateClientDetails object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param request_headers:
            The value to assign to the request_headers property of this AuthenticateClientDetails.
        :type request_headers: dict(str, list[str])

        """
        self.swagger_types = {
            'request_headers': 'dict(str, list[str])'
        }

        self.attribute_map = {
            'request_headers': 'requestHeaders'
        }

        self._request_headers = None

    @property
    def request_headers(self):
        """
        **[Required]** Gets the request_headers of this AuthenticateClientDetails.
        The signed headers of the original caller's request.


        :return: The request_headers of this AuthenticateClientDetails.
        :rtype: dict(str, list[str])
        """
        return self._request_headers

    @request_headers.setter
    def request_headers(self, request_headers):
        """
        Sets the request_headers of this AuthenticateClientDetails.
        The signed headers of the original caller's request.


        :param request_headers: The request_headers of this AuthenticateClientDetails.
        :type: dict(str, list[str])
        """
        self._request_headers = request_headers

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
