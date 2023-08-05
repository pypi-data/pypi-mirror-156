# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class Bastion(object):
    """
    A bastion resource. A bastion provides secured, public access to target resources in the cloud that you cannot otherwise reach from the internet. A bastion resides in a public subnet and establishes the network infrastructure needed to connect a user to a target resource in a private subnet.
    """

    #: A constant which can be used with the lifecycle_state property of a Bastion.
    #: This constant has a value of "CREATING"
    LIFECYCLE_STATE_CREATING = "CREATING"

    #: A constant which can be used with the lifecycle_state property of a Bastion.
    #: This constant has a value of "UPDATING"
    LIFECYCLE_STATE_UPDATING = "UPDATING"

    #: A constant which can be used with the lifecycle_state property of a Bastion.
    #: This constant has a value of "ACTIVE"
    LIFECYCLE_STATE_ACTIVE = "ACTIVE"

    #: A constant which can be used with the lifecycle_state property of a Bastion.
    #: This constant has a value of "DELETING"
    LIFECYCLE_STATE_DELETING = "DELETING"

    #: A constant which can be used with the lifecycle_state property of a Bastion.
    #: This constant has a value of "DELETED"
    LIFECYCLE_STATE_DELETED = "DELETED"

    #: A constant which can be used with the lifecycle_state property of a Bastion.
    #: This constant has a value of "FAILED"
    LIFECYCLE_STATE_FAILED = "FAILED"

    def __init__(self, **kwargs):
        """
        Initializes a new Bastion object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param bastion_type:
            The value to assign to the bastion_type property of this Bastion.
        :type bastion_type: str

        :param id:
            The value to assign to the id property of this Bastion.
        :type id: str

        :param name:
            The value to assign to the name property of this Bastion.
        :type name: str

        :param compartment_id:
            The value to assign to the compartment_id property of this Bastion.
        :type compartment_id: str

        :param target_vcn_id:
            The value to assign to the target_vcn_id property of this Bastion.
        :type target_vcn_id: str

        :param target_subnet_id:
            The value to assign to the target_subnet_id property of this Bastion.
        :type target_subnet_id: str

        :param phone_book_entry:
            The value to assign to the phone_book_entry property of this Bastion.
        :type phone_book_entry: str

        :param client_cidr_block_allow_list:
            The value to assign to the client_cidr_block_allow_list property of this Bastion.
        :type client_cidr_block_allow_list: list[str]

        :param static_jump_host_ip_addresses:
            The value to assign to the static_jump_host_ip_addresses property of this Bastion.
        :type static_jump_host_ip_addresses: list[str]

        :param private_endpoint_ip_address:
            The value to assign to the private_endpoint_ip_address property of this Bastion.
        :type private_endpoint_ip_address: str

        :param max_session_ttl_in_seconds:
            The value to assign to the max_session_ttl_in_seconds property of this Bastion.
        :type max_session_ttl_in_seconds: int

        :param max_sessions_allowed:
            The value to assign to the max_sessions_allowed property of this Bastion.
        :type max_sessions_allowed: int

        :param time_created:
            The value to assign to the time_created property of this Bastion.
        :type time_created: datetime

        :param time_updated:
            The value to assign to the time_updated property of this Bastion.
        :type time_updated: datetime

        :param lifecycle_state:
            The value to assign to the lifecycle_state property of this Bastion.
            Allowed values for this property are: "CREATING", "UPDATING", "ACTIVE", "DELETING", "DELETED", "FAILED", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type lifecycle_state: str

        :param lifecycle_details:
            The value to assign to the lifecycle_details property of this Bastion.
        :type lifecycle_details: str

        :param freeform_tags:
            The value to assign to the freeform_tags property of this Bastion.
        :type freeform_tags: dict(str, str)

        :param defined_tags:
            The value to assign to the defined_tags property of this Bastion.
        :type defined_tags: dict(str, dict(str, object))

        :param system_tags:
            The value to assign to the system_tags property of this Bastion.
        :type system_tags: dict(str, dict(str, object))

        """
        self.swagger_types = {
            'bastion_type': 'str',
            'id': 'str',
            'name': 'str',
            'compartment_id': 'str',
            'target_vcn_id': 'str',
            'target_subnet_id': 'str',
            'phone_book_entry': 'str',
            'client_cidr_block_allow_list': 'list[str]',
            'static_jump_host_ip_addresses': 'list[str]',
            'private_endpoint_ip_address': 'str',
            'max_session_ttl_in_seconds': 'int',
            'max_sessions_allowed': 'int',
            'time_created': 'datetime',
            'time_updated': 'datetime',
            'lifecycle_state': 'str',
            'lifecycle_details': 'str',
            'freeform_tags': 'dict(str, str)',
            'defined_tags': 'dict(str, dict(str, object))',
            'system_tags': 'dict(str, dict(str, object))'
        }

        self.attribute_map = {
            'bastion_type': 'bastionType',
            'id': 'id',
            'name': 'name',
            'compartment_id': 'compartmentId',
            'target_vcn_id': 'targetVcnId',
            'target_subnet_id': 'targetSubnetId',
            'phone_book_entry': 'phoneBookEntry',
            'client_cidr_block_allow_list': 'clientCidrBlockAllowList',
            'static_jump_host_ip_addresses': 'staticJumpHostIpAddresses',
            'private_endpoint_ip_address': 'privateEndpointIpAddress',
            'max_session_ttl_in_seconds': 'maxSessionTtlInSeconds',
            'max_sessions_allowed': 'maxSessionsAllowed',
            'time_created': 'timeCreated',
            'time_updated': 'timeUpdated',
            'lifecycle_state': 'lifecycleState',
            'lifecycle_details': 'lifecycleDetails',
            'freeform_tags': 'freeformTags',
            'defined_tags': 'definedTags',
            'system_tags': 'systemTags'
        }

        self._bastion_type = None
        self._id = None
        self._name = None
        self._compartment_id = None
        self._target_vcn_id = None
        self._target_subnet_id = None
        self._phone_book_entry = None
        self._client_cidr_block_allow_list = None
        self._static_jump_host_ip_addresses = None
        self._private_endpoint_ip_address = None
        self._max_session_ttl_in_seconds = None
        self._max_sessions_allowed = None
        self._time_created = None
        self._time_updated = None
        self._lifecycle_state = None
        self._lifecycle_details = None
        self._freeform_tags = None
        self._defined_tags = None
        self._system_tags = None

    @property
    def bastion_type(self):
        """
        **[Required]** Gets the bastion_type of this Bastion.
        The type of bastion.


        :return: The bastion_type of this Bastion.
        :rtype: str
        """
        return self._bastion_type

    @bastion_type.setter
    def bastion_type(self, bastion_type):
        """
        Sets the bastion_type of this Bastion.
        The type of bastion.


        :param bastion_type: The bastion_type of this Bastion.
        :type: str
        """
        self._bastion_type = bastion_type

    @property
    def id(self):
        """
        **[Required]** Gets the id of this Bastion.
        The unique identifier (OCID) of the bastion, which can't be changed after creation.


        :return: The id of this Bastion.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this Bastion.
        The unique identifier (OCID) of the bastion, which can't be changed after creation.


        :param id: The id of this Bastion.
        :type: str
        """
        self._id = id

    @property
    def name(self):
        """
        **[Required]** Gets the name of this Bastion.
        The name of the bastion, which can't be changed after creation.


        :return: The name of this Bastion.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this Bastion.
        The name of the bastion, which can't be changed after creation.


        :param name: The name of this Bastion.
        :type: str
        """
        self._name = name

    @property
    def compartment_id(self):
        """
        **[Required]** Gets the compartment_id of this Bastion.
        The unique identifier (OCID) of the compartment where the bastion is located.


        :return: The compartment_id of this Bastion.
        :rtype: str
        """
        return self._compartment_id

    @compartment_id.setter
    def compartment_id(self, compartment_id):
        """
        Sets the compartment_id of this Bastion.
        The unique identifier (OCID) of the compartment where the bastion is located.


        :param compartment_id: The compartment_id of this Bastion.
        :type: str
        """
        self._compartment_id = compartment_id

    @property
    def target_vcn_id(self):
        """
        **[Required]** Gets the target_vcn_id of this Bastion.
        The unique identifier (OCID) of the virtual cloud network (VCN) that the bastion connects to.


        :return: The target_vcn_id of this Bastion.
        :rtype: str
        """
        return self._target_vcn_id

    @target_vcn_id.setter
    def target_vcn_id(self, target_vcn_id):
        """
        Sets the target_vcn_id of this Bastion.
        The unique identifier (OCID) of the virtual cloud network (VCN) that the bastion connects to.


        :param target_vcn_id: The target_vcn_id of this Bastion.
        :type: str
        """
        self._target_vcn_id = target_vcn_id

    @property
    def target_subnet_id(self):
        """
        **[Required]** Gets the target_subnet_id of this Bastion.
        The unique identifier (OCID) of the subnet that the bastion connects to.


        :return: The target_subnet_id of this Bastion.
        :rtype: str
        """
        return self._target_subnet_id

    @target_subnet_id.setter
    def target_subnet_id(self, target_subnet_id):
        """
        Sets the target_subnet_id of this Bastion.
        The unique identifier (OCID) of the subnet that the bastion connects to.


        :param target_subnet_id: The target_subnet_id of this Bastion.
        :type: str
        """
        self._target_subnet_id = target_subnet_id

    @property
    def phone_book_entry(self):
        """
        Gets the phone_book_entry of this Bastion.
        The phonebook entry of the customer's team, which can't be changed after creation. Not applicable to `standard` bastions.


        :return: The phone_book_entry of this Bastion.
        :rtype: str
        """
        return self._phone_book_entry

    @phone_book_entry.setter
    def phone_book_entry(self, phone_book_entry):
        """
        Sets the phone_book_entry of this Bastion.
        The phonebook entry of the customer's team, which can't be changed after creation. Not applicable to `standard` bastions.


        :param phone_book_entry: The phone_book_entry of this Bastion.
        :type: str
        """
        self._phone_book_entry = phone_book_entry

    @property
    def client_cidr_block_allow_list(self):
        """
        Gets the client_cidr_block_allow_list of this Bastion.
        A list of address ranges in CIDR notation that you want to allow to connect to sessions hosted by this bastion.


        :return: The client_cidr_block_allow_list of this Bastion.
        :rtype: list[str]
        """
        return self._client_cidr_block_allow_list

    @client_cidr_block_allow_list.setter
    def client_cidr_block_allow_list(self, client_cidr_block_allow_list):
        """
        Sets the client_cidr_block_allow_list of this Bastion.
        A list of address ranges in CIDR notation that you want to allow to connect to sessions hosted by this bastion.


        :param client_cidr_block_allow_list: The client_cidr_block_allow_list of this Bastion.
        :type: list[str]
        """
        self._client_cidr_block_allow_list = client_cidr_block_allow_list

    @property
    def static_jump_host_ip_addresses(self):
        """
        Gets the static_jump_host_ip_addresses of this Bastion.
        A list of IP addresses of the hosts that the bastion has access to. Not applicable to `standard` bastions.


        :return: The static_jump_host_ip_addresses of this Bastion.
        :rtype: list[str]
        """
        return self._static_jump_host_ip_addresses

    @static_jump_host_ip_addresses.setter
    def static_jump_host_ip_addresses(self, static_jump_host_ip_addresses):
        """
        Sets the static_jump_host_ip_addresses of this Bastion.
        A list of IP addresses of the hosts that the bastion has access to. Not applicable to `standard` bastions.


        :param static_jump_host_ip_addresses: The static_jump_host_ip_addresses of this Bastion.
        :type: list[str]
        """
        self._static_jump_host_ip_addresses = static_jump_host_ip_addresses

    @property
    def private_endpoint_ip_address(self):
        """
        Gets the private_endpoint_ip_address of this Bastion.
        The private IP address of the created private endpoint.


        :return: The private_endpoint_ip_address of this Bastion.
        :rtype: str
        """
        return self._private_endpoint_ip_address

    @private_endpoint_ip_address.setter
    def private_endpoint_ip_address(self, private_endpoint_ip_address):
        """
        Sets the private_endpoint_ip_address of this Bastion.
        The private IP address of the created private endpoint.


        :param private_endpoint_ip_address: The private_endpoint_ip_address of this Bastion.
        :type: str
        """
        self._private_endpoint_ip_address = private_endpoint_ip_address

    @property
    def max_session_ttl_in_seconds(self):
        """
        **[Required]** Gets the max_session_ttl_in_seconds of this Bastion.
        The maximum amount of time that any session on the bastion can remain active.


        :return: The max_session_ttl_in_seconds of this Bastion.
        :rtype: int
        """
        return self._max_session_ttl_in_seconds

    @max_session_ttl_in_seconds.setter
    def max_session_ttl_in_seconds(self, max_session_ttl_in_seconds):
        """
        Sets the max_session_ttl_in_seconds of this Bastion.
        The maximum amount of time that any session on the bastion can remain active.


        :param max_session_ttl_in_seconds: The max_session_ttl_in_seconds of this Bastion.
        :type: int
        """
        self._max_session_ttl_in_seconds = max_session_ttl_in_seconds

    @property
    def max_sessions_allowed(self):
        """
        Gets the max_sessions_allowed of this Bastion.
        The maximum number of active sessions allowed on the bastion.


        :return: The max_sessions_allowed of this Bastion.
        :rtype: int
        """
        return self._max_sessions_allowed

    @max_sessions_allowed.setter
    def max_sessions_allowed(self, max_sessions_allowed):
        """
        Sets the max_sessions_allowed of this Bastion.
        The maximum number of active sessions allowed on the bastion.


        :param max_sessions_allowed: The max_sessions_allowed of this Bastion.
        :type: int
        """
        self._max_sessions_allowed = max_sessions_allowed

    @property
    def time_created(self):
        """
        **[Required]** Gets the time_created of this Bastion.
        The time the bastion was created. Format is defined by `RFC3339`__.
        Example: `2020-01-25T21:10:29.600Z`

        __ https://tools.ietf.org/html/rfc3339


        :return: The time_created of this Bastion.
        :rtype: datetime
        """
        return self._time_created

    @time_created.setter
    def time_created(self, time_created):
        """
        Sets the time_created of this Bastion.
        The time the bastion was created. Format is defined by `RFC3339`__.
        Example: `2020-01-25T21:10:29.600Z`

        __ https://tools.ietf.org/html/rfc3339


        :param time_created: The time_created of this Bastion.
        :type: datetime
        """
        self._time_created = time_created

    @property
    def time_updated(self):
        """
        Gets the time_updated of this Bastion.
        The time the bastion was updated. Format is defined by `RFC3339`__.
        Example: `2020-01-25T21:10:29.600Z`

        __ https://tools.ietf.org/html/rfc3339


        :return: The time_updated of this Bastion.
        :rtype: datetime
        """
        return self._time_updated

    @time_updated.setter
    def time_updated(self, time_updated):
        """
        Sets the time_updated of this Bastion.
        The time the bastion was updated. Format is defined by `RFC3339`__.
        Example: `2020-01-25T21:10:29.600Z`

        __ https://tools.ietf.org/html/rfc3339


        :param time_updated: The time_updated of this Bastion.
        :type: datetime
        """
        self._time_updated = time_updated

    @property
    def lifecycle_state(self):
        """
        **[Required]** Gets the lifecycle_state of this Bastion.
        The current state of the bastion.

        Allowed values for this property are: "CREATING", "UPDATING", "ACTIVE", "DELETING", "DELETED", "FAILED", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The lifecycle_state of this Bastion.
        :rtype: str
        """
        return self._lifecycle_state

    @lifecycle_state.setter
    def lifecycle_state(self, lifecycle_state):
        """
        Sets the lifecycle_state of this Bastion.
        The current state of the bastion.


        :param lifecycle_state: The lifecycle_state of this Bastion.
        :type: str
        """
        allowed_values = ["CREATING", "UPDATING", "ACTIVE", "DELETING", "DELETED", "FAILED"]
        if not value_allowed_none_or_none_sentinel(lifecycle_state, allowed_values):
            lifecycle_state = 'UNKNOWN_ENUM_VALUE'
        self._lifecycle_state = lifecycle_state

    @property
    def lifecycle_details(self):
        """
        Gets the lifecycle_details of this Bastion.
        A message describing the current state in more detail.


        :return: The lifecycle_details of this Bastion.
        :rtype: str
        """
        return self._lifecycle_details

    @lifecycle_details.setter
    def lifecycle_details(self, lifecycle_details):
        """
        Sets the lifecycle_details of this Bastion.
        A message describing the current state in more detail.


        :param lifecycle_details: The lifecycle_details of this Bastion.
        :type: str
        """
        self._lifecycle_details = lifecycle_details

    @property
    def freeform_tags(self):
        """
        Gets the freeform_tags of this Bastion.
        Simple key-value pair that is applied without any predefined name, type or scope. Exists for cross-compatibility only.
        Example: `{\"bar-key\": \"value\"}`


        :return: The freeform_tags of this Bastion.
        :rtype: dict(str, str)
        """
        return self._freeform_tags

    @freeform_tags.setter
    def freeform_tags(self, freeform_tags):
        """
        Sets the freeform_tags of this Bastion.
        Simple key-value pair that is applied without any predefined name, type or scope. Exists for cross-compatibility only.
        Example: `{\"bar-key\": \"value\"}`


        :param freeform_tags: The freeform_tags of this Bastion.
        :type: dict(str, str)
        """
        self._freeform_tags = freeform_tags

    @property
    def defined_tags(self):
        """
        Gets the defined_tags of this Bastion.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        Example: `{\"foo-namespace\": {\"bar-key\": \"value\"}}`


        :return: The defined_tags of this Bastion.
        :rtype: dict(str, dict(str, object))
        """
        return self._defined_tags

    @defined_tags.setter
    def defined_tags(self, defined_tags):
        """
        Sets the defined_tags of this Bastion.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        Example: `{\"foo-namespace\": {\"bar-key\": \"value\"}}`


        :param defined_tags: The defined_tags of this Bastion.
        :type: dict(str, dict(str, object))
        """
        self._defined_tags = defined_tags

    @property
    def system_tags(self):
        """
        Gets the system_tags of this Bastion.
        Usage of system tag keys. These predefined keys are scoped to namespaces.
        Example: `{\"orcl-cloud\": {\"free-tier-retained\": \"true\"}}`


        :return: The system_tags of this Bastion.
        :rtype: dict(str, dict(str, object))
        """
        return self._system_tags

    @system_tags.setter
    def system_tags(self, system_tags):
        """
        Sets the system_tags of this Bastion.
        Usage of system tag keys. These predefined keys are scoped to namespaces.
        Example: `{\"orcl-cloud\": {\"free-tier-retained\": \"true\"}}`


        :param system_tags: The system_tags of this Bastion.
        :type: dict(str, dict(str, object))
        """
        self._system_tags = system_tags

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
