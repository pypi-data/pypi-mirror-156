# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class LibraryMaskingFormatSummary(object):
    """
    Summary of a library masking format.
    """

    #: A constant which can be used with the lifecycle_state property of a LibraryMaskingFormatSummary.
    #: This constant has a value of "CREATING"
    LIFECYCLE_STATE_CREATING = "CREATING"

    #: A constant which can be used with the lifecycle_state property of a LibraryMaskingFormatSummary.
    #: This constant has a value of "ACTIVE"
    LIFECYCLE_STATE_ACTIVE = "ACTIVE"

    #: A constant which can be used with the lifecycle_state property of a LibraryMaskingFormatSummary.
    #: This constant has a value of "UPDATING"
    LIFECYCLE_STATE_UPDATING = "UPDATING"

    #: A constant which can be used with the lifecycle_state property of a LibraryMaskingFormatSummary.
    #: This constant has a value of "DELETING"
    LIFECYCLE_STATE_DELETING = "DELETING"

    #: A constant which can be used with the lifecycle_state property of a LibraryMaskingFormatSummary.
    #: This constant has a value of "DELETED"
    LIFECYCLE_STATE_DELETED = "DELETED"

    #: A constant which can be used with the lifecycle_state property of a LibraryMaskingFormatSummary.
    #: This constant has a value of "NEEDS_ATTENTION"
    LIFECYCLE_STATE_NEEDS_ATTENTION = "NEEDS_ATTENTION"

    #: A constant which can be used with the lifecycle_state property of a LibraryMaskingFormatSummary.
    #: This constant has a value of "FAILED"
    LIFECYCLE_STATE_FAILED = "FAILED"

    #: A constant which can be used with the source property of a LibraryMaskingFormatSummary.
    #: This constant has a value of "ORACLE"
    SOURCE_ORACLE = "ORACLE"

    #: A constant which can be used with the source property of a LibraryMaskingFormatSummary.
    #: This constant has a value of "USER"
    SOURCE_USER = "USER"

    def __init__(self, **kwargs):
        """
        Initializes a new LibraryMaskingFormatSummary object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param id:
            The value to assign to the id property of this LibraryMaskingFormatSummary.
        :type id: str

        :param compartment_id:
            The value to assign to the compartment_id property of this LibraryMaskingFormatSummary.
        :type compartment_id: str

        :param display_name:
            The value to assign to the display_name property of this LibraryMaskingFormatSummary.
        :type display_name: str

        :param time_created:
            The value to assign to the time_created property of this LibraryMaskingFormatSummary.
        :type time_created: datetime

        :param time_updated:
            The value to assign to the time_updated property of this LibraryMaskingFormatSummary.
        :type time_updated: datetime

        :param lifecycle_state:
            The value to assign to the lifecycle_state property of this LibraryMaskingFormatSummary.
            Allowed values for this property are: "CREATING", "ACTIVE", "UPDATING", "DELETING", "DELETED", "NEEDS_ATTENTION", "FAILED", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type lifecycle_state: str

        :param description:
            The value to assign to the description property of this LibraryMaskingFormatSummary.
        :type description: str

        :param sensitive_type_ids:
            The value to assign to the sensitive_type_ids property of this LibraryMaskingFormatSummary.
        :type sensitive_type_ids: list[str]

        :param source:
            The value to assign to the source property of this LibraryMaskingFormatSummary.
            Allowed values for this property are: "ORACLE", "USER", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type source: str

        :param freeform_tags:
            The value to assign to the freeform_tags property of this LibraryMaskingFormatSummary.
        :type freeform_tags: dict(str, str)

        :param defined_tags:
            The value to assign to the defined_tags property of this LibraryMaskingFormatSummary.
        :type defined_tags: dict(str, dict(str, object))

        """
        self.swagger_types = {
            'id': 'str',
            'compartment_id': 'str',
            'display_name': 'str',
            'time_created': 'datetime',
            'time_updated': 'datetime',
            'lifecycle_state': 'str',
            'description': 'str',
            'sensitive_type_ids': 'list[str]',
            'source': 'str',
            'freeform_tags': 'dict(str, str)',
            'defined_tags': 'dict(str, dict(str, object))'
        }

        self.attribute_map = {
            'id': 'id',
            'compartment_id': 'compartmentId',
            'display_name': 'displayName',
            'time_created': 'timeCreated',
            'time_updated': 'timeUpdated',
            'lifecycle_state': 'lifecycleState',
            'description': 'description',
            'sensitive_type_ids': 'sensitiveTypeIds',
            'source': 'source',
            'freeform_tags': 'freeformTags',
            'defined_tags': 'definedTags'
        }

        self._id = None
        self._compartment_id = None
        self._display_name = None
        self._time_created = None
        self._time_updated = None
        self._lifecycle_state = None
        self._description = None
        self._sensitive_type_ids = None
        self._source = None
        self._freeform_tags = None
        self._defined_tags = None

    @property
    def id(self):
        """
        **[Required]** Gets the id of this LibraryMaskingFormatSummary.
        The OCID of the library masking format.


        :return: The id of this LibraryMaskingFormatSummary.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this LibraryMaskingFormatSummary.
        The OCID of the library masking format.


        :param id: The id of this LibraryMaskingFormatSummary.
        :type: str
        """
        self._id = id

    @property
    def compartment_id(self):
        """
        **[Required]** Gets the compartment_id of this LibraryMaskingFormatSummary.
        The OCID of the compartment that contains the library masking format.


        :return: The compartment_id of this LibraryMaskingFormatSummary.
        :rtype: str
        """
        return self._compartment_id

    @compartment_id.setter
    def compartment_id(self, compartment_id):
        """
        Sets the compartment_id of this LibraryMaskingFormatSummary.
        The OCID of the compartment that contains the library masking format.


        :param compartment_id: The compartment_id of this LibraryMaskingFormatSummary.
        :type: str
        """
        self._compartment_id = compartment_id

    @property
    def display_name(self):
        """
        **[Required]** Gets the display_name of this LibraryMaskingFormatSummary.
        The display name of the library masking format.


        :return: The display_name of this LibraryMaskingFormatSummary.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """
        Sets the display_name of this LibraryMaskingFormatSummary.
        The display name of the library masking format.


        :param display_name: The display_name of this LibraryMaskingFormatSummary.
        :type: str
        """
        self._display_name = display_name

    @property
    def time_created(self):
        """
        **[Required]** Gets the time_created of this LibraryMaskingFormatSummary.
        The date and time the library masking format was created, in the format defined by `RFC3339`__

        __ https://tools.ietf.org/html/rfc3339


        :return: The time_created of this LibraryMaskingFormatSummary.
        :rtype: datetime
        """
        return self._time_created

    @time_created.setter
    def time_created(self, time_created):
        """
        Sets the time_created of this LibraryMaskingFormatSummary.
        The date and time the library masking format was created, in the format defined by `RFC3339`__

        __ https://tools.ietf.org/html/rfc3339


        :param time_created: The time_created of this LibraryMaskingFormatSummary.
        :type: datetime
        """
        self._time_created = time_created

    @property
    def time_updated(self):
        """
        **[Required]** Gets the time_updated of this LibraryMaskingFormatSummary.
        The date and time the library masking format was updated, in the format defined by `RFC3339`__

        __ https://tools.ietf.org/html/rfc3339


        :return: The time_updated of this LibraryMaskingFormatSummary.
        :rtype: datetime
        """
        return self._time_updated

    @time_updated.setter
    def time_updated(self, time_updated):
        """
        Sets the time_updated of this LibraryMaskingFormatSummary.
        The date and time the library masking format was updated, in the format defined by `RFC3339`__

        __ https://tools.ietf.org/html/rfc3339


        :param time_updated: The time_updated of this LibraryMaskingFormatSummary.
        :type: datetime
        """
        self._time_updated = time_updated

    @property
    def lifecycle_state(self):
        """
        **[Required]** Gets the lifecycle_state of this LibraryMaskingFormatSummary.
        The current state of the library masking format.

        Allowed values for this property are: "CREATING", "ACTIVE", "UPDATING", "DELETING", "DELETED", "NEEDS_ATTENTION", "FAILED", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The lifecycle_state of this LibraryMaskingFormatSummary.
        :rtype: str
        """
        return self._lifecycle_state

    @lifecycle_state.setter
    def lifecycle_state(self, lifecycle_state):
        """
        Sets the lifecycle_state of this LibraryMaskingFormatSummary.
        The current state of the library masking format.


        :param lifecycle_state: The lifecycle_state of this LibraryMaskingFormatSummary.
        :type: str
        """
        allowed_values = ["CREATING", "ACTIVE", "UPDATING", "DELETING", "DELETED", "NEEDS_ATTENTION", "FAILED"]
        if not value_allowed_none_or_none_sentinel(lifecycle_state, allowed_values):
            lifecycle_state = 'UNKNOWN_ENUM_VALUE'
        self._lifecycle_state = lifecycle_state

    @property
    def description(self):
        """
        Gets the description of this LibraryMaskingFormatSummary.
        The description of the library masking format.


        :return: The description of this LibraryMaskingFormatSummary.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this LibraryMaskingFormatSummary.
        The description of the library masking format.


        :param description: The description of this LibraryMaskingFormatSummary.
        :type: str
        """
        self._description = description

    @property
    def sensitive_type_ids(self):
        """
        Gets the sensitive_type_ids of this LibraryMaskingFormatSummary.
        An array of OCIDs of the sensitive types compatible with the library masking format.


        :return: The sensitive_type_ids of this LibraryMaskingFormatSummary.
        :rtype: list[str]
        """
        return self._sensitive_type_ids

    @sensitive_type_ids.setter
    def sensitive_type_ids(self, sensitive_type_ids):
        """
        Sets the sensitive_type_ids of this LibraryMaskingFormatSummary.
        An array of OCIDs of the sensitive types compatible with the library masking format.


        :param sensitive_type_ids: The sensitive_type_ids of this LibraryMaskingFormatSummary.
        :type: list[str]
        """
        self._sensitive_type_ids = sensitive_type_ids

    @property
    def source(self):
        """
        **[Required]** Gets the source of this LibraryMaskingFormatSummary.
        Indicates whether the library masking format is user-defined or predefined.

        Allowed values for this property are: "ORACLE", "USER", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The source of this LibraryMaskingFormatSummary.
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source):
        """
        Sets the source of this LibraryMaskingFormatSummary.
        Indicates whether the library masking format is user-defined or predefined.


        :param source: The source of this LibraryMaskingFormatSummary.
        :type: str
        """
        allowed_values = ["ORACLE", "USER"]
        if not value_allowed_none_or_none_sentinel(source, allowed_values):
            source = 'UNKNOWN_ENUM_VALUE'
        self._source = source

    @property
    def freeform_tags(self):
        """
        Gets the freeform_tags of this LibraryMaskingFormatSummary.
        Free-form tags for this resource. Each tag is a simple key-value pair with no predefined name, type, or namespace. For more information, see `Resource Tags`__

        Example: `{\"Department\": \"Finance\"}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :return: The freeform_tags of this LibraryMaskingFormatSummary.
        :rtype: dict(str, str)
        """
        return self._freeform_tags

    @freeform_tags.setter
    def freeform_tags(self, freeform_tags):
        """
        Sets the freeform_tags of this LibraryMaskingFormatSummary.
        Free-form tags for this resource. Each tag is a simple key-value pair with no predefined name, type, or namespace. For more information, see `Resource Tags`__

        Example: `{\"Department\": \"Finance\"}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :param freeform_tags: The freeform_tags of this LibraryMaskingFormatSummary.
        :type: dict(str, str)
        """
        self._freeform_tags = freeform_tags

    @property
    def defined_tags(self):
        """
        Gets the defined_tags of this LibraryMaskingFormatSummary.
        Defined tags for this resource. Each key is predefined and scoped to a namespace. For more information, see `Resource Tags`__

        Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :return: The defined_tags of this LibraryMaskingFormatSummary.
        :rtype: dict(str, dict(str, object))
        """
        return self._defined_tags

    @defined_tags.setter
    def defined_tags(self, defined_tags):
        """
        Sets the defined_tags of this LibraryMaskingFormatSummary.
        Defined tags for this resource. Each key is predefined and scoped to a namespace. For more information, see `Resource Tags`__

        Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :param defined_tags: The defined_tags of this LibraryMaskingFormatSummary.
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
