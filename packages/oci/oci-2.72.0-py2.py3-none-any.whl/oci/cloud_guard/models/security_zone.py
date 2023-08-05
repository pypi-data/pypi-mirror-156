# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class SecurityZone(object):
    """
    A security zone is associated with a security zone recipe and enforces all security zone policies in the recipe. Any actions in the zone's compartment (and any subcompartments in the zone) that violate a policy are denied.
    """

    #: A constant which can be used with the lifecycle_state property of a SecurityZone.
    #: This constant has a value of "CREATING"
    LIFECYCLE_STATE_CREATING = "CREATING"

    #: A constant which can be used with the lifecycle_state property of a SecurityZone.
    #: This constant has a value of "UPDATING"
    LIFECYCLE_STATE_UPDATING = "UPDATING"

    #: A constant which can be used with the lifecycle_state property of a SecurityZone.
    #: This constant has a value of "ACTIVE"
    LIFECYCLE_STATE_ACTIVE = "ACTIVE"

    #: A constant which can be used with the lifecycle_state property of a SecurityZone.
    #: This constant has a value of "INACTIVE"
    LIFECYCLE_STATE_INACTIVE = "INACTIVE"

    #: A constant which can be used with the lifecycle_state property of a SecurityZone.
    #: This constant has a value of "DELETING"
    LIFECYCLE_STATE_DELETING = "DELETING"

    #: A constant which can be used with the lifecycle_state property of a SecurityZone.
    #: This constant has a value of "DELETED"
    LIFECYCLE_STATE_DELETED = "DELETED"

    #: A constant which can be used with the lifecycle_state property of a SecurityZone.
    #: This constant has a value of "FAILED"
    LIFECYCLE_STATE_FAILED = "FAILED"

    def __init__(self, **kwargs):
        """
        Initializes a new SecurityZone object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param id:
            The value to assign to the id property of this SecurityZone.
        :type id: str

        :param display_name:
            The value to assign to the display_name property of this SecurityZone.
        :type display_name: str

        :param description:
            The value to assign to the description property of this SecurityZone.
        :type description: str

        :param compartment_id:
            The value to assign to the compartment_id property of this SecurityZone.
        :type compartment_id: str

        :param security_zone_recipe_id:
            The value to assign to the security_zone_recipe_id property of this SecurityZone.
        :type security_zone_recipe_id: str

        :param security_zone_target_id:
            The value to assign to the security_zone_target_id property of this SecurityZone.
        :type security_zone_target_id: str

        :param inherited_by_compartments:
            The value to assign to the inherited_by_compartments property of this SecurityZone.
        :type inherited_by_compartments: list[str]

        :param time_created:
            The value to assign to the time_created property of this SecurityZone.
        :type time_created: datetime

        :param time_updated:
            The value to assign to the time_updated property of this SecurityZone.
        :type time_updated: datetime

        :param lifecycle_state:
            The value to assign to the lifecycle_state property of this SecurityZone.
            Allowed values for this property are: "CREATING", "UPDATING", "ACTIVE", "INACTIVE", "DELETING", "DELETED", "FAILED", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type lifecycle_state: str

        :param lifecycle_details:
            The value to assign to the lifecycle_details property of this SecurityZone.
        :type lifecycle_details: str

        :param freeform_tags:
            The value to assign to the freeform_tags property of this SecurityZone.
        :type freeform_tags: dict(str, str)

        :param defined_tags:
            The value to assign to the defined_tags property of this SecurityZone.
        :type defined_tags: dict(str, dict(str, object))

        :param system_tags:
            The value to assign to the system_tags property of this SecurityZone.
        :type system_tags: dict(str, dict(str, object))

        """
        self.swagger_types = {
            'id': 'str',
            'display_name': 'str',
            'description': 'str',
            'compartment_id': 'str',
            'security_zone_recipe_id': 'str',
            'security_zone_target_id': 'str',
            'inherited_by_compartments': 'list[str]',
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
            'description': 'description',
            'compartment_id': 'compartmentId',
            'security_zone_recipe_id': 'securityZoneRecipeId',
            'security_zone_target_id': 'securityZoneTargetId',
            'inherited_by_compartments': 'inheritedByCompartments',
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
        self._description = None
        self._compartment_id = None
        self._security_zone_recipe_id = None
        self._security_zone_target_id = None
        self._inherited_by_compartments = None
        self._time_created = None
        self._time_updated = None
        self._lifecycle_state = None
        self._lifecycle_details = None
        self._freeform_tags = None
        self._defined_tags = None
        self._system_tags = None

    @property
    def id(self):
        """
        **[Required]** Gets the id of this SecurityZone.
        Unique identifier that is immutable on creation


        :return: The id of this SecurityZone.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this SecurityZone.
        Unique identifier that is immutable on creation


        :param id: The id of this SecurityZone.
        :type: str
        """
        self._id = id

    @property
    def display_name(self):
        """
        Gets the display_name of this SecurityZone.
        The security zone's name


        :return: The display_name of this SecurityZone.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """
        Sets the display_name of this SecurityZone.
        The security zone's name


        :param display_name: The display_name of this SecurityZone.
        :type: str
        """
        self._display_name = display_name

    @property
    def description(self):
        """
        Gets the description of this SecurityZone.
        The security zone's description


        :return: The description of this SecurityZone.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this SecurityZone.
        The security zone's description


        :param description: The description of this SecurityZone.
        :type: str
        """
        self._description = description

    @property
    def compartment_id(self):
        """
        **[Required]** Gets the compartment_id of this SecurityZone.
        The OCID of the compartment for the security zone


        :return: The compartment_id of this SecurityZone.
        :rtype: str
        """
        return self._compartment_id

    @compartment_id.setter
    def compartment_id(self, compartment_id):
        """
        Sets the compartment_id of this SecurityZone.
        The OCID of the compartment for the security zone


        :param compartment_id: The compartment_id of this SecurityZone.
        :type: str
        """
        self._compartment_id = compartment_id

    @property
    def security_zone_recipe_id(self):
        """
        **[Required]** Gets the security_zone_recipe_id of this SecurityZone.
        The OCID of the recipe (`SecurityRecipe`) for the security zone


        :return: The security_zone_recipe_id of this SecurityZone.
        :rtype: str
        """
        return self._security_zone_recipe_id

    @security_zone_recipe_id.setter
    def security_zone_recipe_id(self, security_zone_recipe_id):
        """
        Sets the security_zone_recipe_id of this SecurityZone.
        The OCID of the recipe (`SecurityRecipe`) for the security zone


        :param security_zone_recipe_id: The security_zone_recipe_id of this SecurityZone.
        :type: str
        """
        self._security_zone_recipe_id = security_zone_recipe_id

    @property
    def security_zone_target_id(self):
        """
        Gets the security_zone_target_id of this SecurityZone.
        The OCID of the target associated with the security zone


        :return: The security_zone_target_id of this SecurityZone.
        :rtype: str
        """
        return self._security_zone_target_id

    @security_zone_target_id.setter
    def security_zone_target_id(self, security_zone_target_id):
        """
        Sets the security_zone_target_id of this SecurityZone.
        The OCID of the target associated with the security zone


        :param security_zone_target_id: The security_zone_target_id of this SecurityZone.
        :type: str
        """
        self._security_zone_target_id = security_zone_target_id

    @property
    def inherited_by_compartments(self):
        """
        Gets the inherited_by_compartments of this SecurityZone.
        List of inherited compartments


        :return: The inherited_by_compartments of this SecurityZone.
        :rtype: list[str]
        """
        return self._inherited_by_compartments

    @inherited_by_compartments.setter
    def inherited_by_compartments(self, inherited_by_compartments):
        """
        Sets the inherited_by_compartments of this SecurityZone.
        List of inherited compartments


        :param inherited_by_compartments: The inherited_by_compartments of this SecurityZone.
        :type: list[str]
        """
        self._inherited_by_compartments = inherited_by_compartments

    @property
    def time_created(self):
        """
        Gets the time_created of this SecurityZone.
        The time the security zone was created. An RFC3339 formatted datetime string.


        :return: The time_created of this SecurityZone.
        :rtype: datetime
        """
        return self._time_created

    @time_created.setter
    def time_created(self, time_created):
        """
        Sets the time_created of this SecurityZone.
        The time the security zone was created. An RFC3339 formatted datetime string.


        :param time_created: The time_created of this SecurityZone.
        :type: datetime
        """
        self._time_created = time_created

    @property
    def time_updated(self):
        """
        Gets the time_updated of this SecurityZone.
        The time the security zone was last updated. An RFC3339 formatted datetime string.


        :return: The time_updated of this SecurityZone.
        :rtype: datetime
        """
        return self._time_updated

    @time_updated.setter
    def time_updated(self, time_updated):
        """
        Sets the time_updated of this SecurityZone.
        The time the security zone was last updated. An RFC3339 formatted datetime string.


        :param time_updated: The time_updated of this SecurityZone.
        :type: datetime
        """
        self._time_updated = time_updated

    @property
    def lifecycle_state(self):
        """
        Gets the lifecycle_state of this SecurityZone.
        The current state of the security zone

        Allowed values for this property are: "CREATING", "UPDATING", "ACTIVE", "INACTIVE", "DELETING", "DELETED", "FAILED", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The lifecycle_state of this SecurityZone.
        :rtype: str
        """
        return self._lifecycle_state

    @lifecycle_state.setter
    def lifecycle_state(self, lifecycle_state):
        """
        Sets the lifecycle_state of this SecurityZone.
        The current state of the security zone


        :param lifecycle_state: The lifecycle_state of this SecurityZone.
        :type: str
        """
        allowed_values = ["CREATING", "UPDATING", "ACTIVE", "INACTIVE", "DELETING", "DELETED", "FAILED"]
        if not value_allowed_none_or_none_sentinel(lifecycle_state, allowed_values):
            lifecycle_state = 'UNKNOWN_ENUM_VALUE'
        self._lifecycle_state = lifecycle_state

    @property
    def lifecycle_details(self):
        """
        Gets the lifecycle_details of this SecurityZone.
        A message describing the current state in more detail. For example, this can be used to provide actionable information for a zone in the `Failed` state.


        :return: The lifecycle_details of this SecurityZone.
        :rtype: str
        """
        return self._lifecycle_details

    @lifecycle_details.setter
    def lifecycle_details(self, lifecycle_details):
        """
        Sets the lifecycle_details of this SecurityZone.
        A message describing the current state in more detail. For example, this can be used to provide actionable information for a zone in the `Failed` state.


        :param lifecycle_details: The lifecycle_details of this SecurityZone.
        :type: str
        """
        self._lifecycle_details = lifecycle_details

    @property
    def freeform_tags(self):
        """
        Gets the freeform_tags of this SecurityZone.
        Simple key-value pair that is applied without any predefined name, type or scope. Exists for cross-compatibility only.
        Example: `{\"bar-key\": \"value\"}`

        Avoid entering confidential information.


        :return: The freeform_tags of this SecurityZone.
        :rtype: dict(str, str)
        """
        return self._freeform_tags

    @freeform_tags.setter
    def freeform_tags(self, freeform_tags):
        """
        Sets the freeform_tags of this SecurityZone.
        Simple key-value pair that is applied without any predefined name, type or scope. Exists for cross-compatibility only.
        Example: `{\"bar-key\": \"value\"}`

        Avoid entering confidential information.


        :param freeform_tags: The freeform_tags of this SecurityZone.
        :type: dict(str, str)
        """
        self._freeform_tags = freeform_tags

    @property
    def defined_tags(self):
        """
        Gets the defined_tags of this SecurityZone.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        Example: `{\"foo-namespace\": {\"bar-key\": \"value\"}}`


        :return: The defined_tags of this SecurityZone.
        :rtype: dict(str, dict(str, object))
        """
        return self._defined_tags

    @defined_tags.setter
    def defined_tags(self, defined_tags):
        """
        Sets the defined_tags of this SecurityZone.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        Example: `{\"foo-namespace\": {\"bar-key\": \"value\"}}`


        :param defined_tags: The defined_tags of this SecurityZone.
        :type: dict(str, dict(str, object))
        """
        self._defined_tags = defined_tags

    @property
    def system_tags(self):
        """
        Gets the system_tags of this SecurityZone.
        System tags for this resource. Each key is predefined and scoped to a namespace.
        For more information, see `Resource Tags`__.
        System tags can be viewed by users, but can only be created by the system.

        Example: `{\"orcl-cloud\": {\"free-tier-retained\": \"true\"}}`

        __ https://docs.cloud.oracle.com/Content/General/Concepts/resourcetags.htm


        :return: The system_tags of this SecurityZone.
        :rtype: dict(str, dict(str, object))
        """
        return self._system_tags

    @system_tags.setter
    def system_tags(self, system_tags):
        """
        Sets the system_tags of this SecurityZone.
        System tags for this resource. Each key is predefined and scoped to a namespace.
        For more information, see `Resource Tags`__.
        System tags can be viewed by users, but can only be created by the system.

        Example: `{\"orcl-cloud\": {\"free-tier-retained\": \"true\"}}`

        __ https://docs.cloud.oracle.com/Content/General/Concepts/resourcetags.htm


        :param system_tags: The system_tags of this SecurityZone.
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
