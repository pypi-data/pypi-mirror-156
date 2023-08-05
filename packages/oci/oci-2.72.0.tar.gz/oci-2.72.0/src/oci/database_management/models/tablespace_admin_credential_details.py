# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class TablespaceAdminCredentialDetails(object):
    """
    The credential to connect to the database to perform tablespace administration tasks.
    """

    #: A constant which can be used with the tablespace_admin_credential_type property of a TablespaceAdminCredentialDetails.
    #: This constant has a value of "SECRET"
    TABLESPACE_ADMIN_CREDENTIAL_TYPE_SECRET = "SECRET"

    #: A constant which can be used with the tablespace_admin_credential_type property of a TablespaceAdminCredentialDetails.
    #: This constant has a value of "PASSWORD"
    TABLESPACE_ADMIN_CREDENTIAL_TYPE_PASSWORD = "PASSWORD"

    #: A constant which can be used with the role property of a TablespaceAdminCredentialDetails.
    #: This constant has a value of "NORMAL"
    ROLE_NORMAL = "NORMAL"

    #: A constant which can be used with the role property of a TablespaceAdminCredentialDetails.
    #: This constant has a value of "SYSDBA"
    ROLE_SYSDBA = "SYSDBA"

    def __init__(self, **kwargs):
        """
        Initializes a new TablespaceAdminCredentialDetails object with values from keyword arguments. This class has the following subclasses and if you are using this class as input
        to a service operations then you should favor using a subclass over the base class:

        * :class:`~oci.database_management.models.TablespaceAdminPasswordCredentialDetails`
        * :class:`~oci.database_management.models.TablespaceAdminSecretCredentialDetails`

        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param tablespace_admin_credential_type:
            The value to assign to the tablespace_admin_credential_type property of this TablespaceAdminCredentialDetails.
            Allowed values for this property are: "SECRET", "PASSWORD"
        :type tablespace_admin_credential_type: str

        :param username:
            The value to assign to the username property of this TablespaceAdminCredentialDetails.
        :type username: str

        :param role:
            The value to assign to the role property of this TablespaceAdminCredentialDetails.
            Allowed values for this property are: "NORMAL", "SYSDBA"
        :type role: str

        """
        self.swagger_types = {
            'tablespace_admin_credential_type': 'str',
            'username': 'str',
            'role': 'str'
        }

        self.attribute_map = {
            'tablespace_admin_credential_type': 'tablespaceAdminCredentialType',
            'username': 'username',
            'role': 'role'
        }

        self._tablespace_admin_credential_type = None
        self._username = None
        self._role = None

    @staticmethod
    def get_subtype(object_dictionary):
        """
        Given the hash representation of a subtype of this class,
        use the info in the hash to return the class of the subtype.
        """
        type = object_dictionary['tablespaceAdminCredentialType']

        if type == 'PASSWORD':
            return 'TablespaceAdminPasswordCredentialDetails'

        if type == 'SECRET':
            return 'TablespaceAdminSecretCredentialDetails'
        else:
            return 'TablespaceAdminCredentialDetails'

    @property
    def tablespace_admin_credential_type(self):
        """
        **[Required]** Gets the tablespace_admin_credential_type of this TablespaceAdminCredentialDetails.
        The type of the credential for tablespace administration tasks.

        Allowed values for this property are: "SECRET", "PASSWORD"


        :return: The tablespace_admin_credential_type of this TablespaceAdminCredentialDetails.
        :rtype: str
        """
        return self._tablespace_admin_credential_type

    @tablespace_admin_credential_type.setter
    def tablespace_admin_credential_type(self, tablespace_admin_credential_type):
        """
        Sets the tablespace_admin_credential_type of this TablespaceAdminCredentialDetails.
        The type of the credential for tablespace administration tasks.


        :param tablespace_admin_credential_type: The tablespace_admin_credential_type of this TablespaceAdminCredentialDetails.
        :type: str
        """
        allowed_values = ["SECRET", "PASSWORD"]
        if not value_allowed_none_or_none_sentinel(tablespace_admin_credential_type, allowed_values):
            raise ValueError(
                "Invalid value for `tablespace_admin_credential_type`, must be None or one of {0}"
                .format(allowed_values)
            )
        self._tablespace_admin_credential_type = tablespace_admin_credential_type

    @property
    def username(self):
        """
        **[Required]** Gets the username of this TablespaceAdminCredentialDetails.
        The user to connect to the database.


        :return: The username of this TablespaceAdminCredentialDetails.
        :rtype: str
        """
        return self._username

    @username.setter
    def username(self, username):
        """
        Sets the username of this TablespaceAdminCredentialDetails.
        The user to connect to the database.


        :param username: The username of this TablespaceAdminCredentialDetails.
        :type: str
        """
        self._username = username

    @property
    def role(self):
        """
        **[Required]** Gets the role of this TablespaceAdminCredentialDetails.
        The role of the database user.

        Allowed values for this property are: "NORMAL", "SYSDBA"


        :return: The role of this TablespaceAdminCredentialDetails.
        :rtype: str
        """
        return self._role

    @role.setter
    def role(self, role):
        """
        Sets the role of this TablespaceAdminCredentialDetails.
        The role of the database user.


        :param role: The role of this TablespaceAdminCredentialDetails.
        :type: str
        """
        allowed_values = ["NORMAL", "SYSDBA"]
        if not value_allowed_none_or_none_sentinel(role, allowed_values):
            raise ValueError(
                "Invalid value for `role`, must be None or one of {0}"
                .format(allowed_values)
            )
        self._role = role

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
