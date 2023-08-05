# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class WebAppFirewall(object):
    """
    A resource connecting a WebAppFirewallPolicy to a backend of particular type, applying that policy's coverage to the backend.
    """

    #: A constant which can be used with the backend_type property of a WebAppFirewall.
    #: This constant has a value of "LOAD_BALANCER"
    BACKEND_TYPE_LOAD_BALANCER = "LOAD_BALANCER"

    #: A constant which can be used with the lifecycle_state property of a WebAppFirewall.
    #: This constant has a value of "CREATING"
    LIFECYCLE_STATE_CREATING = "CREATING"

    #: A constant which can be used with the lifecycle_state property of a WebAppFirewall.
    #: This constant has a value of "UPDATING"
    LIFECYCLE_STATE_UPDATING = "UPDATING"

    #: A constant which can be used with the lifecycle_state property of a WebAppFirewall.
    #: This constant has a value of "ACTIVE"
    LIFECYCLE_STATE_ACTIVE = "ACTIVE"

    #: A constant which can be used with the lifecycle_state property of a WebAppFirewall.
    #: This constant has a value of "DELETING"
    LIFECYCLE_STATE_DELETING = "DELETING"

    #: A constant which can be used with the lifecycle_state property of a WebAppFirewall.
    #: This constant has a value of "DELETED"
    LIFECYCLE_STATE_DELETED = "DELETED"

    #: A constant which can be used with the lifecycle_state property of a WebAppFirewall.
    #: This constant has a value of "FAILED"
    LIFECYCLE_STATE_FAILED = "FAILED"

    def __init__(self, **kwargs):
        """
        Initializes a new WebAppFirewall object with values from keyword arguments. This class has the following subclasses and if you are using this class as input
        to a service operations then you should favor using a subclass over the base class:

        * :class:`~oci.waf.models.WebAppFirewallLoadBalancer`

        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param id:
            The value to assign to the id property of this WebAppFirewall.
        :type id: str

        :param display_name:
            The value to assign to the display_name property of this WebAppFirewall.
        :type display_name: str

        :param compartment_id:
            The value to assign to the compartment_id property of this WebAppFirewall.
        :type compartment_id: str

        :param backend_type:
            The value to assign to the backend_type property of this WebAppFirewall.
            Allowed values for this property are: "LOAD_BALANCER", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type backend_type: str

        :param web_app_firewall_policy_id:
            The value to assign to the web_app_firewall_policy_id property of this WebAppFirewall.
        :type web_app_firewall_policy_id: str

        :param time_created:
            The value to assign to the time_created property of this WebAppFirewall.
        :type time_created: datetime

        :param time_updated:
            The value to assign to the time_updated property of this WebAppFirewall.
        :type time_updated: datetime

        :param lifecycle_state:
            The value to assign to the lifecycle_state property of this WebAppFirewall.
            Allowed values for this property are: "CREATING", "UPDATING", "ACTIVE", "DELETING", "DELETED", "FAILED", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type lifecycle_state: str

        :param lifecycle_details:
            The value to assign to the lifecycle_details property of this WebAppFirewall.
        :type lifecycle_details: str

        :param freeform_tags:
            The value to assign to the freeform_tags property of this WebAppFirewall.
        :type freeform_tags: dict(str, str)

        :param defined_tags:
            The value to assign to the defined_tags property of this WebAppFirewall.
        :type defined_tags: dict(str, dict(str, object))

        :param system_tags:
            The value to assign to the system_tags property of this WebAppFirewall.
        :type system_tags: dict(str, dict(str, object))

        """
        self.swagger_types = {
            'id': 'str',
            'display_name': 'str',
            'compartment_id': 'str',
            'backend_type': 'str',
            'web_app_firewall_policy_id': 'str',
            'time_created': 'datetime',
            'time_updated': 'datetime',
            'lifecycle_state': 'str',
            'lifecycle_details': 'str',
            'freeform_tags': 'dict(str, str)',
            'defined_tags': 'dict(str, dict(str, object))',
            'system_tags': 'dict(str, dict(str, object))'
        }

        self.attribute_map = {
            'id': 'id',
            'display_name': 'displayName',
            'compartment_id': 'compartmentId',
            'backend_type': 'backendType',
            'web_app_firewall_policy_id': 'webAppFirewallPolicyId',
            'time_created': 'timeCreated',
            'time_updated': 'timeUpdated',
            'lifecycle_state': 'lifecycleState',
            'lifecycle_details': 'lifecycleDetails',
            'freeform_tags': 'freeformTags',
            'defined_tags': 'definedTags',
            'system_tags': 'systemTags'
        }

        self._id = None
        self._display_name = None
        self._compartment_id = None
        self._backend_type = None
        self._web_app_firewall_policy_id = None
        self._time_created = None
        self._time_updated = None
        self._lifecycle_state = None
        self._lifecycle_details = None
        self._freeform_tags = None
        self._defined_tags = None
        self._system_tags = None

    @staticmethod
    def get_subtype(object_dictionary):
        """
        Given the hash representation of a subtype of this class,
        use the info in the hash to return the class of the subtype.
        """
        type = object_dictionary['backendType']

        if type == 'LOAD_BALANCER':
            return 'WebAppFirewallLoadBalancer'
        else:
            return 'WebAppFirewall'

    @property
    def id(self):
        """
        **[Required]** Gets the id of this WebAppFirewall.
        The `OCID`__ of the WebAppFirewall.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :return: The id of this WebAppFirewall.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this WebAppFirewall.
        The `OCID`__ of the WebAppFirewall.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :param id: The id of this WebAppFirewall.
        :type: str
        """
        self._id = id

    @property
    def display_name(self):
        """
        **[Required]** Gets the display_name of this WebAppFirewall.
        WebAppFirewall display name, can be renamed.


        :return: The display_name of this WebAppFirewall.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """
        Sets the display_name of this WebAppFirewall.
        WebAppFirewall display name, can be renamed.


        :param display_name: The display_name of this WebAppFirewall.
        :type: str
        """
        self._display_name = display_name

    @property
    def compartment_id(self):
        """
        **[Required]** Gets the compartment_id of this WebAppFirewall.
        The `OCID`__ of the compartment.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :return: The compartment_id of this WebAppFirewall.
        :rtype: str
        """
        return self._compartment_id

    @compartment_id.setter
    def compartment_id(self, compartment_id):
        """
        Sets the compartment_id of this WebAppFirewall.
        The `OCID`__ of the compartment.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :param compartment_id: The compartment_id of this WebAppFirewall.
        :type: str
        """
        self._compartment_id = compartment_id

    @property
    def backend_type(self):
        """
        **[Required]** Gets the backend_type of this WebAppFirewall.
        Type of the WebAppFirewall, as example LOAD_BALANCER.

        Allowed values for this property are: "LOAD_BALANCER", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The backend_type of this WebAppFirewall.
        :rtype: str
        """
        return self._backend_type

    @backend_type.setter
    def backend_type(self, backend_type):
        """
        Sets the backend_type of this WebAppFirewall.
        Type of the WebAppFirewall, as example LOAD_BALANCER.


        :param backend_type: The backend_type of this WebAppFirewall.
        :type: str
        """
        allowed_values = ["LOAD_BALANCER"]
        if not value_allowed_none_or_none_sentinel(backend_type, allowed_values):
            backend_type = 'UNKNOWN_ENUM_VALUE'
        self._backend_type = backend_type

    @property
    def web_app_firewall_policy_id(self):
        """
        **[Required]** Gets the web_app_firewall_policy_id of this WebAppFirewall.
        The `OCID`__ of WebAppFirewallPolicy, which is attached to the resource.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :return: The web_app_firewall_policy_id of this WebAppFirewall.
        :rtype: str
        """
        return self._web_app_firewall_policy_id

    @web_app_firewall_policy_id.setter
    def web_app_firewall_policy_id(self, web_app_firewall_policy_id):
        """
        Sets the web_app_firewall_policy_id of this WebAppFirewall.
        The `OCID`__ of WebAppFirewallPolicy, which is attached to the resource.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :param web_app_firewall_policy_id: The web_app_firewall_policy_id of this WebAppFirewall.
        :type: str
        """
        self._web_app_firewall_policy_id = web_app_firewall_policy_id

    @property
    def time_created(self):
        """
        **[Required]** Gets the time_created of this WebAppFirewall.
        The time the WebAppFirewall was created. An RFC3339 formatted datetime string.


        :return: The time_created of this WebAppFirewall.
        :rtype: datetime
        """
        return self._time_created

    @time_created.setter
    def time_created(self, time_created):
        """
        Sets the time_created of this WebAppFirewall.
        The time the WebAppFirewall was created. An RFC3339 formatted datetime string.


        :param time_created: The time_created of this WebAppFirewall.
        :type: datetime
        """
        self._time_created = time_created

    @property
    def time_updated(self):
        """
        Gets the time_updated of this WebAppFirewall.
        The time the WebAppFirewall was updated. An RFC3339 formatted datetime string.


        :return: The time_updated of this WebAppFirewall.
        :rtype: datetime
        """
        return self._time_updated

    @time_updated.setter
    def time_updated(self, time_updated):
        """
        Sets the time_updated of this WebAppFirewall.
        The time the WebAppFirewall was updated. An RFC3339 formatted datetime string.


        :param time_updated: The time_updated of this WebAppFirewall.
        :type: datetime
        """
        self._time_updated = time_updated

    @property
    def lifecycle_state(self):
        """
        **[Required]** Gets the lifecycle_state of this WebAppFirewall.
        The current state of the WebAppFirewall.

        Allowed values for this property are: "CREATING", "UPDATING", "ACTIVE", "DELETING", "DELETED", "FAILED", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The lifecycle_state of this WebAppFirewall.
        :rtype: str
        """
        return self._lifecycle_state

    @lifecycle_state.setter
    def lifecycle_state(self, lifecycle_state):
        """
        Sets the lifecycle_state of this WebAppFirewall.
        The current state of the WebAppFirewall.


        :param lifecycle_state: The lifecycle_state of this WebAppFirewall.
        :type: str
        """
        allowed_values = ["CREATING", "UPDATING", "ACTIVE", "DELETING", "DELETED", "FAILED"]
        if not value_allowed_none_or_none_sentinel(lifecycle_state, allowed_values):
            lifecycle_state = 'UNKNOWN_ENUM_VALUE'
        self._lifecycle_state = lifecycle_state

    @property
    def lifecycle_details(self):
        """
        Gets the lifecycle_details of this WebAppFirewall.
        A message describing the current state in more detail.
        For example, can be used to provide actionable information for a resource in FAILED state.


        :return: The lifecycle_details of this WebAppFirewall.
        :rtype: str
        """
        return self._lifecycle_details

    @lifecycle_details.setter
    def lifecycle_details(self, lifecycle_details):
        """
        Sets the lifecycle_details of this WebAppFirewall.
        A message describing the current state in more detail.
        For example, can be used to provide actionable information for a resource in FAILED state.


        :param lifecycle_details: The lifecycle_details of this WebAppFirewall.
        :type: str
        """
        self._lifecycle_details = lifecycle_details

    @property
    def freeform_tags(self):
        """
        **[Required]** Gets the freeform_tags of this WebAppFirewall.
        Simple key-value pair that is applied without any predefined name, type or scope. Exists for cross-compatibility only.
        Example: `{\"bar-key\": \"value\"}`


        :return: The freeform_tags of this WebAppFirewall.
        :rtype: dict(str, str)
        """
        return self._freeform_tags

    @freeform_tags.setter
    def freeform_tags(self, freeform_tags):
        """
        Sets the freeform_tags of this WebAppFirewall.
        Simple key-value pair that is applied without any predefined name, type or scope. Exists for cross-compatibility only.
        Example: `{\"bar-key\": \"value\"}`


        :param freeform_tags: The freeform_tags of this WebAppFirewall.
        :type: dict(str, str)
        """
        self._freeform_tags = freeform_tags

    @property
    def defined_tags(self):
        """
        **[Required]** Gets the defined_tags of this WebAppFirewall.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        Example: `{\"foo-namespace\": {\"bar-key\": \"value\"}}`


        :return: The defined_tags of this WebAppFirewall.
        :rtype: dict(str, dict(str, object))
        """
        return self._defined_tags

    @defined_tags.setter
    def defined_tags(self, defined_tags):
        """
        Sets the defined_tags of this WebAppFirewall.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        Example: `{\"foo-namespace\": {\"bar-key\": \"value\"}}`


        :param defined_tags: The defined_tags of this WebAppFirewall.
        :type: dict(str, dict(str, object))
        """
        self._defined_tags = defined_tags

    @property
    def system_tags(self):
        """
        **[Required]** Gets the system_tags of this WebAppFirewall.
        Usage of system tag keys. These predefined keys are scoped to namespaces.
        Example: `{\"orcl-cloud\": {\"free-tier-retained\": \"true\"}}`


        :return: The system_tags of this WebAppFirewall.
        :rtype: dict(str, dict(str, object))
        """
        return self._system_tags

    @system_tags.setter
    def system_tags(self, system_tags):
        """
        Sets the system_tags of this WebAppFirewall.
        Usage of system tag keys. These predefined keys are scoped to namespaces.
        Example: `{\"orcl-cloud\": {\"free-tier-retained\": \"true\"}}`


        :param system_tags: The system_tags of this WebAppFirewall.
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
