# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class UpdateDatabaseRegistrationDetails(object):
    """
    The information to update for a DatabaseRegistration.
    """

    #: A constant which can be used with the session_mode property of a UpdateDatabaseRegistrationDetails.
    #: This constant has a value of "DIRECT"
    SESSION_MODE_DIRECT = "DIRECT"

    #: A constant which can be used with the session_mode property of a UpdateDatabaseRegistrationDetails.
    #: This constant has a value of "REDIRECT"
    SESSION_MODE_REDIRECT = "REDIRECT"

    def __init__(self, **kwargs):
        """
        Initializes a new UpdateDatabaseRegistrationDetails object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param display_name:
            The value to assign to the display_name property of this UpdateDatabaseRegistrationDetails.
        :type display_name: str

        :param description:
            The value to assign to the description property of this UpdateDatabaseRegistrationDetails.
        :type description: str

        :param freeform_tags:
            The value to assign to the freeform_tags property of this UpdateDatabaseRegistrationDetails.
        :type freeform_tags: dict(str, str)

        :param defined_tags:
            The value to assign to the defined_tags property of this UpdateDatabaseRegistrationDetails.
        :type defined_tags: dict(str, dict(str, object))

        :param fqdn:
            The value to assign to the fqdn property of this UpdateDatabaseRegistrationDetails.
        :type fqdn: str

        :param username:
            The value to assign to the username property of this UpdateDatabaseRegistrationDetails.
        :type username: str

        :param password:
            The value to assign to the password property of this UpdateDatabaseRegistrationDetails.
        :type password: str

        :param connection_string:
            The value to assign to the connection_string property of this UpdateDatabaseRegistrationDetails.
        :type connection_string: str

        :param session_mode:
            The value to assign to the session_mode property of this UpdateDatabaseRegistrationDetails.
            Allowed values for this property are: "DIRECT", "REDIRECT"
        :type session_mode: str

        :param wallet:
            The value to assign to the wallet property of this UpdateDatabaseRegistrationDetails.
        :type wallet: str

        :param alias_name:
            The value to assign to the alias_name property of this UpdateDatabaseRegistrationDetails.
        :type alias_name: str

        """
        self.swagger_types = {
            'display_name': 'str',
            'description': 'str',
            'freeform_tags': 'dict(str, str)',
            'defined_tags': 'dict(str, dict(str, object))',
            'fqdn': 'str',
            'username': 'str',
            'password': 'str',
            'connection_string': 'str',
            'session_mode': 'str',
            'wallet': 'str',
            'alias_name': 'str'
        }

        self.attribute_map = {
            'display_name': 'displayName',
            'description': 'description',
            'freeform_tags': 'freeformTags',
            'defined_tags': 'definedTags',
            'fqdn': 'fqdn',
            'username': 'username',
            'password': 'password',
            'connection_string': 'connectionString',
            'session_mode': 'sessionMode',
            'wallet': 'wallet',
            'alias_name': 'aliasName'
        }

        self._display_name = None
        self._description = None
        self._freeform_tags = None
        self._defined_tags = None
        self._fqdn = None
        self._username = None
        self._password = None
        self._connection_string = None
        self._session_mode = None
        self._wallet = None
        self._alias_name = None

    @property
    def display_name(self):
        """
        Gets the display_name of this UpdateDatabaseRegistrationDetails.
        An object's Display Name.


        :return: The display_name of this UpdateDatabaseRegistrationDetails.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """
        Sets the display_name of this UpdateDatabaseRegistrationDetails.
        An object's Display Name.


        :param display_name: The display_name of this UpdateDatabaseRegistrationDetails.
        :type: str
        """
        self._display_name = display_name

    @property
    def description(self):
        """
        Gets the description of this UpdateDatabaseRegistrationDetails.
        Metadata about this specific object.


        :return: The description of this UpdateDatabaseRegistrationDetails.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this UpdateDatabaseRegistrationDetails.
        Metadata about this specific object.


        :param description: The description of this UpdateDatabaseRegistrationDetails.
        :type: str
        """
        self._description = description

    @property
    def freeform_tags(self):
        """
        Gets the freeform_tags of this UpdateDatabaseRegistrationDetails.
        A simple key-value pair that is applied without any predefined name, type, or scope. Exists for cross-compatibility only.
        Example: `{\"bar-key\": \"value\"}`


        :return: The freeform_tags of this UpdateDatabaseRegistrationDetails.
        :rtype: dict(str, str)
        """
        return self._freeform_tags

    @freeform_tags.setter
    def freeform_tags(self, freeform_tags):
        """
        Sets the freeform_tags of this UpdateDatabaseRegistrationDetails.
        A simple key-value pair that is applied without any predefined name, type, or scope. Exists for cross-compatibility only.
        Example: `{\"bar-key\": \"value\"}`


        :param freeform_tags: The freeform_tags of this UpdateDatabaseRegistrationDetails.
        :type: dict(str, str)
        """
        self._freeform_tags = freeform_tags

    @property
    def defined_tags(self):
        """
        Gets the defined_tags of this UpdateDatabaseRegistrationDetails.
        Tags defined for this resource. Each key is predefined and scoped to a namespace.
        Example: `{\"foo-namespace\": {\"bar-key\": \"value\"}}`


        :return: The defined_tags of this UpdateDatabaseRegistrationDetails.
        :rtype: dict(str, dict(str, object))
        """
        return self._defined_tags

    @defined_tags.setter
    def defined_tags(self, defined_tags):
        """
        Sets the defined_tags of this UpdateDatabaseRegistrationDetails.
        Tags defined for this resource. Each key is predefined and scoped to a namespace.
        Example: `{\"foo-namespace\": {\"bar-key\": \"value\"}}`


        :param defined_tags: The defined_tags of this UpdateDatabaseRegistrationDetails.
        :type: dict(str, dict(str, object))
        """
        self._defined_tags = defined_tags

    @property
    def fqdn(self):
        """
        Gets the fqdn of this UpdateDatabaseRegistrationDetails.
        A three-label Fully Qualified Domain Name (FQDN) for a resource.


        :return: The fqdn of this UpdateDatabaseRegistrationDetails.
        :rtype: str
        """
        return self._fqdn

    @fqdn.setter
    def fqdn(self, fqdn):
        """
        Sets the fqdn of this UpdateDatabaseRegistrationDetails.
        A three-label Fully Qualified Domain Name (FQDN) for a resource.


        :param fqdn: The fqdn of this UpdateDatabaseRegistrationDetails.
        :type: str
        """
        self._fqdn = fqdn

    @property
    def username(self):
        """
        Gets the username of this UpdateDatabaseRegistrationDetails.
        The username Oracle GoldenGate uses to connect the associated RDBMS.  This username must already exist and be available for use by the database.  It must conform to the security requirements implemented by the database including length, case sensitivity, and so on.


        :return: The username of this UpdateDatabaseRegistrationDetails.
        :rtype: str
        """
        return self._username

    @username.setter
    def username(self, username):
        """
        Sets the username of this UpdateDatabaseRegistrationDetails.
        The username Oracle GoldenGate uses to connect the associated RDBMS.  This username must already exist and be available for use by the database.  It must conform to the security requirements implemented by the database including length, case sensitivity, and so on.


        :param username: The username of this UpdateDatabaseRegistrationDetails.
        :type: str
        """
        self._username = username

    @property
    def password(self):
        """
        Gets the password of this UpdateDatabaseRegistrationDetails.
        The password Oracle GoldenGate uses to connect the associated RDBMS.  It must conform to the specific security requirements implemented by the database including length, case sensitivity, and so on.


        :return: The password of this UpdateDatabaseRegistrationDetails.
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """
        Sets the password of this UpdateDatabaseRegistrationDetails.
        The password Oracle GoldenGate uses to connect the associated RDBMS.  It must conform to the specific security requirements implemented by the database including length, case sensitivity, and so on.


        :param password: The password of this UpdateDatabaseRegistrationDetails.
        :type: str
        """
        self._password = password

    @property
    def connection_string(self):
        """
        Gets the connection_string of this UpdateDatabaseRegistrationDetails.
        Connect descriptor or Easy Connect Naming method that Oracle GoldenGate uses to connect to a database.


        :return: The connection_string of this UpdateDatabaseRegistrationDetails.
        :rtype: str
        """
        return self._connection_string

    @connection_string.setter
    def connection_string(self, connection_string):
        """
        Sets the connection_string of this UpdateDatabaseRegistrationDetails.
        Connect descriptor or Easy Connect Naming method that Oracle GoldenGate uses to connect to a database.


        :param connection_string: The connection_string of this UpdateDatabaseRegistrationDetails.
        :type: str
        """
        self._connection_string = connection_string

    @property
    def session_mode(self):
        """
        Gets the session_mode of this UpdateDatabaseRegistrationDetails.
        The mode of the database connection session to be established by the data client. REDIRECT - for a RAC database, DIRECT - for a non-RAC database. Connection to a RAC database involves a redirection received from the SCAN listeners to the database node to connect to. By default the mode would be DIRECT.

        Allowed values for this property are: "DIRECT", "REDIRECT"


        :return: The session_mode of this UpdateDatabaseRegistrationDetails.
        :rtype: str
        """
        return self._session_mode

    @session_mode.setter
    def session_mode(self, session_mode):
        """
        Sets the session_mode of this UpdateDatabaseRegistrationDetails.
        The mode of the database connection session to be established by the data client. REDIRECT - for a RAC database, DIRECT - for a non-RAC database. Connection to a RAC database involves a redirection received from the SCAN listeners to the database node to connect to. By default the mode would be DIRECT.


        :param session_mode: The session_mode of this UpdateDatabaseRegistrationDetails.
        :type: str
        """
        allowed_values = ["DIRECT", "REDIRECT"]
        if not value_allowed_none_or_none_sentinel(session_mode, allowed_values):
            raise ValueError(
                "Invalid value for `session_mode`, must be None or one of {0}"
                .format(allowed_values)
            )
        self._session_mode = session_mode

    @property
    def wallet(self):
        """
        Gets the wallet of this UpdateDatabaseRegistrationDetails.
        The wallet contents Oracle GoldenGate uses to make connections to a database.  This attribute is expected to be base64 encoded.


        :return: The wallet of this UpdateDatabaseRegistrationDetails.
        :rtype: str
        """
        return self._wallet

    @wallet.setter
    def wallet(self, wallet):
        """
        Sets the wallet of this UpdateDatabaseRegistrationDetails.
        The wallet contents Oracle GoldenGate uses to make connections to a database.  This attribute is expected to be base64 encoded.


        :param wallet: The wallet of this UpdateDatabaseRegistrationDetails.
        :type: str
        """
        self._wallet = wallet

    @property
    def alias_name(self):
        """
        Gets the alias_name of this UpdateDatabaseRegistrationDetails.
        Credential store alias.


        :return: The alias_name of this UpdateDatabaseRegistrationDetails.
        :rtype: str
        """
        return self._alias_name

    @alias_name.setter
    def alias_name(self, alias_name):
        """
        Sets the alias_name of this UpdateDatabaseRegistrationDetails.
        Credential store alias.


        :param alias_name: The alias_name of this UpdateDatabaseRegistrationDetails.
        :type: str
        """
        self._alias_name = alias_name

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
