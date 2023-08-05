# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class AuditPolicySummary(object):
    """
    The resource represents all available audit policies relevant for the target database with their corresponding audit conditions.
    The audit policies could be in any one of the following 3 states in the target database
    1) Created and enabled
    2) Created but not enabled
    3) Not created
    For more details on available audit policies, refer to `documentation`__.

    __ https://docs.oracle.com/en/cloud/paas/data-safe/udscs/audit-policies.html#GUID-361A9A9A-7C21-4F5A-8945-9B3A0C472827
    """

    #: A constant which can be used with the lifecycle_state property of a AuditPolicySummary.
    #: This constant has a value of "CREATING"
    LIFECYCLE_STATE_CREATING = "CREATING"

    #: A constant which can be used with the lifecycle_state property of a AuditPolicySummary.
    #: This constant has a value of "UPDATING"
    LIFECYCLE_STATE_UPDATING = "UPDATING"

    #: A constant which can be used with the lifecycle_state property of a AuditPolicySummary.
    #: This constant has a value of "ACTIVE"
    LIFECYCLE_STATE_ACTIVE = "ACTIVE"

    #: A constant which can be used with the lifecycle_state property of a AuditPolicySummary.
    #: This constant has a value of "FAILED"
    LIFECYCLE_STATE_FAILED = "FAILED"

    #: A constant which can be used with the lifecycle_state property of a AuditPolicySummary.
    #: This constant has a value of "NEEDS_ATTENTION"
    LIFECYCLE_STATE_NEEDS_ATTENTION = "NEEDS_ATTENTION"

    #: A constant which can be used with the lifecycle_state property of a AuditPolicySummary.
    #: This constant has a value of "DELETING"
    LIFECYCLE_STATE_DELETING = "DELETING"

    #: A constant which can be used with the lifecycle_state property of a AuditPolicySummary.
    #: This constant has a value of "DELETED"
    LIFECYCLE_STATE_DELETED = "DELETED"

    def __init__(self, **kwargs):
        """
        Initializes a new AuditPolicySummary object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param id:
            The value to assign to the id property of this AuditPolicySummary.
        :type id: str

        :param compartment_id:
            The value to assign to the compartment_id property of this AuditPolicySummary.
        :type compartment_id: str

        :param display_name:
            The value to assign to the display_name property of this AuditPolicySummary.
        :type display_name: str

        :param description:
            The value to assign to the description property of this AuditPolicySummary.
        :type description: str

        :param time_created:
            The value to assign to the time_created property of this AuditPolicySummary.
        :type time_created: datetime

        :param time_updated:
            The value to assign to the time_updated property of this AuditPolicySummary.
        :type time_updated: datetime

        :param lifecycle_state:
            The value to assign to the lifecycle_state property of this AuditPolicySummary.
            Allowed values for this property are: "CREATING", "UPDATING", "ACTIVE", "FAILED", "NEEDS_ATTENTION", "DELETING", "DELETED", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type lifecycle_state: str

        :param lifecycle_details:
            The value to assign to the lifecycle_details property of this AuditPolicySummary.
        :type lifecycle_details: str

        :param target_id:
            The value to assign to the target_id property of this AuditPolicySummary.
        :type target_id: str

        :param is_data_safe_service_account_excluded:
            The value to assign to the is_data_safe_service_account_excluded property of this AuditPolicySummary.
        :type is_data_safe_service_account_excluded: bool

        :param audit_specifications:
            The value to assign to the audit_specifications property of this AuditPolicySummary.
        :type audit_specifications: list[oci.data_safe.models.AuditSpecification]

        :param time_last_provisioned:
            The value to assign to the time_last_provisioned property of this AuditPolicySummary.
        :type time_last_provisioned: datetime

        :param time_last_retrieved:
            The value to assign to the time_last_retrieved property of this AuditPolicySummary.
        :type time_last_retrieved: datetime

        :param freeform_tags:
            The value to assign to the freeform_tags property of this AuditPolicySummary.
        :type freeform_tags: dict(str, str)

        :param defined_tags:
            The value to assign to the defined_tags property of this AuditPolicySummary.
        :type defined_tags: dict(str, dict(str, object))

        """
        self.swagger_types = {
            'id': 'str',
            'compartment_id': 'str',
            'display_name': 'str',
            'description': 'str',
            'time_created': 'datetime',
            'time_updated': 'datetime',
            'lifecycle_state': 'str',
            'lifecycle_details': 'str',
            'target_id': 'str',
            'is_data_safe_service_account_excluded': 'bool',
            'audit_specifications': 'list[AuditSpecification]',
            'time_last_provisioned': 'datetime',
            'time_last_retrieved': 'datetime',
            'freeform_tags': 'dict(str, str)',
            'defined_tags': 'dict(str, dict(str, object))'
        }

        self.attribute_map = {
            'id': 'id',
            'compartment_id': 'compartmentId',
            'display_name': 'displayName',
            'description': 'description',
            'time_created': 'timeCreated',
            'time_updated': 'timeUpdated',
            'lifecycle_state': 'lifecycleState',
            'lifecycle_details': 'lifecycleDetails',
            'target_id': 'targetId',
            'is_data_safe_service_account_excluded': 'isDataSafeServiceAccountExcluded',
            'audit_specifications': 'auditSpecifications',
            'time_last_provisioned': 'timeLastProvisioned',
            'time_last_retrieved': 'timeLastRetrieved',
            'freeform_tags': 'freeformTags',
            'defined_tags': 'definedTags'
        }

        self._id = None
        self._compartment_id = None
        self._display_name = None
        self._description = None
        self._time_created = None
        self._time_updated = None
        self._lifecycle_state = None
        self._lifecycle_details = None
        self._target_id = None
        self._is_data_safe_service_account_excluded = None
        self._audit_specifications = None
        self._time_last_provisioned = None
        self._time_last_retrieved = None
        self._freeform_tags = None
        self._defined_tags = None

    @property
    def id(self):
        """
        **[Required]** Gets the id of this AuditPolicySummary.
        The OCID of the audit policy.


        :return: The id of this AuditPolicySummary.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this AuditPolicySummary.
        The OCID of the audit policy.


        :param id: The id of this AuditPolicySummary.
        :type: str
        """
        self._id = id

    @property
    def compartment_id(self):
        """
        **[Required]** Gets the compartment_id of this AuditPolicySummary.
        The OCID of the compartment containing the audit policy.


        :return: The compartment_id of this AuditPolicySummary.
        :rtype: str
        """
        return self._compartment_id

    @compartment_id.setter
    def compartment_id(self, compartment_id):
        """
        Sets the compartment_id of this AuditPolicySummary.
        The OCID of the compartment containing the audit policy.


        :param compartment_id: The compartment_id of this AuditPolicySummary.
        :type: str
        """
        self._compartment_id = compartment_id

    @property
    def display_name(self):
        """
        **[Required]** Gets the display_name of this AuditPolicySummary.
        The display name of the audit policy.


        :return: The display_name of this AuditPolicySummary.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """
        Sets the display_name of this AuditPolicySummary.
        The display name of the audit policy.


        :param display_name: The display_name of this AuditPolicySummary.
        :type: str
        """
        self._display_name = display_name

    @property
    def description(self):
        """
        Gets the description of this AuditPolicySummary.
        Description of the audit policy.


        :return: The description of this AuditPolicySummary.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this AuditPolicySummary.
        Description of the audit policy.


        :param description: The description of this AuditPolicySummary.
        :type: str
        """
        self._description = description

    @property
    def time_created(self):
        """
        **[Required]** Gets the time_created of this AuditPolicySummary.
        The time the the audit policy was created, in the format defined by RFC3339.


        :return: The time_created of this AuditPolicySummary.
        :rtype: datetime
        """
        return self._time_created

    @time_created.setter
    def time_created(self, time_created):
        """
        Sets the time_created of this AuditPolicySummary.
        The time the the audit policy was created, in the format defined by RFC3339.


        :param time_created: The time_created of this AuditPolicySummary.
        :type: datetime
        """
        self._time_created = time_created

    @property
    def time_updated(self):
        """
        Gets the time_updated of this AuditPolicySummary.
        The last date and time the audit policy was updated, in the format defined by RFC3339.


        :return: The time_updated of this AuditPolicySummary.
        :rtype: datetime
        """
        return self._time_updated

    @time_updated.setter
    def time_updated(self, time_updated):
        """
        Sets the time_updated of this AuditPolicySummary.
        The last date and time the audit policy was updated, in the format defined by RFC3339.


        :param time_updated: The time_updated of this AuditPolicySummary.
        :type: datetime
        """
        self._time_updated = time_updated

    @property
    def lifecycle_state(self):
        """
        **[Required]** Gets the lifecycle_state of this AuditPolicySummary.
        The current state of the audit policy.

        Allowed values for this property are: "CREATING", "UPDATING", "ACTIVE", "FAILED", "NEEDS_ATTENTION", "DELETING", "DELETED", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The lifecycle_state of this AuditPolicySummary.
        :rtype: str
        """
        return self._lifecycle_state

    @lifecycle_state.setter
    def lifecycle_state(self, lifecycle_state):
        """
        Sets the lifecycle_state of this AuditPolicySummary.
        The current state of the audit policy.


        :param lifecycle_state: The lifecycle_state of this AuditPolicySummary.
        :type: str
        """
        allowed_values = ["CREATING", "UPDATING", "ACTIVE", "FAILED", "NEEDS_ATTENTION", "DELETING", "DELETED"]
        if not value_allowed_none_or_none_sentinel(lifecycle_state, allowed_values):
            lifecycle_state = 'UNKNOWN_ENUM_VALUE'
        self._lifecycle_state = lifecycle_state

    @property
    def lifecycle_details(self):
        """
        Gets the lifecycle_details of this AuditPolicySummary.
        Details about the current state of the audit policy in Data Safe.


        :return: The lifecycle_details of this AuditPolicySummary.
        :rtype: str
        """
        return self._lifecycle_details

    @lifecycle_details.setter
    def lifecycle_details(self, lifecycle_details):
        """
        Sets the lifecycle_details of this AuditPolicySummary.
        Details about the current state of the audit policy in Data Safe.


        :param lifecycle_details: The lifecycle_details of this AuditPolicySummary.
        :type: str
        """
        self._lifecycle_details = lifecycle_details

    @property
    def target_id(self):
        """
        **[Required]** Gets the target_id of this AuditPolicySummary.
        The OCID of the target for which the audit policy is created.


        :return: The target_id of this AuditPolicySummary.
        :rtype: str
        """
        return self._target_id

    @target_id.setter
    def target_id(self, target_id):
        """
        Sets the target_id of this AuditPolicySummary.
        The OCID of the target for which the audit policy is created.


        :param target_id: The target_id of this AuditPolicySummary.
        :type: str
        """
        self._target_id = target_id

    @property
    def is_data_safe_service_account_excluded(self):
        """
        **[Required]** Gets the is_data_safe_service_account_excluded of this AuditPolicySummary.
        Option provided to users at the target to indicate whether the Data Safe service account has to be excluded while provisioning the audit policies.


        :return: The is_data_safe_service_account_excluded of this AuditPolicySummary.
        :rtype: bool
        """
        return self._is_data_safe_service_account_excluded

    @is_data_safe_service_account_excluded.setter
    def is_data_safe_service_account_excluded(self, is_data_safe_service_account_excluded):
        """
        Sets the is_data_safe_service_account_excluded of this AuditPolicySummary.
        Option provided to users at the target to indicate whether the Data Safe service account has to be excluded while provisioning the audit policies.


        :param is_data_safe_service_account_excluded: The is_data_safe_service_account_excluded of this AuditPolicySummary.
        :type: bool
        """
        self._is_data_safe_service_account_excluded = is_data_safe_service_account_excluded

    @property
    def audit_specifications(self):
        """
        Gets the audit_specifications of this AuditPolicySummary.
        Represents all available audit policy specifications relevant for the target database. For more details on available audit polcies, refer to `documentation`__.

        __ https://docs.oracle.com/en/cloud/paas/data-safe/udscs/audit-policies.html#GUID-361A9A9A-7C21-4F5A-8945-9B3A0C472827


        :return: The audit_specifications of this AuditPolicySummary.
        :rtype: list[oci.data_safe.models.AuditSpecification]
        """
        return self._audit_specifications

    @audit_specifications.setter
    def audit_specifications(self, audit_specifications):
        """
        Sets the audit_specifications of this AuditPolicySummary.
        Represents all available audit policy specifications relevant for the target database. For more details on available audit polcies, refer to `documentation`__.

        __ https://docs.oracle.com/en/cloud/paas/data-safe/udscs/audit-policies.html#GUID-361A9A9A-7C21-4F5A-8945-9B3A0C472827


        :param audit_specifications: The audit_specifications of this AuditPolicySummary.
        :type: list[oci.data_safe.models.AuditSpecification]
        """
        self._audit_specifications = audit_specifications

    @property
    def time_last_provisioned(self):
        """
        Gets the time_last_provisioned of this AuditPolicySummary.
        Indicates the last provisioning time of audit policies on the target, in the format defined by RFC3339.


        :return: The time_last_provisioned of this AuditPolicySummary.
        :rtype: datetime
        """
        return self._time_last_provisioned

    @time_last_provisioned.setter
    def time_last_provisioned(self, time_last_provisioned):
        """
        Sets the time_last_provisioned of this AuditPolicySummary.
        Indicates the last provisioning time of audit policies on the target, in the format defined by RFC3339.


        :param time_last_provisioned: The time_last_provisioned of this AuditPolicySummary.
        :type: datetime
        """
        self._time_last_provisioned = time_last_provisioned

    @property
    def time_last_retrieved(self):
        """
        Gets the time_last_retrieved of this AuditPolicySummary.
        The time when the audit policies was last retrieved from this target, in the format defined by RFC3339.


        :return: The time_last_retrieved of this AuditPolicySummary.
        :rtype: datetime
        """
        return self._time_last_retrieved

    @time_last_retrieved.setter
    def time_last_retrieved(self, time_last_retrieved):
        """
        Sets the time_last_retrieved of this AuditPolicySummary.
        The time when the audit policies was last retrieved from this target, in the format defined by RFC3339.


        :param time_last_retrieved: The time_last_retrieved of this AuditPolicySummary.
        :type: datetime
        """
        self._time_last_retrieved = time_last_retrieved

    @property
    def freeform_tags(self):
        """
        Gets the freeform_tags of this AuditPolicySummary.
        Free-form tags for this resource. Each tag is a simple key-value pair with no predefined name, type, or namespace. For more information, see `Resource Tags`__

        Example: `{\"Department\": \"Finance\"}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :return: The freeform_tags of this AuditPolicySummary.
        :rtype: dict(str, str)
        """
        return self._freeform_tags

    @freeform_tags.setter
    def freeform_tags(self, freeform_tags):
        """
        Sets the freeform_tags of this AuditPolicySummary.
        Free-form tags for this resource. Each tag is a simple key-value pair with no predefined name, type, or namespace. For more information, see `Resource Tags`__

        Example: `{\"Department\": \"Finance\"}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :param freeform_tags: The freeform_tags of this AuditPolicySummary.
        :type: dict(str, str)
        """
        self._freeform_tags = freeform_tags

    @property
    def defined_tags(self):
        """
        Gets the defined_tags of this AuditPolicySummary.
        Defined tags for this resource. Each key is predefined and scoped to a namespace. For more information, see `Resource Tags`__

        Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :return: The defined_tags of this AuditPolicySummary.
        :rtype: dict(str, dict(str, object))
        """
        return self._defined_tags

    @defined_tags.setter
    def defined_tags(self, defined_tags):
        """
        Sets the defined_tags of this AuditPolicySummary.
        Defined tags for this resource. Each key is predefined and scoped to a namespace. For more information, see `Resource Tags`__

        Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :param defined_tags: The defined_tags of this AuditPolicySummary.
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
