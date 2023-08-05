# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class Quota(object):
    """
    Quotas are applied on top of the service limits and inherited through the nested compartment hierarchy.
    Quotas allow compartment admins to limit resource consumption and set boundaries around acceptable resource use.
    The term \"quota\" can be interpreted as the following:
    * An individual statement written in the declarative language.
    * A collection of statements in a single, named \"quota\" object (which has an Oracle Cloud ID (OCID) assigned to it).
    * The overall body of quotas your organization uses to control access to resources.
    """

    #: A constant which can be used with the lifecycle_state property of a Quota.
    #: This constant has a value of "ACTIVE"
    LIFECYCLE_STATE_ACTIVE = "ACTIVE"

    def __init__(self, **kwargs):
        """
        Initializes a new Quota object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param id:
            The value to assign to the id property of this Quota.
        :type id: str

        :param compartment_id:
            The value to assign to the compartment_id property of this Quota.
        :type compartment_id: str

        :param name:
            The value to assign to the name property of this Quota.
        :type name: str

        :param statements:
            The value to assign to the statements property of this Quota.
        :type statements: list[str]

        :param locks:
            The value to assign to the locks property of this Quota.
        :type locks: list[oci.limits.models.ResourceLock]

        :param description:
            The value to assign to the description property of this Quota.
        :type description: str

        :param time_created:
            The value to assign to the time_created property of this Quota.
        :type time_created: datetime

        :param lifecycle_state:
            The value to assign to the lifecycle_state property of this Quota.
            Allowed values for this property are: "ACTIVE", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type lifecycle_state: str

        :param freeform_tags:
            The value to assign to the freeform_tags property of this Quota.
        :type freeform_tags: dict(str, str)

        :param defined_tags:
            The value to assign to the defined_tags property of this Quota.
        :type defined_tags: dict(str, dict(str, object))

        """
        self.swagger_types = {
            'id': 'str',
            'compartment_id': 'str',
            'name': 'str',
            'statements': 'list[str]',
            'locks': 'list[ResourceLock]',
            'description': 'str',
            'time_created': 'datetime',
            'lifecycle_state': 'str',
            'freeform_tags': 'dict(str, str)',
            'defined_tags': 'dict(str, dict(str, object))'
        }

        self.attribute_map = {
            'id': 'id',
            'compartment_id': 'compartmentId',
            'name': 'name',
            'statements': 'statements',
            'locks': 'locks',
            'description': 'description',
            'time_created': 'timeCreated',
            'lifecycle_state': 'lifecycleState',
            'freeform_tags': 'freeformTags',
            'defined_tags': 'definedTags'
        }

        self._id = None
        self._compartment_id = None
        self._name = None
        self._statements = None
        self._locks = None
        self._description = None
        self._time_created = None
        self._lifecycle_state = None
        self._freeform_tags = None
        self._defined_tags = None

    @property
    def id(self):
        """
        **[Required]** Gets the id of this Quota.
        The OCID of the quota.


        :return: The id of this Quota.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this Quota.
        The OCID of the quota.


        :param id: The id of this Quota.
        :type: str
        """
        self._id = id

    @property
    def compartment_id(self):
        """
        **[Required]** Gets the compartment_id of this Quota.
        The OCID of the compartment containing the resource this quota applies to.


        :return: The compartment_id of this Quota.
        :rtype: str
        """
        return self._compartment_id

    @compartment_id.setter
    def compartment_id(self, compartment_id):
        """
        Sets the compartment_id of this Quota.
        The OCID of the compartment containing the resource this quota applies to.


        :param compartment_id: The compartment_id of this Quota.
        :type: str
        """
        self._compartment_id = compartment_id

    @property
    def name(self):
        """
        **[Required]** Gets the name of this Quota.
        The name you assign to the quota during creation. The name must be unique across all quotas
        in the tenancy and cannot be changed.


        :return: The name of this Quota.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this Quota.
        The name you assign to the quota during creation. The name must be unique across all quotas
        in the tenancy and cannot be changed.


        :param name: The name of this Quota.
        :type: str
        """
        self._name = name

    @property
    def statements(self):
        """
        **[Required]** Gets the statements of this Quota.
        An array of one or more quota statements written in the declarative quota statement language.


        :return: The statements of this Quota.
        :rtype: list[str]
        """
        return self._statements

    @statements.setter
    def statements(self, statements):
        """
        Sets the statements of this Quota.
        An array of one or more quota statements written in the declarative quota statement language.


        :param statements: The statements of this Quota.
        :type: list[str]
        """
        self._statements = statements

    @property
    def locks(self):
        """
        Gets the locks of this Quota.
        Locks associated with this resource.


        :return: The locks of this Quota.
        :rtype: list[oci.limits.models.ResourceLock]
        """
        return self._locks

    @locks.setter
    def locks(self, locks):
        """
        Sets the locks of this Quota.
        Locks associated with this resource.


        :param locks: The locks of this Quota.
        :type: list[oci.limits.models.ResourceLock]
        """
        self._locks = locks

    @property
    def description(self):
        """
        **[Required]** Gets the description of this Quota.
        The description you assign to the quota.


        :return: The description of this Quota.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this Quota.
        The description you assign to the quota.


        :param description: The description of this Quota.
        :type: str
        """
        self._description = description

    @property
    def time_created(self):
        """
        **[Required]** Gets the time_created of this Quota.
        Date and time the quota was created, in the format defined by RFC 3339.
        Example: `2016-08-25T21:10:29.600Z`


        :return: The time_created of this Quota.
        :rtype: datetime
        """
        return self._time_created

    @time_created.setter
    def time_created(self, time_created):
        """
        Sets the time_created of this Quota.
        Date and time the quota was created, in the format defined by RFC 3339.
        Example: `2016-08-25T21:10:29.600Z`


        :param time_created: The time_created of this Quota.
        :type: datetime
        """
        self._time_created = time_created

    @property
    def lifecycle_state(self):
        """
        Gets the lifecycle_state of this Quota.
        The quota's current state. After creating a quota, make sure its `lifecycleState` is set to
        ACTIVE before using it.

        Allowed values for this property are: "ACTIVE", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The lifecycle_state of this Quota.
        :rtype: str
        """
        return self._lifecycle_state

    @lifecycle_state.setter
    def lifecycle_state(self, lifecycle_state):
        """
        Sets the lifecycle_state of this Quota.
        The quota's current state. After creating a quota, make sure its `lifecycleState` is set to
        ACTIVE before using it.


        :param lifecycle_state: The lifecycle_state of this Quota.
        :type: str
        """
        allowed_values = ["ACTIVE"]
        if not value_allowed_none_or_none_sentinel(lifecycle_state, allowed_values):
            lifecycle_state = 'UNKNOWN_ENUM_VALUE'
        self._lifecycle_state = lifecycle_state

    @property
    def freeform_tags(self):
        """
        Gets the freeform_tags of this Quota.
        Free-form tags for this resource. Each tag is a simple key-value pair with no predefined name, type, or namespace.
        For more information, see `Resource Tags`__.
        Example: `{\"Department\": \"Finance\"}`

        __ https://docs.cloud.oracle.com/Content/General/Concepts/resourcetags.htm


        :return: The freeform_tags of this Quota.
        :rtype: dict(str, str)
        """
        return self._freeform_tags

    @freeform_tags.setter
    def freeform_tags(self, freeform_tags):
        """
        Sets the freeform_tags of this Quota.
        Free-form tags for this resource. Each tag is a simple key-value pair with no predefined name, type, or namespace.
        For more information, see `Resource Tags`__.
        Example: `{\"Department\": \"Finance\"}`

        __ https://docs.cloud.oracle.com/Content/General/Concepts/resourcetags.htm


        :param freeform_tags: The freeform_tags of this Quota.
        :type: dict(str, str)
        """
        self._freeform_tags = freeform_tags

    @property
    def defined_tags(self):
        """
        Gets the defined_tags of this Quota.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        For more information, see `Resource Tags`__.
        Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`

        __ https://docs.cloud.oracle.com/Content/General/Concepts/resourcetags.htm


        :return: The defined_tags of this Quota.
        :rtype: dict(str, dict(str, object))
        """
        return self._defined_tags

    @defined_tags.setter
    def defined_tags(self, defined_tags):
        """
        Sets the defined_tags of this Quota.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        For more information, see `Resource Tags`__.
        Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`

        __ https://docs.cloud.oracle.com/Content/General/Concepts/resourcetags.htm


        :param defined_tags: The defined_tags of this Quota.
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
