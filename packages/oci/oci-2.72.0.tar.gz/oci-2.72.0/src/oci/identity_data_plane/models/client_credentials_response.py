# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class ClientCredentialsResponse(object):
    """
    ClientCredentialsResponse model.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new ClientCredentialsResponse object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param access_token:
            The value to assign to the access_token property of this ClientCredentialsResponse.
        :type access_token: str

        :param token_type:
            The value to assign to the token_type property of this ClientCredentialsResponse.
        :type token_type: str

        :param expires_in:
            The value to assign to the expires_in property of this ClientCredentialsResponse.
        :type expires_in: str

        """
        self.swagger_types = {
            'access_token': 'str',
            'token_type': 'str',
            'expires_in': 'str'
        }

        self.attribute_map = {
            'access_token': 'access_token',
            'token_type': 'token_type',
            'expires_in': 'expires_in'
        }

        self._access_token = None
        self._token_type = None
        self._expires_in = None

    @property
    def access_token(self):
        """
        **[Required]** Gets the access_token of this ClientCredentialsResponse.
        The access token.


        :return: The access_token of this ClientCredentialsResponse.
        :rtype: str
        """
        return self._access_token

    @access_token.setter
    def access_token(self, access_token):
        """
        Sets the access_token of this ClientCredentialsResponse.
        The access token.


        :param access_token: The access_token of this ClientCredentialsResponse.
        :type: str
        """
        self._access_token = access_token

    @property
    def token_type(self):
        """
        **[Required]** Gets the token_type of this ClientCredentialsResponse.
        The token type.


        :return: The token_type of this ClientCredentialsResponse.
        :rtype: str
        """
        return self._token_type

    @token_type.setter
    def token_type(self, token_type):
        """
        Sets the token_type of this ClientCredentialsResponse.
        The token type.


        :param token_type: The token_type of this ClientCredentialsResponse.
        :type: str
        """
        self._token_type = token_type

    @property
    def expires_in(self):
        """
        **[Required]** Gets the expires_in of this ClientCredentialsResponse.
        The amount of time until the token expires.


        :return: The expires_in of this ClientCredentialsResponse.
        :rtype: str
        """
        return self._expires_in

    @expires_in.setter
    def expires_in(self, expires_in):
        """
        Sets the expires_in of this ClientCredentialsResponse.
        The amount of time until the token expires.


        :param expires_in: The expires_in of this ClientCredentialsResponse.
        :type: str
        """
        self._expires_in = expires_in

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
