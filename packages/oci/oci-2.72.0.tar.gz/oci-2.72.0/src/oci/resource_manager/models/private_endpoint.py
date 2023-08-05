# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class PrivateEndpoint(object):
    """
    A private endpoint. For more information about private endpoints, see `About Private Endpoints`__.

    __ https://docs.cloud.oracle.com/iaas/Content/Network/Concepts/privateaccess.htm#private-endpoints
    """

    #: A constant which can be used with the lifecycle_state property of a PrivateEndpoint.
    #: This constant has a value of "ACTIVE"
    LIFECYCLE_STATE_ACTIVE = "ACTIVE"

    #: A constant which can be used with the lifecycle_state property of a PrivateEndpoint.
    #: This constant has a value of "CREATING"
    LIFECYCLE_STATE_CREATING = "CREATING"

    #: A constant which can be used with the lifecycle_state property of a PrivateEndpoint.
    #: This constant has a value of "DELETING"
    LIFECYCLE_STATE_DELETING = "DELETING"

    #: A constant which can be used with the lifecycle_state property of a PrivateEndpoint.
    #: This constant has a value of "DELETED"
    LIFECYCLE_STATE_DELETED = "DELETED"

    #: A constant which can be used with the lifecycle_state property of a PrivateEndpoint.
    #: This constant has a value of "FAILED"
    LIFECYCLE_STATE_FAILED = "FAILED"

    def __init__(self, **kwargs):
        """
        Initializes a new PrivateEndpoint object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param id:
            The value to assign to the id property of this PrivateEndpoint.
        :type id: str

        :param compartment_id:
            The value to assign to the compartment_id property of this PrivateEndpoint.
        :type compartment_id: str

        :param display_name:
            The value to assign to the display_name property of this PrivateEndpoint.
        :type display_name: str

        :param description:
            The value to assign to the description property of this PrivateEndpoint.
        :type description: str

        :param vcn_id:
            The value to assign to the vcn_id property of this PrivateEndpoint.
        :type vcn_id: str

        :param subnet_id:
            The value to assign to the subnet_id property of this PrivateEndpoint.
        :type subnet_id: str

        :param source_ips:
            The value to assign to the source_ips property of this PrivateEndpoint.
        :type source_ips: list[str]

        :param nsg_id_list:
            The value to assign to the nsg_id_list property of this PrivateEndpoint.
        :type nsg_id_list: list[str]

        :param is_used_with_configuration_source_provider:
            The value to assign to the is_used_with_configuration_source_provider property of this PrivateEndpoint.
        :type is_used_with_configuration_source_provider: bool

        :param dns_zones:
            The value to assign to the dns_zones property of this PrivateEndpoint.
        :type dns_zones: list[str]

        :param time_created:
            The value to assign to the time_created property of this PrivateEndpoint.
        :type time_created: datetime

        :param lifecycle_state:
            The value to assign to the lifecycle_state property of this PrivateEndpoint.
            Allowed values for this property are: "ACTIVE", "CREATING", "DELETING", "DELETED", "FAILED", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type lifecycle_state: str

        :param freeform_tags:
            The value to assign to the freeform_tags property of this PrivateEndpoint.
        :type freeform_tags: dict(str, str)

        :param defined_tags:
            The value to assign to the defined_tags property of this PrivateEndpoint.
        :type defined_tags: dict(str, dict(str, object))

        """
        self.swagger_types = {
            'id': 'str',
            'compartment_id': 'str',
            'display_name': 'str',
            'description': 'str',
            'vcn_id': 'str',
            'subnet_id': 'str',
            'source_ips': 'list[str]',
            'nsg_id_list': 'list[str]',
            'is_used_with_configuration_source_provider': 'bool',
            'dns_zones': 'list[str]',
            'time_created': 'datetime',
            'lifecycle_state': 'str',
            'freeform_tags': 'dict(str, str)',
            'defined_tags': 'dict(str, dict(str, object))'
        }

        self.attribute_map = {
            'id': 'id',
            'compartment_id': 'compartmentId',
            'display_name': 'displayName',
            'description': 'description',
            'vcn_id': 'vcnId',
            'subnet_id': 'subnetId',
            'source_ips': 'sourceIps',
            'nsg_id_list': 'nsgIdList',
            'is_used_with_configuration_source_provider': 'isUsedWithConfigurationSourceProvider',
            'dns_zones': 'dnsZones',
            'time_created': 'timeCreated',
            'lifecycle_state': 'lifecycleState',
            'freeform_tags': 'freeformTags',
            'defined_tags': 'definedTags'
        }

        self._id = None
        self._compartment_id = None
        self._display_name = None
        self._description = None
        self._vcn_id = None
        self._subnet_id = None
        self._source_ips = None
        self._nsg_id_list = None
        self._is_used_with_configuration_source_provider = None
        self._dns_zones = None
        self._time_created = None
        self._lifecycle_state = None
        self._freeform_tags = None
        self._defined_tags = None

    @property
    def id(self):
        """
        **[Required]** Gets the id of this PrivateEndpoint.
        Unique identifier (`OCID`__) of the private endpoint details.

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :return: The id of this PrivateEndpoint.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this PrivateEndpoint.
        Unique identifier (`OCID`__) of the private endpoint details.

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :param id: The id of this PrivateEndpoint.
        :type: str
        """
        self._id = id

    @property
    def compartment_id(self):
        """
        **[Required]** Gets the compartment_id of this PrivateEndpoint.
        The `OCID`__ of the compartment containing this private endpoint details.

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :return: The compartment_id of this PrivateEndpoint.
        :rtype: str
        """
        return self._compartment_id

    @compartment_id.setter
    def compartment_id(self, compartment_id):
        """
        Sets the compartment_id of this PrivateEndpoint.
        The `OCID`__ of the compartment containing this private endpoint details.

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :param compartment_id: The compartment_id of this PrivateEndpoint.
        :type: str
        """
        self._compartment_id = compartment_id

    @property
    def display_name(self):
        """
        Gets the display_name of this PrivateEndpoint.
        A user-friendly name. Does not have to be unique, and it's changeable. Avoid entering confidential information.


        :return: The display_name of this PrivateEndpoint.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """
        Sets the display_name of this PrivateEndpoint.
        A user-friendly name. Does not have to be unique, and it's changeable. Avoid entering confidential information.


        :param display_name: The display_name of this PrivateEndpoint.
        :type: str
        """
        self._display_name = display_name

    @property
    def description(self):
        """
        Gets the description of this PrivateEndpoint.
        Description of the private endpoint. Avoid entering confidential information.


        :return: The description of this PrivateEndpoint.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this PrivateEndpoint.
        Description of the private endpoint. Avoid entering confidential information.


        :param description: The description of this PrivateEndpoint.
        :type: str
        """
        self._description = description

    @property
    def vcn_id(self):
        """
        **[Required]** Gets the vcn_id of this PrivateEndpoint.
        The `OCID`__ of the VCN for the private endpoint.

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :return: The vcn_id of this PrivateEndpoint.
        :rtype: str
        """
        return self._vcn_id

    @vcn_id.setter
    def vcn_id(self, vcn_id):
        """
        Sets the vcn_id of this PrivateEndpoint.
        The `OCID`__ of the VCN for the private endpoint.

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :param vcn_id: The vcn_id of this PrivateEndpoint.
        :type: str
        """
        self._vcn_id = vcn_id

    @property
    def subnet_id(self):
        """
        **[Required]** Gets the subnet_id of this PrivateEndpoint.
        The `OCID`__ of the subnet within the VCN for the private endpoint.

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :return: The subnet_id of this PrivateEndpoint.
        :rtype: str
        """
        return self._subnet_id

    @subnet_id.setter
    def subnet_id(self, subnet_id):
        """
        Sets the subnet_id of this PrivateEndpoint.
        The `OCID`__ of the subnet within the VCN for the private endpoint.

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :param subnet_id: The subnet_id of this PrivateEndpoint.
        :type: str
        """
        self._subnet_id = subnet_id

    @property
    def source_ips(self):
        """
        Gets the source_ips of this PrivateEndpoint.
        The source IPs which resource manager service will use to connect to customer's network. Automatically assigned by Resource Manager Service.


        :return: The source_ips of this PrivateEndpoint.
        :rtype: list[str]
        """
        return self._source_ips

    @source_ips.setter
    def source_ips(self, source_ips):
        """
        Sets the source_ips of this PrivateEndpoint.
        The source IPs which resource manager service will use to connect to customer's network. Automatically assigned by Resource Manager Service.


        :param source_ips: The source_ips of this PrivateEndpoint.
        :type: list[str]
        """
        self._source_ips = source_ips

    @property
    def nsg_id_list(self):
        """
        Gets the nsg_id_list of this PrivateEndpoint.
        An array of network security groups (NSG) that the customer can optionally provide.


        :return: The nsg_id_list of this PrivateEndpoint.
        :rtype: list[str]
        """
        return self._nsg_id_list

    @nsg_id_list.setter
    def nsg_id_list(self, nsg_id_list):
        """
        Sets the nsg_id_list of this PrivateEndpoint.
        An array of network security groups (NSG) that the customer can optionally provide.


        :param nsg_id_list: The nsg_id_list of this PrivateEndpoint.
        :type: list[str]
        """
        self._nsg_id_list = nsg_id_list

    @property
    def is_used_with_configuration_source_provider(self):
        """
        Gets the is_used_with_configuration_source_provider of this PrivateEndpoint.
        When `true`, allows the private endpoint to be used with a configuration source provider.


        :return: The is_used_with_configuration_source_provider of this PrivateEndpoint.
        :rtype: bool
        """
        return self._is_used_with_configuration_source_provider

    @is_used_with_configuration_source_provider.setter
    def is_used_with_configuration_source_provider(self, is_used_with_configuration_source_provider):
        """
        Sets the is_used_with_configuration_source_provider of this PrivateEndpoint.
        When `true`, allows the private endpoint to be used with a configuration source provider.


        :param is_used_with_configuration_source_provider: The is_used_with_configuration_source_provider of this PrivateEndpoint.
        :type: bool
        """
        self._is_used_with_configuration_source_provider = is_used_with_configuration_source_provider

    @property
    def dns_zones(self):
        """
        Gets the dns_zones of this PrivateEndpoint.
        DNS Proxy forwards any DNS FQDN queries over into the consumer DNS resolver if the DNS FQDN is included in the dns zones list otherwise it goes to service provider VCN resolver.


        :return: The dns_zones of this PrivateEndpoint.
        :rtype: list[str]
        """
        return self._dns_zones

    @dns_zones.setter
    def dns_zones(self, dns_zones):
        """
        Sets the dns_zones of this PrivateEndpoint.
        DNS Proxy forwards any DNS FQDN queries over into the consumer DNS resolver if the DNS FQDN is included in the dns zones list otherwise it goes to service provider VCN resolver.


        :param dns_zones: The dns_zones of this PrivateEndpoint.
        :type: list[str]
        """
        self._dns_zones = dns_zones

    @property
    def time_created(self):
        """
        Gets the time_created of this PrivateEndpoint.
        The date and time at which the private endpoint was created.
        Format is defined by RFC3339.
        Example: `2020-11-25T21:10:29.600Z`


        :return: The time_created of this PrivateEndpoint.
        :rtype: datetime
        """
        return self._time_created

    @time_created.setter
    def time_created(self, time_created):
        """
        Sets the time_created of this PrivateEndpoint.
        The date and time at which the private endpoint was created.
        Format is defined by RFC3339.
        Example: `2020-11-25T21:10:29.600Z`


        :param time_created: The time_created of this PrivateEndpoint.
        :type: datetime
        """
        self._time_created = time_created

    @property
    def lifecycle_state(self):
        """
        Gets the lifecycle_state of this PrivateEndpoint.
        The current lifecycle state of the private endpoint.

        Allowed values for this property are: "ACTIVE", "CREATING", "DELETING", "DELETED", "FAILED", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The lifecycle_state of this PrivateEndpoint.
        :rtype: str
        """
        return self._lifecycle_state

    @lifecycle_state.setter
    def lifecycle_state(self, lifecycle_state):
        """
        Sets the lifecycle_state of this PrivateEndpoint.
        The current lifecycle state of the private endpoint.


        :param lifecycle_state: The lifecycle_state of this PrivateEndpoint.
        :type: str
        """
        allowed_values = ["ACTIVE", "CREATING", "DELETING", "DELETED", "FAILED"]
        if not value_allowed_none_or_none_sentinel(lifecycle_state, allowed_values):
            lifecycle_state = 'UNKNOWN_ENUM_VALUE'
        self._lifecycle_state = lifecycle_state

    @property
    def freeform_tags(self):
        """
        Gets the freeform_tags of this PrivateEndpoint.
        Free-form tags associated with the resource. Each tag is a key-value pair with no predefined name, type, or namespace.
        For more information, see `Resource Tags`__.
        Example: `{\"Department\": \"Finance\"}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :return: The freeform_tags of this PrivateEndpoint.
        :rtype: dict(str, str)
        """
        return self._freeform_tags

    @freeform_tags.setter
    def freeform_tags(self, freeform_tags):
        """
        Sets the freeform_tags of this PrivateEndpoint.
        Free-form tags associated with the resource. Each tag is a key-value pair with no predefined name, type, or namespace.
        For more information, see `Resource Tags`__.
        Example: `{\"Department\": \"Finance\"}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :param freeform_tags: The freeform_tags of this PrivateEndpoint.
        :type: dict(str, str)
        """
        self._freeform_tags = freeform_tags

    @property
    def defined_tags(self):
        """
        Gets the defined_tags of this PrivateEndpoint.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        For more information, see `Resource Tags`__.
        Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :return: The defined_tags of this PrivateEndpoint.
        :rtype: dict(str, dict(str, object))
        """
        return self._defined_tags

    @defined_tags.setter
    def defined_tags(self, defined_tags):
        """
        Sets the defined_tags of this PrivateEndpoint.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        For more information, see `Resource Tags`__.
        Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :param defined_tags: The defined_tags of this PrivateEndpoint.
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
