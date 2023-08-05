# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class OperatorControlAssignmentSummary(object):
    """
    Details of the operator control assignment.
    """

    #: A constant which can be used with the resource_type property of a OperatorControlAssignmentSummary.
    #: This constant has a value of "EXACC"
    RESOURCE_TYPE_EXACC = "EXACC"

    #: A constant which can be used with the resource_type property of a OperatorControlAssignmentSummary.
    #: This constant has a value of "EXADATAINFRASTRUCTURE"
    RESOURCE_TYPE_EXADATAINFRASTRUCTURE = "EXADATAINFRASTRUCTURE"

    #: A constant which can be used with the resource_type property of a OperatorControlAssignmentSummary.
    #: This constant has a value of "AUTONOMOUSVMCLUSTER"
    RESOURCE_TYPE_AUTONOMOUSVMCLUSTER = "AUTONOMOUSVMCLUSTER"

    #: A constant which can be used with the lifecycle_state property of a OperatorControlAssignmentSummary.
    #: This constant has a value of "CREATED"
    LIFECYCLE_STATE_CREATED = "CREATED"

    #: A constant which can be used with the lifecycle_state property of a OperatorControlAssignmentSummary.
    #: This constant has a value of "APPLIED"
    LIFECYCLE_STATE_APPLIED = "APPLIED"

    #: A constant which can be used with the lifecycle_state property of a OperatorControlAssignmentSummary.
    #: This constant has a value of "APPLYFAILED"
    LIFECYCLE_STATE_APPLYFAILED = "APPLYFAILED"

    #: A constant which can be used with the lifecycle_state property of a OperatorControlAssignmentSummary.
    #: This constant has a value of "UPDATING"
    LIFECYCLE_STATE_UPDATING = "UPDATING"

    #: A constant which can be used with the lifecycle_state property of a OperatorControlAssignmentSummary.
    #: This constant has a value of "DELETING"
    LIFECYCLE_STATE_DELETING = "DELETING"

    #: A constant which can be used with the lifecycle_state property of a OperatorControlAssignmentSummary.
    #: This constant has a value of "DELETED"
    LIFECYCLE_STATE_DELETED = "DELETED"

    #: A constant which can be used with the lifecycle_state property of a OperatorControlAssignmentSummary.
    #: This constant has a value of "DELETIONFAILED"
    LIFECYCLE_STATE_DELETIONFAILED = "DELETIONFAILED"

    def __init__(self, **kwargs):
        """
        Initializes a new OperatorControlAssignmentSummary object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param id:
            The value to assign to the id property of this OperatorControlAssignmentSummary.
        :type id: str

        :param operator_control_id:
            The value to assign to the operator_control_id property of this OperatorControlAssignmentSummary.
        :type operator_control_id: str

        :param resource_id:
            The value to assign to the resource_id property of this OperatorControlAssignmentSummary.
        :type resource_id: str

        :param compartment_id:
            The value to assign to the compartment_id property of this OperatorControlAssignmentSummary.
        :type compartment_id: str

        :param resource_type:
            The value to assign to the resource_type property of this OperatorControlAssignmentSummary.
            Allowed values for this property are: "EXACC", "EXADATAINFRASTRUCTURE", "AUTONOMOUSVMCLUSTER", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type resource_type: str

        :param time_assignment_from:
            The value to assign to the time_assignment_from property of this OperatorControlAssignmentSummary.
        :type time_assignment_from: datetime

        :param time_assignment_to:
            The value to assign to the time_assignment_to property of this OperatorControlAssignmentSummary.
        :type time_assignment_to: datetime

        :param is_enforced_always:
            The value to assign to the is_enforced_always property of this OperatorControlAssignmentSummary.
        :type is_enforced_always: bool

        :param time_of_assignment:
            The value to assign to the time_of_assignment property of this OperatorControlAssignmentSummary.
        :type time_of_assignment: datetime

        :param error_code:
            The value to assign to the error_code property of this OperatorControlAssignmentSummary.
        :type error_code: int

        :param error_message:
            The value to assign to the error_message property of this OperatorControlAssignmentSummary.
        :type error_message: str

        :param is_log_forwarded:
            The value to assign to the is_log_forwarded property of this OperatorControlAssignmentSummary.
        :type is_log_forwarded: bool

        :param remote_syslog_server_address:
            The value to assign to the remote_syslog_server_address property of this OperatorControlAssignmentSummary.
        :type remote_syslog_server_address: str

        :param remote_syslog_server_port:
            The value to assign to the remote_syslog_server_port property of this OperatorControlAssignmentSummary.
        :type remote_syslog_server_port: int

        :param lifecycle_state:
            The value to assign to the lifecycle_state property of this OperatorControlAssignmentSummary.
            Allowed values for this property are: "CREATED", "APPLIED", "APPLYFAILED", "UPDATING", "DELETING", "DELETED", "DELETIONFAILED", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type lifecycle_state: str

        :param freeform_tags:
            The value to assign to the freeform_tags property of this OperatorControlAssignmentSummary.
        :type freeform_tags: dict(str, str)

        :param defined_tags:
            The value to assign to the defined_tags property of this OperatorControlAssignmentSummary.
        :type defined_tags: dict(str, dict(str, object))

        """
        self.swagger_types = {
            'id': 'str',
            'operator_control_id': 'str',
            'resource_id': 'str',
            'compartment_id': 'str',
            'resource_type': 'str',
            'time_assignment_from': 'datetime',
            'time_assignment_to': 'datetime',
            'is_enforced_always': 'bool',
            'time_of_assignment': 'datetime',
            'error_code': 'int',
            'error_message': 'str',
            'is_log_forwarded': 'bool',
            'remote_syslog_server_address': 'str',
            'remote_syslog_server_port': 'int',
            'lifecycle_state': 'str',
            'freeform_tags': 'dict(str, str)',
            'defined_tags': 'dict(str, dict(str, object))'
        }

        self.attribute_map = {
            'id': 'id',
            'operator_control_id': 'operatorControlId',
            'resource_id': 'resourceId',
            'compartment_id': 'compartmentId',
            'resource_type': 'resourceType',
            'time_assignment_from': 'timeAssignmentFrom',
            'time_assignment_to': 'timeAssignmentTo',
            'is_enforced_always': 'isEnforcedAlways',
            'time_of_assignment': 'timeOfAssignment',
            'error_code': 'errorCode',
            'error_message': 'errorMessage',
            'is_log_forwarded': 'isLogForwarded',
            'remote_syslog_server_address': 'remoteSyslogServerAddress',
            'remote_syslog_server_port': 'remoteSyslogServerPort',
            'lifecycle_state': 'lifecycleState',
            'freeform_tags': 'freeformTags',
            'defined_tags': 'definedTags'
        }

        self._id = None
        self._operator_control_id = None
        self._resource_id = None
        self._compartment_id = None
        self._resource_type = None
        self._time_assignment_from = None
        self._time_assignment_to = None
        self._is_enforced_always = None
        self._time_of_assignment = None
        self._error_code = None
        self._error_message = None
        self._is_log_forwarded = None
        self._remote_syslog_server_address = None
        self._remote_syslog_server_port = None
        self._lifecycle_state = None
        self._freeform_tags = None
        self._defined_tags = None

    @property
    def id(self):
        """
        **[Required]** Gets the id of this OperatorControlAssignmentSummary.
        The OCID of the operator control assignment.


        :return: The id of this OperatorControlAssignmentSummary.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this OperatorControlAssignmentSummary.
        The OCID of the operator control assignment.


        :param id: The id of this OperatorControlAssignmentSummary.
        :type: str
        """
        self._id = id

    @property
    def operator_control_id(self):
        """
        **[Required]** Gets the operator_control_id of this OperatorControlAssignmentSummary.
        The OCID of the operator control.


        :return: The operator_control_id of this OperatorControlAssignmentSummary.
        :rtype: str
        """
        return self._operator_control_id

    @operator_control_id.setter
    def operator_control_id(self, operator_control_id):
        """
        Sets the operator_control_id of this OperatorControlAssignmentSummary.
        The OCID of the operator control.


        :param operator_control_id: The operator_control_id of this OperatorControlAssignmentSummary.
        :type: str
        """
        self._operator_control_id = operator_control_id

    @property
    def resource_id(self):
        """
        **[Required]** Gets the resource_id of this OperatorControlAssignmentSummary.
        The OCID of the target resource being governed by the operator control.


        :return: The resource_id of this OperatorControlAssignmentSummary.
        :rtype: str
        """
        return self._resource_id

    @resource_id.setter
    def resource_id(self, resource_id):
        """
        Sets the resource_id of this OperatorControlAssignmentSummary.
        The OCID of the target resource being governed by the operator control.


        :param resource_id: The resource_id of this OperatorControlAssignmentSummary.
        :type: str
        """
        self._resource_id = resource_id

    @property
    def compartment_id(self):
        """
        **[Required]** Gets the compartment_id of this OperatorControlAssignmentSummary.
        The OCID of the compartment that contains the operator control assignment.


        :return: The compartment_id of this OperatorControlAssignmentSummary.
        :rtype: str
        """
        return self._compartment_id

    @compartment_id.setter
    def compartment_id(self, compartment_id):
        """
        Sets the compartment_id of this OperatorControlAssignmentSummary.
        The OCID of the compartment that contains the operator control assignment.


        :param compartment_id: The compartment_id of this OperatorControlAssignmentSummary.
        :type: str
        """
        self._compartment_id = compartment_id

    @property
    def resource_type(self):
        """
        Gets the resource_type of this OperatorControlAssignmentSummary.
        resourceType for which the OperatorControlAssignment is applicable

        Allowed values for this property are: "EXACC", "EXADATAINFRASTRUCTURE", "AUTONOMOUSVMCLUSTER", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The resource_type of this OperatorControlAssignmentSummary.
        :rtype: str
        """
        return self._resource_type

    @resource_type.setter
    def resource_type(self, resource_type):
        """
        Sets the resource_type of this OperatorControlAssignmentSummary.
        resourceType for which the OperatorControlAssignment is applicable


        :param resource_type: The resource_type of this OperatorControlAssignmentSummary.
        :type: str
        """
        allowed_values = ["EXACC", "EXADATAINFRASTRUCTURE", "AUTONOMOUSVMCLUSTER"]
        if not value_allowed_none_or_none_sentinel(resource_type, allowed_values):
            resource_type = 'UNKNOWN_ENUM_VALUE'
        self._resource_type = resource_type

    @property
    def time_assignment_from(self):
        """
        Gets the time_assignment_from of this OperatorControlAssignmentSummary.
        The time at which the target resource will be brought under the governance of the operator control in `RFC 3339`__ timestamp format. Example: '2020-05-22T21:10:29.600Z'

        __ https://tools.ietf.org/html/rfc3339


        :return: The time_assignment_from of this OperatorControlAssignmentSummary.
        :rtype: datetime
        """
        return self._time_assignment_from

    @time_assignment_from.setter
    def time_assignment_from(self, time_assignment_from):
        """
        Sets the time_assignment_from of this OperatorControlAssignmentSummary.
        The time at which the target resource will be brought under the governance of the operator control in `RFC 3339`__ timestamp format. Example: '2020-05-22T21:10:29.600Z'

        __ https://tools.ietf.org/html/rfc3339


        :param time_assignment_from: The time_assignment_from of this OperatorControlAssignmentSummary.
        :type: datetime
        """
        self._time_assignment_from = time_assignment_from

    @property
    def time_assignment_to(self):
        """
        Gets the time_assignment_to of this OperatorControlAssignmentSummary.
        The time at which the target resource will leave the governance of the operator control in `RFC 3339`__timestamp format.Example: '2020-05-22T21:10:29.600Z'

        __ https://tools.ietf.org/html/rfc3339


        :return: The time_assignment_to of this OperatorControlAssignmentSummary.
        :rtype: datetime
        """
        return self._time_assignment_to

    @time_assignment_to.setter
    def time_assignment_to(self, time_assignment_to):
        """
        Sets the time_assignment_to of this OperatorControlAssignmentSummary.
        The time at which the target resource will leave the governance of the operator control in `RFC 3339`__timestamp format.Example: '2020-05-22T21:10:29.600Z'

        __ https://tools.ietf.org/html/rfc3339


        :param time_assignment_to: The time_assignment_to of this OperatorControlAssignmentSummary.
        :type: datetime
        """
        self._time_assignment_to = time_assignment_to

    @property
    def is_enforced_always(self):
        """
        Gets the is_enforced_always of this OperatorControlAssignmentSummary.
        If true, then the target resource is always governed by the operator control. Otherwise governance is time-based as specified by timeAssignmentTo and timeAssignmentFrom.


        :return: The is_enforced_always of this OperatorControlAssignmentSummary.
        :rtype: bool
        """
        return self._is_enforced_always

    @is_enforced_always.setter
    def is_enforced_always(self, is_enforced_always):
        """
        Sets the is_enforced_always of this OperatorControlAssignmentSummary.
        If true, then the target resource is always governed by the operator control. Otherwise governance is time-based as specified by timeAssignmentTo and timeAssignmentFrom.


        :param is_enforced_always: The is_enforced_always of this OperatorControlAssignmentSummary.
        :type: bool
        """
        self._is_enforced_always = is_enforced_always

    @property
    def time_of_assignment(self):
        """
        Gets the time_of_assignment of this OperatorControlAssignmentSummary.
        Time when the operator control assignment is created in `RFC 3339`__ timestamp format. Example: '2020-05-22T21:10:29.600Z'

        __ https://tools.ietf.org/html/rfc3339


        :return: The time_of_assignment of this OperatorControlAssignmentSummary.
        :rtype: datetime
        """
        return self._time_of_assignment

    @time_of_assignment.setter
    def time_of_assignment(self, time_of_assignment):
        """
        Sets the time_of_assignment of this OperatorControlAssignmentSummary.
        Time when the operator control assignment is created in `RFC 3339`__ timestamp format. Example: '2020-05-22T21:10:29.600Z'

        __ https://tools.ietf.org/html/rfc3339


        :param time_of_assignment: The time_of_assignment of this OperatorControlAssignmentSummary.
        :type: datetime
        """
        self._time_of_assignment = time_of_assignment

    @property
    def error_code(self):
        """
        Gets the error_code of this OperatorControlAssignmentSummary.
        The code identifying the error occurred during Assignment operation.


        :return: The error_code of this OperatorControlAssignmentSummary.
        :rtype: int
        """
        return self._error_code

    @error_code.setter
    def error_code(self, error_code):
        """
        Sets the error_code of this OperatorControlAssignmentSummary.
        The code identifying the error occurred during Assignment operation.


        :param error_code: The error_code of this OperatorControlAssignmentSummary.
        :type: int
        """
        self._error_code = error_code

    @property
    def error_message(self):
        """
        Gets the error_message of this OperatorControlAssignmentSummary.
        The message describing the error occurred during Assignment operation.


        :return: The error_message of this OperatorControlAssignmentSummary.
        :rtype: str
        """
        return self._error_message

    @error_message.setter
    def error_message(self, error_message):
        """
        Sets the error_message of this OperatorControlAssignmentSummary.
        The message describing the error occurred during Assignment operation.


        :param error_message: The error_message of this OperatorControlAssignmentSummary.
        :type: str
        """
        self._error_message = error_message

    @property
    def is_log_forwarded(self):
        """
        Gets the is_log_forwarded of this OperatorControlAssignmentSummary.
        If set, then the audit logs are being forwarded to the relevant remote logging server


        :return: The is_log_forwarded of this OperatorControlAssignmentSummary.
        :rtype: bool
        """
        return self._is_log_forwarded

    @is_log_forwarded.setter
    def is_log_forwarded(self, is_log_forwarded):
        """
        Sets the is_log_forwarded of this OperatorControlAssignmentSummary.
        If set, then the audit logs are being forwarded to the relevant remote logging server


        :param is_log_forwarded: The is_log_forwarded of this OperatorControlAssignmentSummary.
        :type: bool
        """
        self._is_log_forwarded = is_log_forwarded

    @property
    def remote_syslog_server_address(self):
        """
        Gets the remote_syslog_server_address of this OperatorControlAssignmentSummary.
        The address of the remote syslog server where the audit logs are being forwarded to. Address in host or IP format.


        :return: The remote_syslog_server_address of this OperatorControlAssignmentSummary.
        :rtype: str
        """
        return self._remote_syslog_server_address

    @remote_syslog_server_address.setter
    def remote_syslog_server_address(self, remote_syslog_server_address):
        """
        Sets the remote_syslog_server_address of this OperatorControlAssignmentSummary.
        The address of the remote syslog server where the audit logs are being forwarded to. Address in host or IP format.


        :param remote_syslog_server_address: The remote_syslog_server_address of this OperatorControlAssignmentSummary.
        :type: str
        """
        self._remote_syslog_server_address = remote_syslog_server_address

    @property
    def remote_syslog_server_port(self):
        """
        Gets the remote_syslog_server_port of this OperatorControlAssignmentSummary.
        The listening port of the remote syslog server. The port range is 0 - 65535.


        :return: The remote_syslog_server_port of this OperatorControlAssignmentSummary.
        :rtype: int
        """
        return self._remote_syslog_server_port

    @remote_syslog_server_port.setter
    def remote_syslog_server_port(self, remote_syslog_server_port):
        """
        Sets the remote_syslog_server_port of this OperatorControlAssignmentSummary.
        The listening port of the remote syslog server. The port range is 0 - 65535.


        :param remote_syslog_server_port: The remote_syslog_server_port of this OperatorControlAssignmentSummary.
        :type: int
        """
        self._remote_syslog_server_port = remote_syslog_server_port

    @property
    def lifecycle_state(self):
        """
        Gets the lifecycle_state of this OperatorControlAssignmentSummary.
        The current lifcycle state of the OperatorControl.

        Allowed values for this property are: "CREATED", "APPLIED", "APPLYFAILED", "UPDATING", "DELETING", "DELETED", "DELETIONFAILED", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The lifecycle_state of this OperatorControlAssignmentSummary.
        :rtype: str
        """
        return self._lifecycle_state

    @lifecycle_state.setter
    def lifecycle_state(self, lifecycle_state):
        """
        Sets the lifecycle_state of this OperatorControlAssignmentSummary.
        The current lifcycle state of the OperatorControl.


        :param lifecycle_state: The lifecycle_state of this OperatorControlAssignmentSummary.
        :type: str
        """
        allowed_values = ["CREATED", "APPLIED", "APPLYFAILED", "UPDATING", "DELETING", "DELETED", "DELETIONFAILED"]
        if not value_allowed_none_or_none_sentinel(lifecycle_state, allowed_values):
            lifecycle_state = 'UNKNOWN_ENUM_VALUE'
        self._lifecycle_state = lifecycle_state

    @property
    def freeform_tags(self):
        """
        Gets the freeform_tags of this OperatorControlAssignmentSummary.
        Simple key-value pair that is applied without any predefined name, type or scope. Exists for cross-compatibility only.


        :return: The freeform_tags of this OperatorControlAssignmentSummary.
        :rtype: dict(str, str)
        """
        return self._freeform_tags

    @freeform_tags.setter
    def freeform_tags(self, freeform_tags):
        """
        Sets the freeform_tags of this OperatorControlAssignmentSummary.
        Simple key-value pair that is applied without any predefined name, type or scope. Exists for cross-compatibility only.


        :param freeform_tags: The freeform_tags of this OperatorControlAssignmentSummary.
        :type: dict(str, str)
        """
        self._freeform_tags = freeform_tags

    @property
    def defined_tags(self):
        """
        Gets the defined_tags of this OperatorControlAssignmentSummary.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.


        :return: The defined_tags of this OperatorControlAssignmentSummary.
        :rtype: dict(str, dict(str, object))
        """
        return self._defined_tags

    @defined_tags.setter
    def defined_tags(self, defined_tags):
        """
        Sets the defined_tags of this OperatorControlAssignmentSummary.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.


        :param defined_tags: The defined_tags of this OperatorControlAssignmentSummary.
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
