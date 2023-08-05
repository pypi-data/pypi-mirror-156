# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class TenancyAttachment(object):
    """
    Tenancy attachment associates a tenancy to a governance rule via an inclusion criterion.
    """

    #: A constant which can be used with the lifecycle_state property of a TenancyAttachment.
    #: This constant has a value of "CREATING"
    LIFECYCLE_STATE_CREATING = "CREATING"

    #: A constant which can be used with the lifecycle_state property of a TenancyAttachment.
    #: This constant has a value of "ACTIVE"
    LIFECYCLE_STATE_ACTIVE = "ACTIVE"

    #: A constant which can be used with the lifecycle_state property of a TenancyAttachment.
    #: This constant has a value of "UPDATING"
    LIFECYCLE_STATE_UPDATING = "UPDATING"

    #: A constant which can be used with the lifecycle_state property of a TenancyAttachment.
    #: This constant has a value of "NEEDS_ATTENTION"
    LIFECYCLE_STATE_NEEDS_ATTENTION = "NEEDS_ATTENTION"

    #: A constant which can be used with the lifecycle_state property of a TenancyAttachment.
    #: This constant has a value of "DELETING"
    LIFECYCLE_STATE_DELETING = "DELETING"

    #: A constant which can be used with the lifecycle_state property of a TenancyAttachment.
    #: This constant has a value of "DELETED"
    LIFECYCLE_STATE_DELETED = "DELETED"

    def __init__(self, **kwargs):
        """
        Initializes a new TenancyAttachment object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param id:
            The value to assign to the id property of this TenancyAttachment.
        :type id: str

        :param compartment_id:
            The value to assign to the compartment_id property of this TenancyAttachment.
        :type compartment_id: str

        :param governance_rule_id:
            The value to assign to the governance_rule_id property of this TenancyAttachment.
        :type governance_rule_id: str

        :param tenancy_id:
            The value to assign to the tenancy_id property of this TenancyAttachment.
        :type tenancy_id: str

        :param lifecycle_state:
            The value to assign to the lifecycle_state property of this TenancyAttachment.
            Allowed values for this property are: "CREATING", "ACTIVE", "UPDATING", "NEEDS_ATTENTION", "DELETING", "DELETED", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type lifecycle_state: str

        :param time_created:
            The value to assign to the time_created property of this TenancyAttachment.
        :type time_created: datetime

        :param time_updated:
            The value to assign to the time_updated property of this TenancyAttachment.
        :type time_updated: datetime

        :param time_last_attempted:
            The value to assign to the time_last_attempted property of this TenancyAttachment.
        :type time_last_attempted: datetime

        """
        self.swagger_types = {
            'id': 'str',
            'compartment_id': 'str',
            'governance_rule_id': 'str',
            'tenancy_id': 'str',
            'lifecycle_state': 'str',
            'time_created': 'datetime',
            'time_updated': 'datetime',
            'time_last_attempted': 'datetime'
        }

        self.attribute_map = {
            'id': 'id',
            'compartment_id': 'compartmentId',
            'governance_rule_id': 'governanceRuleId',
            'tenancy_id': 'tenancyId',
            'lifecycle_state': 'lifecycleState',
            'time_created': 'timeCreated',
            'time_updated': 'timeUpdated',
            'time_last_attempted': 'timeLastAttempted'
        }

        self._id = None
        self._compartment_id = None
        self._governance_rule_id = None
        self._tenancy_id = None
        self._lifecycle_state = None
        self._time_created = None
        self._time_updated = None
        self._time_last_attempted = None

    @property
    def id(self):
        """
        **[Required]** Gets the id of this TenancyAttachment.
        The Oracle ID (`OCID`__) of the tenancy attachment.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :return: The id of this TenancyAttachment.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this TenancyAttachment.
        The Oracle ID (`OCID`__) of the tenancy attachment.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :param id: The id of this TenancyAttachment.
        :type: str
        """
        self._id = id

    @property
    def compartment_id(self):
        """
        **[Required]** Gets the compartment_id of this TenancyAttachment.
        The Oracle ID (`OCID`__) of the root compartment containing the tenancy attachment.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :return: The compartment_id of this TenancyAttachment.
        :rtype: str
        """
        return self._compartment_id

    @compartment_id.setter
    def compartment_id(self, compartment_id):
        """
        Sets the compartment_id of this TenancyAttachment.
        The Oracle ID (`OCID`__) of the root compartment containing the tenancy attachment.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :param compartment_id: The compartment_id of this TenancyAttachment.
        :type: str
        """
        self._compartment_id = compartment_id

    @property
    def governance_rule_id(self):
        """
        **[Required]** Gets the governance_rule_id of this TenancyAttachment.
        The Oracle ID (`OCID`__) of the governance rule. Every tenancy attachment is associated with a governance rule.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :return: The governance_rule_id of this TenancyAttachment.
        :rtype: str
        """
        return self._governance_rule_id

    @governance_rule_id.setter
    def governance_rule_id(self, governance_rule_id):
        """
        Sets the governance_rule_id of this TenancyAttachment.
        The Oracle ID (`OCID`__) of the governance rule. Every tenancy attachment is associated with a governance rule.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :param governance_rule_id: The governance_rule_id of this TenancyAttachment.
        :type: str
        """
        self._governance_rule_id = governance_rule_id

    @property
    def tenancy_id(self):
        """
        **[Required]** Gets the tenancy_id of this TenancyAttachment.
        The Oracle ID (`OCID`__) of the tenancy to which the governance rule is attached.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :return: The tenancy_id of this TenancyAttachment.
        :rtype: str
        """
        return self._tenancy_id

    @tenancy_id.setter
    def tenancy_id(self, tenancy_id):
        """
        Sets the tenancy_id of this TenancyAttachment.
        The Oracle ID (`OCID`__) of the tenancy to which the governance rule is attached.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :param tenancy_id: The tenancy_id of this TenancyAttachment.
        :type: str
        """
        self._tenancy_id = tenancy_id

    @property
    def lifecycle_state(self):
        """
        **[Required]** Gets the lifecycle_state of this TenancyAttachment.
        The current state of the tenancy attachment.

        Allowed values for this property are: "CREATING", "ACTIVE", "UPDATING", "NEEDS_ATTENTION", "DELETING", "DELETED", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The lifecycle_state of this TenancyAttachment.
        :rtype: str
        """
        return self._lifecycle_state

    @lifecycle_state.setter
    def lifecycle_state(self, lifecycle_state):
        """
        Sets the lifecycle_state of this TenancyAttachment.
        The current state of the tenancy attachment.


        :param lifecycle_state: The lifecycle_state of this TenancyAttachment.
        :type: str
        """
        allowed_values = ["CREATING", "ACTIVE", "UPDATING", "NEEDS_ATTENTION", "DELETING", "DELETED"]
        if not value_allowed_none_or_none_sentinel(lifecycle_state, allowed_values):
            lifecycle_state = 'UNKNOWN_ENUM_VALUE'
        self._lifecycle_state = lifecycle_state

    @property
    def time_created(self):
        """
        **[Required]** Gets the time_created of this TenancyAttachment.
        Date and time the tenancy attachment was created. An RFC3339 formatted datetime string.

        Example: `2016-08-25T21:10:29.600Z`


        :return: The time_created of this TenancyAttachment.
        :rtype: datetime
        """
        return self._time_created

    @time_created.setter
    def time_created(self, time_created):
        """
        Sets the time_created of this TenancyAttachment.
        Date and time the tenancy attachment was created. An RFC3339 formatted datetime string.

        Example: `2016-08-25T21:10:29.600Z`


        :param time_created: The time_created of this TenancyAttachment.
        :type: datetime
        """
        self._time_created = time_created

    @property
    def time_updated(self):
        """
        **[Required]** Gets the time_updated of this TenancyAttachment.
        Date and time the tenancy attachment was updated. An RFC3339 formatted datetime string.

        Example: `2016-08-25T21:10:29.600Z`


        :return: The time_updated of this TenancyAttachment.
        :rtype: datetime
        """
        return self._time_updated

    @time_updated.setter
    def time_updated(self, time_updated):
        """
        Sets the time_updated of this TenancyAttachment.
        Date and time the tenancy attachment was updated. An RFC3339 formatted datetime string.

        Example: `2016-08-25T21:10:29.600Z`


        :param time_updated: The time_updated of this TenancyAttachment.
        :type: datetime
        """
        self._time_updated = time_updated

    @property
    def time_last_attempted(self):
        """
        Gets the time_last_attempted of this TenancyAttachment.
        Date and time the tenancy attachment was last attempted. An RFC3339 formatted datetime string.

        Example: `2016-08-25T21:10:29.600Z`


        :return: The time_last_attempted of this TenancyAttachment.
        :rtype: datetime
        """
        return self._time_last_attempted

    @time_last_attempted.setter
    def time_last_attempted(self, time_last_attempted):
        """
        Sets the time_last_attempted of this TenancyAttachment.
        Date and time the tenancy attachment was last attempted. An RFC3339 formatted datetime string.

        Example: `2016-08-25T21:10:29.600Z`


        :param time_last_attempted: The time_last_attempted of this TenancyAttachment.
        :type: datetime
        """
        self._time_last_attempted = time_last_attempted

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
