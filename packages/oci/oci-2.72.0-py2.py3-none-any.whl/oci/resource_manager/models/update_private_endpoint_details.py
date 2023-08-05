# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class UpdatePrivateEndpointDetails(object):
    """
    Update details for a private endpoint.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new UpdatePrivateEndpointDetails object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param display_name:
            The value to assign to the display_name property of this UpdatePrivateEndpointDetails.
        :type display_name: str

        :param description:
            The value to assign to the description property of this UpdatePrivateEndpointDetails.
        :type description: str

        :param vcn_id:
            The value to assign to the vcn_id property of this UpdatePrivateEndpointDetails.
        :type vcn_id: str

        :param subnet_id:
            The value to assign to the subnet_id property of this UpdatePrivateEndpointDetails.
        :type subnet_id: str

        :param dns_zones:
            The value to assign to the dns_zones property of this UpdatePrivateEndpointDetails.
        :type dns_zones: list[str]

        :param nsg_id_list:
            The value to assign to the nsg_id_list property of this UpdatePrivateEndpointDetails.
        :type nsg_id_list: list[str]

        :param is_used_with_configuration_source_provider:
            The value to assign to the is_used_with_configuration_source_provider property of this UpdatePrivateEndpointDetails.
        :type is_used_with_configuration_source_provider: bool

        :param freeform_tags:
            The value to assign to the freeform_tags property of this UpdatePrivateEndpointDetails.
        :type freeform_tags: dict(str, str)

        :param defined_tags:
            The value to assign to the defined_tags property of this UpdatePrivateEndpointDetails.
        :type defined_tags: dict(str, dict(str, object))

        """
        self.swagger_types = {
            'display_name': 'str',
            'description': 'str',
            'vcn_id': 'str',
            'subnet_id': 'str',
            'dns_zones': 'list[str]',
            'nsg_id_list': 'list[str]',
            'is_used_with_configuration_source_provider': 'bool',
            'freeform_tags': 'dict(str, str)',
            'defined_tags': 'dict(str, dict(str, object))'
        }

        self.attribute_map = {
            'display_name': 'displayName',
            'description': 'description',
            'vcn_id': 'vcnId',
            'subnet_id': 'subnetId',
            'dns_zones': 'dnsZones',
            'nsg_id_list': 'nsgIdList',
            'is_used_with_configuration_source_provider': 'isUsedWithConfigurationSourceProvider',
            'freeform_tags': 'freeformTags',
            'defined_tags': 'definedTags'
        }

        self._display_name = None
        self._description = None
        self._vcn_id = None
        self._subnet_id = None
        self._dns_zones = None
        self._nsg_id_list = None
        self._is_used_with_configuration_source_provider = None
        self._freeform_tags = None
        self._defined_tags = None

    @property
    def display_name(self):
        """
        Gets the display_name of this UpdatePrivateEndpointDetails.
        The private endpoint display name. Avoid entering confidential information.


        :return: The display_name of this UpdatePrivateEndpointDetails.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """
        Sets the display_name of this UpdatePrivateEndpointDetails.
        The private endpoint display name. Avoid entering confidential information.


        :param display_name: The display_name of this UpdatePrivateEndpointDetails.
        :type: str
        """
        self._display_name = display_name

    @property
    def description(self):
        """
        Gets the description of this UpdatePrivateEndpointDetails.
        Description of the private endpoint. Avoid entering confidential information.


        :return: The description of this UpdatePrivateEndpointDetails.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this UpdatePrivateEndpointDetails.
        Description of the private endpoint. Avoid entering confidential information.


        :param description: The description of this UpdatePrivateEndpointDetails.
        :type: str
        """
        self._description = description

    @property
    def vcn_id(self):
        """
        Gets the vcn_id of this UpdatePrivateEndpointDetails.
        The `OCID`__ of the VCN for the private endpoint.

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :return: The vcn_id of this UpdatePrivateEndpointDetails.
        :rtype: str
        """
        return self._vcn_id

    @vcn_id.setter
    def vcn_id(self, vcn_id):
        """
        Sets the vcn_id of this UpdatePrivateEndpointDetails.
        The `OCID`__ of the VCN for the private endpoint.

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :param vcn_id: The vcn_id of this UpdatePrivateEndpointDetails.
        :type: str
        """
        self._vcn_id = vcn_id

    @property
    def subnet_id(self):
        """
        Gets the subnet_id of this UpdatePrivateEndpointDetails.
        The `OCID`__ of the subnet within the VCN for the private endpoint.

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :return: The subnet_id of this UpdatePrivateEndpointDetails.
        :rtype: str
        """
        return self._subnet_id

    @subnet_id.setter
    def subnet_id(self, subnet_id):
        """
        Sets the subnet_id of this UpdatePrivateEndpointDetails.
        The `OCID`__ of the subnet within the VCN for the private endpoint.

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :param subnet_id: The subnet_id of this UpdatePrivateEndpointDetails.
        :type: str
        """
        self._subnet_id = subnet_id

    @property
    def dns_zones(self):
        """
        Gets the dns_zones of this UpdatePrivateEndpointDetails.
        DNS Proxy forwards any DNS FQDN queries over into the consumer DNS resolver if the DNS FQDN is included in the dns zones list otherwise it goes to service provider VCN resolver.


        :return: The dns_zones of this UpdatePrivateEndpointDetails.
        :rtype: list[str]
        """
        return self._dns_zones

    @dns_zones.setter
    def dns_zones(self, dns_zones):
        """
        Sets the dns_zones of this UpdatePrivateEndpointDetails.
        DNS Proxy forwards any DNS FQDN queries over into the consumer DNS resolver if the DNS FQDN is included in the dns zones list otherwise it goes to service provider VCN resolver.


        :param dns_zones: The dns_zones of this UpdatePrivateEndpointDetails.
        :type: list[str]
        """
        self._dns_zones = dns_zones

    @property
    def nsg_id_list(self):
        """
        Gets the nsg_id_list of this UpdatePrivateEndpointDetails.
        An array of network security group (NSG) `OCIDs`__ for the private endpoint.

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :return: The nsg_id_list of this UpdatePrivateEndpointDetails.
        :rtype: list[str]
        """
        return self._nsg_id_list

    @nsg_id_list.setter
    def nsg_id_list(self, nsg_id_list):
        """
        Sets the nsg_id_list of this UpdatePrivateEndpointDetails.
        An array of network security group (NSG) `OCIDs`__ for the private endpoint.

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :param nsg_id_list: The nsg_id_list of this UpdatePrivateEndpointDetails.
        :type: list[str]
        """
        self._nsg_id_list = nsg_id_list

    @property
    def is_used_with_configuration_source_provider(self):
        """
        Gets the is_used_with_configuration_source_provider of this UpdatePrivateEndpointDetails.
        When `true`, allows the private endpoint to be used with a configuration source provider.


        :return: The is_used_with_configuration_source_provider of this UpdatePrivateEndpointDetails.
        :rtype: bool
        """
        return self._is_used_with_configuration_source_provider

    @is_used_with_configuration_source_provider.setter
    def is_used_with_configuration_source_provider(self, is_used_with_configuration_source_provider):
        """
        Sets the is_used_with_configuration_source_provider of this UpdatePrivateEndpointDetails.
        When `true`, allows the private endpoint to be used with a configuration source provider.


        :param is_used_with_configuration_source_provider: The is_used_with_configuration_source_provider of this UpdatePrivateEndpointDetails.
        :type: bool
        """
        self._is_used_with_configuration_source_provider = is_used_with_configuration_source_provider

    @property
    def freeform_tags(self):
        """
        Gets the freeform_tags of this UpdatePrivateEndpointDetails.
        Free-form tags associated with the resource. Each tag is a key-value pair with no predefined name, type, or namespace.
        For more information, see `Resource Tags`__.
        Example: `{\"Department\": \"Finance\"}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :return: The freeform_tags of this UpdatePrivateEndpointDetails.
        :rtype: dict(str, str)
        """
        return self._freeform_tags

    @freeform_tags.setter
    def freeform_tags(self, freeform_tags):
        """
        Sets the freeform_tags of this UpdatePrivateEndpointDetails.
        Free-form tags associated with the resource. Each tag is a key-value pair with no predefined name, type, or namespace.
        For more information, see `Resource Tags`__.
        Example: `{\"Department\": \"Finance\"}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :param freeform_tags: The freeform_tags of this UpdatePrivateEndpointDetails.
        :type: dict(str, str)
        """
        self._freeform_tags = freeform_tags

    @property
    def defined_tags(self):
        """
        Gets the defined_tags of this UpdatePrivateEndpointDetails.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        For more information, see `Resource Tags`__.
        Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :return: The defined_tags of this UpdatePrivateEndpointDetails.
        :rtype: dict(str, dict(str, object))
        """
        return self._defined_tags

    @defined_tags.setter
    def defined_tags(self, defined_tags):
        """
        Sets the defined_tags of this UpdatePrivateEndpointDetails.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        For more information, see `Resource Tags`__.
        Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :param defined_tags: The defined_tags of this UpdatePrivateEndpointDetails.
        :type: dict(str, dict(str, object))
        """
        self._defined_tags = defined_tags

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
