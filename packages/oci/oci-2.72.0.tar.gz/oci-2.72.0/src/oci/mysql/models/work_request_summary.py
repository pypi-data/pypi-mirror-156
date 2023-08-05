# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class WorkRequestSummary(object):
    """
    The status of an asynchronous task in the system.
    """

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "CREATE_DBSYSTEM"
    OPERATION_TYPE_CREATE_DBSYSTEM = "CREATE_DBSYSTEM"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "UPDATE_DBSYSTEM"
    OPERATION_TYPE_UPDATE_DBSYSTEM = "UPDATE_DBSYSTEM"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "DELETE_DBSYSTEM"
    OPERATION_TYPE_DELETE_DBSYSTEM = "DELETE_DBSYSTEM"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "START_DBSYSTEM"
    OPERATION_TYPE_START_DBSYSTEM = "START_DBSYSTEM"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "STOP_DBSYSTEM"
    OPERATION_TYPE_STOP_DBSYSTEM = "STOP_DBSYSTEM"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "RESTART_DBSYSTEM"
    OPERATION_TYPE_RESTART_DBSYSTEM = "RESTART_DBSYSTEM"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "ADD_ANALYTICS_CLUSTER"
    OPERATION_TYPE_ADD_ANALYTICS_CLUSTER = "ADD_ANALYTICS_CLUSTER"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "UPDATE_ANALYTICS_CLUSTER"
    OPERATION_TYPE_UPDATE_ANALYTICS_CLUSTER = "UPDATE_ANALYTICS_CLUSTER"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "DELETE_ANALYTICS_CLUSTER"
    OPERATION_TYPE_DELETE_ANALYTICS_CLUSTER = "DELETE_ANALYTICS_CLUSTER"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "START_ANALYTICS_CLUSTER"
    OPERATION_TYPE_START_ANALYTICS_CLUSTER = "START_ANALYTICS_CLUSTER"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "STOP_ANALYTICS_CLUSTER"
    OPERATION_TYPE_STOP_ANALYTICS_CLUSTER = "STOP_ANALYTICS_CLUSTER"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "RESTART_ANALYTICS_CLUSTER"
    OPERATION_TYPE_RESTART_ANALYTICS_CLUSTER = "RESTART_ANALYTICS_CLUSTER"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "GENERATE_ANALYTICS_CLUSTER_MEMORY_ESTIMATE"
    OPERATION_TYPE_GENERATE_ANALYTICS_CLUSTER_MEMORY_ESTIMATE = "GENERATE_ANALYTICS_CLUSTER_MEMORY_ESTIMATE"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "ADD_HEATWAVE_CLUSTER"
    OPERATION_TYPE_ADD_HEATWAVE_CLUSTER = "ADD_HEATWAVE_CLUSTER"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "UPDATE_HEATWAVE_CLUSTER"
    OPERATION_TYPE_UPDATE_HEATWAVE_CLUSTER = "UPDATE_HEATWAVE_CLUSTER"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "DELETE_HEATWAVE_CLUSTER"
    OPERATION_TYPE_DELETE_HEATWAVE_CLUSTER = "DELETE_HEATWAVE_CLUSTER"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "START_HEATWAVE_CLUSTER"
    OPERATION_TYPE_START_HEATWAVE_CLUSTER = "START_HEATWAVE_CLUSTER"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "STOP_HEATWAVE_CLUSTER"
    OPERATION_TYPE_STOP_HEATWAVE_CLUSTER = "STOP_HEATWAVE_CLUSTER"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "RESTART_HEATWAVE_CLUSTER"
    OPERATION_TYPE_RESTART_HEATWAVE_CLUSTER = "RESTART_HEATWAVE_CLUSTER"

    #: A constant which can be used with the operation_type property of a WorkRequestSummary.
    #: This constant has a value of "GENERATE_HEATWAVE_CLUSTER_MEMORY_ESTIMATE"
    OPERATION_TYPE_GENERATE_HEATWAVE_CLUSTER_MEMORY_ESTIMATE = "GENERATE_HEATWAVE_CLUSTER_MEMORY_ESTIMATE"

    #: A constant which can be used with the status property of a WorkRequestSummary.
    #: This constant has a value of "ACCEPTED"
    STATUS_ACCEPTED = "ACCEPTED"

    #: A constant which can be used with the status property of a WorkRequestSummary.
    #: This constant has a value of "IN_PROGRESS"
    STATUS_IN_PROGRESS = "IN_PROGRESS"

    #: A constant which can be used with the status property of a WorkRequestSummary.
    #: This constant has a value of "FAILED"
    STATUS_FAILED = "FAILED"

    #: A constant which can be used with the status property of a WorkRequestSummary.
    #: This constant has a value of "SUCCEEDED"
    STATUS_SUCCEEDED = "SUCCEEDED"

    #: A constant which can be used with the status property of a WorkRequestSummary.
    #: This constant has a value of "CANCELING"
    STATUS_CANCELING = "CANCELING"

    #: A constant which can be used with the status property of a WorkRequestSummary.
    #: This constant has a value of "CANCELED"
    STATUS_CANCELED = "CANCELED"

    def __init__(self, **kwargs):
        """
        Initializes a new WorkRequestSummary object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param id:
            The value to assign to the id property of this WorkRequestSummary.
        :type id: str

        :param operation_type:
            The value to assign to the operation_type property of this WorkRequestSummary.
            Allowed values for this property are: "CREATE_DBSYSTEM", "UPDATE_DBSYSTEM", "DELETE_DBSYSTEM", "START_DBSYSTEM", "STOP_DBSYSTEM", "RESTART_DBSYSTEM", "ADD_ANALYTICS_CLUSTER", "UPDATE_ANALYTICS_CLUSTER", "DELETE_ANALYTICS_CLUSTER", "START_ANALYTICS_CLUSTER", "STOP_ANALYTICS_CLUSTER", "RESTART_ANALYTICS_CLUSTER", "GENERATE_ANALYTICS_CLUSTER_MEMORY_ESTIMATE", "ADD_HEATWAVE_CLUSTER", "UPDATE_HEATWAVE_CLUSTER", "DELETE_HEATWAVE_CLUSTER", "START_HEATWAVE_CLUSTER", "STOP_HEATWAVE_CLUSTER", "RESTART_HEATWAVE_CLUSTER", "GENERATE_HEATWAVE_CLUSTER_MEMORY_ESTIMATE", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type operation_type: str

        :param status:
            The value to assign to the status property of this WorkRequestSummary.
            Allowed values for this property are: "ACCEPTED", "IN_PROGRESS", "FAILED", "SUCCEEDED", "CANCELING", "CANCELED", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type status: str

        :param compartment_id:
            The value to assign to the compartment_id property of this WorkRequestSummary.
        :type compartment_id: str

        :param percent_complete:
            The value to assign to the percent_complete property of this WorkRequestSummary.
        :type percent_complete: float

        :param time_accepted:
            The value to assign to the time_accepted property of this WorkRequestSummary.
        :type time_accepted: datetime

        :param time_started:
            The value to assign to the time_started property of this WorkRequestSummary.
        :type time_started: datetime

        :param time_finished:
            The value to assign to the time_finished property of this WorkRequestSummary.
        :type time_finished: datetime

        """
        self.swagger_types = {
            'id': 'str',
            'operation_type': 'str',
            'status': 'str',
            'compartment_id': 'str',
            'percent_complete': 'float',
            'time_accepted': 'datetime',
            'time_started': 'datetime',
            'time_finished': 'datetime'
        }

        self.attribute_map = {
            'id': 'id',
            'operation_type': 'operationType',
            'status': 'status',
            'compartment_id': 'compartmentId',
            'percent_complete': 'percentComplete',
            'time_accepted': 'timeAccepted',
            'time_started': 'timeStarted',
            'time_finished': 'timeFinished'
        }

        self._id = None
        self._operation_type = None
        self._status = None
        self._compartment_id = None
        self._percent_complete = None
        self._time_accepted = None
        self._time_started = None
        self._time_finished = None

    @property
    def id(self):
        """
        **[Required]** Gets the id of this WorkRequestSummary.
        The id of the work request.


        :return: The id of this WorkRequestSummary.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this WorkRequestSummary.
        The id of the work request.


        :param id: The id of this WorkRequestSummary.
        :type: str
        """
        self._id = id

    @property
    def operation_type(self):
        """
        **[Required]** Gets the operation_type of this WorkRequestSummary.
        the original operation ID requested

        Allowed values for this property are: "CREATE_DBSYSTEM", "UPDATE_DBSYSTEM", "DELETE_DBSYSTEM", "START_DBSYSTEM", "STOP_DBSYSTEM", "RESTART_DBSYSTEM", "ADD_ANALYTICS_CLUSTER", "UPDATE_ANALYTICS_CLUSTER", "DELETE_ANALYTICS_CLUSTER", "START_ANALYTICS_CLUSTER", "STOP_ANALYTICS_CLUSTER", "RESTART_ANALYTICS_CLUSTER", "GENERATE_ANALYTICS_CLUSTER_MEMORY_ESTIMATE", "ADD_HEATWAVE_CLUSTER", "UPDATE_HEATWAVE_CLUSTER", "DELETE_HEATWAVE_CLUSTER", "START_HEATWAVE_CLUSTER", "STOP_HEATWAVE_CLUSTER", "RESTART_HEATWAVE_CLUSTER", "GENERATE_HEATWAVE_CLUSTER_MEMORY_ESTIMATE", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The operation_type of this WorkRequestSummary.
        :rtype: str
        """
        return self._operation_type

    @operation_type.setter
    def operation_type(self, operation_type):
        """
        Sets the operation_type of this WorkRequestSummary.
        the original operation ID requested


        :param operation_type: The operation_type of this WorkRequestSummary.
        :type: str
        """
        allowed_values = ["CREATE_DBSYSTEM", "UPDATE_DBSYSTEM", "DELETE_DBSYSTEM", "START_DBSYSTEM", "STOP_DBSYSTEM", "RESTART_DBSYSTEM", "ADD_ANALYTICS_CLUSTER", "UPDATE_ANALYTICS_CLUSTER", "DELETE_ANALYTICS_CLUSTER", "START_ANALYTICS_CLUSTER", "STOP_ANALYTICS_CLUSTER", "RESTART_ANALYTICS_CLUSTER", "GENERATE_ANALYTICS_CLUSTER_MEMORY_ESTIMATE", "ADD_HEATWAVE_CLUSTER", "UPDATE_HEATWAVE_CLUSTER", "DELETE_HEATWAVE_CLUSTER", "START_HEATWAVE_CLUSTER", "STOP_HEATWAVE_CLUSTER", "RESTART_HEATWAVE_CLUSTER", "GENERATE_HEATWAVE_CLUSTER_MEMORY_ESTIMATE"]
        if not value_allowed_none_or_none_sentinel(operation_type, allowed_values):
            operation_type = 'UNKNOWN_ENUM_VALUE'
        self._operation_type = operation_type

    @property
    def status(self):
        """
        **[Required]** Gets the status of this WorkRequestSummary.
        Current status of the work request

        Allowed values for this property are: "ACCEPTED", "IN_PROGRESS", "FAILED", "SUCCEEDED", "CANCELING", "CANCELED", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The status of this WorkRequestSummary.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """
        Sets the status of this WorkRequestSummary.
        Current status of the work request


        :param status: The status of this WorkRequestSummary.
        :type: str
        """
        allowed_values = ["ACCEPTED", "IN_PROGRESS", "FAILED", "SUCCEEDED", "CANCELING", "CANCELED"]
        if not value_allowed_none_or_none_sentinel(status, allowed_values):
            status = 'UNKNOWN_ENUM_VALUE'
        self._status = status

    @property
    def compartment_id(self):
        """
        **[Required]** Gets the compartment_id of this WorkRequestSummary.
        The ocid of the compartment that contains the work request. Work
        requests should be scoped to the same compartment as the resource
        the work request affects. If the work request affects multiple
        resources, and those resources are not in the same compartment, it
        is up to the service team to pick the primary resource whose
        compartment should be used


        :return: The compartment_id of this WorkRequestSummary.
        :rtype: str
        """
        return self._compartment_id

    @compartment_id.setter
    def compartment_id(self, compartment_id):
        """
        Sets the compartment_id of this WorkRequestSummary.
        The ocid of the compartment that contains the work request. Work
        requests should be scoped to the same compartment as the resource
        the work request affects. If the work request affects multiple
        resources, and those resources are not in the same compartment, it
        is up to the service team to pick the primary resource whose
        compartment should be used


        :param compartment_id: The compartment_id of this WorkRequestSummary.
        :type: str
        """
        self._compartment_id = compartment_id

    @property
    def percent_complete(self):
        """
        **[Required]** Gets the percent_complete of this WorkRequestSummary.
        Percentage of the request completed.


        :return: The percent_complete of this WorkRequestSummary.
        :rtype: float
        """
        return self._percent_complete

    @percent_complete.setter
    def percent_complete(self, percent_complete):
        """
        Sets the percent_complete of this WorkRequestSummary.
        Percentage of the request completed.


        :param percent_complete: The percent_complete of this WorkRequestSummary.
        :type: float
        """
        self._percent_complete = percent_complete

    @property
    def time_accepted(self):
        """
        **[Required]** Gets the time_accepted of this WorkRequestSummary.
        The date and time the request was created, as described in
        `RFC 3339`__, section 14.29.

        __ https://tools.ietf.org/rfc/rfc3339


        :return: The time_accepted of this WorkRequestSummary.
        :rtype: datetime
        """
        return self._time_accepted

    @time_accepted.setter
    def time_accepted(self, time_accepted):
        """
        Sets the time_accepted of this WorkRequestSummary.
        The date and time the request was created, as described in
        `RFC 3339`__, section 14.29.

        __ https://tools.ietf.org/rfc/rfc3339


        :param time_accepted: The time_accepted of this WorkRequestSummary.
        :type: datetime
        """
        self._time_accepted = time_accepted

    @property
    def time_started(self):
        """
        Gets the time_started of this WorkRequestSummary.
        The date and time the request was started, as described in `RFC 3339`__,
        section 14.29.

        __ https://tools.ietf.org/rfc/rfc3339


        :return: The time_started of this WorkRequestSummary.
        :rtype: datetime
        """
        return self._time_started

    @time_started.setter
    def time_started(self, time_started):
        """
        Sets the time_started of this WorkRequestSummary.
        The date and time the request was started, as described in `RFC 3339`__,
        section 14.29.

        __ https://tools.ietf.org/rfc/rfc3339


        :param time_started: The time_started of this WorkRequestSummary.
        :type: datetime
        """
        self._time_started = time_started

    @property
    def time_finished(self):
        """
        Gets the time_finished of this WorkRequestSummary.
        The date and time the object was finished, as described in `RFC 3339`__.

        __ https://tools.ietf.org/rfc/rfc3339


        :return: The time_finished of this WorkRequestSummary.
        :rtype: datetime
        """
        return self._time_finished

    @time_finished.setter
    def time_finished(self, time_finished):
        """
        Sets the time_finished of this WorkRequestSummary.
        The date and time the object was finished, as described in `RFC 3339`__.

        __ https://tools.ietf.org/rfc/rfc3339


        :param time_finished: The time_finished of this WorkRequestSummary.
        :type: datetime
        """
        self._time_finished = time_finished

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
