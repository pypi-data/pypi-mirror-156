# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class CreateCertificateAuthorityConfigDetails(object):
    """
    The configuration details for creating a certificate authority (CA).
    """

    #: A constant which can be used with the config_type property of a CreateCertificateAuthorityConfigDetails.
    #: This constant has a value of "ROOT_CA_GENERATED_INTERNALLY"
    CONFIG_TYPE_ROOT_CA_GENERATED_INTERNALLY = "ROOT_CA_GENERATED_INTERNALLY"

    #: A constant which can be used with the config_type property of a CreateCertificateAuthorityConfigDetails.
    #: This constant has a value of "SUBORDINATE_CA_ISSUED_BY_INTERNAL_CA"
    CONFIG_TYPE_SUBORDINATE_CA_ISSUED_BY_INTERNAL_CA = "SUBORDINATE_CA_ISSUED_BY_INTERNAL_CA"

    def __init__(self, **kwargs):
        """
        Initializes a new CreateCertificateAuthorityConfigDetails object with values from keyword arguments. This class has the following subclasses and if you are using this class as input
        to a service operations then you should favor using a subclass over the base class:

        * :class:`~oci.certificates_management.models.CreateRootCaByGeneratingInternallyConfigDetails`
        * :class:`~oci.certificates_management.models.CreateSubordinateCaIssuedByInternalCaConfigDetails`

        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param config_type:
            The value to assign to the config_type property of this CreateCertificateAuthorityConfigDetails.
            Allowed values for this property are: "ROOT_CA_GENERATED_INTERNALLY", "SUBORDINATE_CA_ISSUED_BY_INTERNAL_CA"
        :type config_type: str

        :param version_name:
            The value to assign to the version_name property of this CreateCertificateAuthorityConfigDetails.
        :type version_name: str

        """
        self.swagger_types = {
            'config_type': 'str',
            'version_name': 'str'
        }

        self.attribute_map = {
            'config_type': 'configType',
            'version_name': 'versionName'
        }

        self._config_type = None
        self._version_name = None

    @staticmethod
    def get_subtype(object_dictionary):
        """
        Given the hash representation of a subtype of this class,
        use the info in the hash to return the class of the subtype.
        """
        type = object_dictionary['configType']

        if type == 'ROOT_CA_GENERATED_INTERNALLY':
            return 'CreateRootCaByGeneratingInternallyConfigDetails'

        if type == 'SUBORDINATE_CA_ISSUED_BY_INTERNAL_CA':
            return 'CreateSubordinateCaIssuedByInternalCaConfigDetails'
        else:
            return 'CreateCertificateAuthorityConfigDetails'

    @property
    def config_type(self):
        """
        **[Required]** Gets the config_type of this CreateCertificateAuthorityConfigDetails.
        The origin of the CA.

        Allowed values for this property are: "ROOT_CA_GENERATED_INTERNALLY", "SUBORDINATE_CA_ISSUED_BY_INTERNAL_CA"


        :return: The config_type of this CreateCertificateAuthorityConfigDetails.
        :rtype: str
        """
        return self._config_type

    @config_type.setter
    def config_type(self, config_type):
        """
        Sets the config_type of this CreateCertificateAuthorityConfigDetails.
        The origin of the CA.


        :param config_type: The config_type of this CreateCertificateAuthorityConfigDetails.
        :type: str
        """
        allowed_values = ["ROOT_CA_GENERATED_INTERNALLY", "SUBORDINATE_CA_ISSUED_BY_INTERNAL_CA"]
        if not value_allowed_none_or_none_sentinel(config_type, allowed_values):
            raise ValueError(
                "Invalid value for `config_type`, must be None or one of {0}"
                .format(allowed_values)
            )
        self._config_type = config_type

    @property
    def version_name(self):
        """
        Gets the version_name of this CreateCertificateAuthorityConfigDetails.
        The name of the CA version. When the value is not null, a name is unique across versions of a given CA.


        :return: The version_name of this CreateCertificateAuthorityConfigDetails.
        :rtype: str
        """
        return self._version_name

    @version_name.setter
    def version_name(self, version_name):
        """
        Sets the version_name of this CreateCertificateAuthorityConfigDetails.
        The name of the CA version. When the value is not null, a name is unique across versions of a given CA.


        :param version_name: The version_name of this CreateCertificateAuthorityConfigDetails.
        :type: str
        """
        self._version_name = version_name

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
