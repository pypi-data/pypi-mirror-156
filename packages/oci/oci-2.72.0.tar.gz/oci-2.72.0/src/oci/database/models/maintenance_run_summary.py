# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class MaintenanceRunSummary(object):
    """
    Details of a maintenance run.
    """

    #: A constant which can be used with the lifecycle_state property of a MaintenanceRunSummary.
    #: This constant has a value of "SCHEDULED"
    LIFECYCLE_STATE_SCHEDULED = "SCHEDULED"

    #: A constant which can be used with the lifecycle_state property of a MaintenanceRunSummary.
    #: This constant has a value of "IN_PROGRESS"
    LIFECYCLE_STATE_IN_PROGRESS = "IN_PROGRESS"

    #: A constant which can be used with the lifecycle_state property of a MaintenanceRunSummary.
    #: This constant has a value of "SUCCEEDED"
    LIFECYCLE_STATE_SUCCEEDED = "SUCCEEDED"

    #: A constant which can be used with the lifecycle_state property of a MaintenanceRunSummary.
    #: This constant has a value of "SKIPPED"
    LIFECYCLE_STATE_SKIPPED = "SKIPPED"

    #: A constant which can be used with the lifecycle_state property of a MaintenanceRunSummary.
    #: This constant has a value of "FAILED"
    LIFECYCLE_STATE_FAILED = "FAILED"

    #: A constant which can be used with the lifecycle_state property of a MaintenanceRunSummary.
    #: This constant has a value of "UPDATING"
    LIFECYCLE_STATE_UPDATING = "UPDATING"

    #: A constant which can be used with the lifecycle_state property of a MaintenanceRunSummary.
    #: This constant has a value of "DELETING"
    LIFECYCLE_STATE_DELETING = "DELETING"

    #: A constant which can be used with the lifecycle_state property of a MaintenanceRunSummary.
    #: This constant has a value of "DELETED"
    LIFECYCLE_STATE_DELETED = "DELETED"

    #: A constant which can be used with the lifecycle_state property of a MaintenanceRunSummary.
    #: This constant has a value of "CANCELED"
    LIFECYCLE_STATE_CANCELED = "CANCELED"

    #: A constant which can be used with the target_resource_type property of a MaintenanceRunSummary.
    #: This constant has a value of "AUTONOMOUS_EXADATA_INFRASTRUCTURE"
    TARGET_RESOURCE_TYPE_AUTONOMOUS_EXADATA_INFRASTRUCTURE = "AUTONOMOUS_EXADATA_INFRASTRUCTURE"

    #: A constant which can be used with the target_resource_type property of a MaintenanceRunSummary.
    #: This constant has a value of "AUTONOMOUS_CONTAINER_DATABASE"
    TARGET_RESOURCE_TYPE_AUTONOMOUS_CONTAINER_DATABASE = "AUTONOMOUS_CONTAINER_DATABASE"

    #: A constant which can be used with the target_resource_type property of a MaintenanceRunSummary.
    #: This constant has a value of "EXADATA_DB_SYSTEM"
    TARGET_RESOURCE_TYPE_EXADATA_DB_SYSTEM = "EXADATA_DB_SYSTEM"

    #: A constant which can be used with the target_resource_type property of a MaintenanceRunSummary.
    #: This constant has a value of "CLOUD_EXADATA_INFRASTRUCTURE"
    TARGET_RESOURCE_TYPE_CLOUD_EXADATA_INFRASTRUCTURE = "CLOUD_EXADATA_INFRASTRUCTURE"

    #: A constant which can be used with the target_resource_type property of a MaintenanceRunSummary.
    #: This constant has a value of "EXACC_INFRASTRUCTURE"
    TARGET_RESOURCE_TYPE_EXACC_INFRASTRUCTURE = "EXACC_INFRASTRUCTURE"

    #: A constant which can be used with the target_resource_type property of a MaintenanceRunSummary.
    #: This constant has a value of "AUTONOMOUS_VM_CLUSTER"
    TARGET_RESOURCE_TYPE_AUTONOMOUS_VM_CLUSTER = "AUTONOMOUS_VM_CLUSTER"

    #: A constant which can be used with the target_resource_type property of a MaintenanceRunSummary.
    #: This constant has a value of "AUTONOMOUS_DATABASE"
    TARGET_RESOURCE_TYPE_AUTONOMOUS_DATABASE = "AUTONOMOUS_DATABASE"

    #: A constant which can be used with the maintenance_type property of a MaintenanceRunSummary.
    #: This constant has a value of "PLANNED"
    MAINTENANCE_TYPE_PLANNED = "PLANNED"

    #: A constant which can be used with the maintenance_type property of a MaintenanceRunSummary.
    #: This constant has a value of "UNPLANNED"
    MAINTENANCE_TYPE_UNPLANNED = "UNPLANNED"

    #: A constant which can be used with the maintenance_subtype property of a MaintenanceRunSummary.
    #: This constant has a value of "QUARTERLY"
    MAINTENANCE_SUBTYPE_QUARTERLY = "QUARTERLY"

    #: A constant which can be used with the maintenance_subtype property of a MaintenanceRunSummary.
    #: This constant has a value of "HARDWARE"
    MAINTENANCE_SUBTYPE_HARDWARE = "HARDWARE"

    #: A constant which can be used with the maintenance_subtype property of a MaintenanceRunSummary.
    #: This constant has a value of "CRITICAL"
    MAINTENANCE_SUBTYPE_CRITICAL = "CRITICAL"

    #: A constant which can be used with the maintenance_subtype property of a MaintenanceRunSummary.
    #: This constant has a value of "INFRASTRUCTURE"
    MAINTENANCE_SUBTYPE_INFRASTRUCTURE = "INFRASTRUCTURE"

    #: A constant which can be used with the maintenance_subtype property of a MaintenanceRunSummary.
    #: This constant has a value of "DATABASE"
    MAINTENANCE_SUBTYPE_DATABASE = "DATABASE"

    #: A constant which can be used with the maintenance_subtype property of a MaintenanceRunSummary.
    #: This constant has a value of "ONEOFF"
    MAINTENANCE_SUBTYPE_ONEOFF = "ONEOFF"

    #: A constant which can be used with the patching_mode property of a MaintenanceRunSummary.
    #: This constant has a value of "ROLLING"
    PATCHING_MODE_ROLLING = "ROLLING"

    #: A constant which can be used with the patching_mode property of a MaintenanceRunSummary.
    #: This constant has a value of "NONROLLING"
    PATCHING_MODE_NONROLLING = "NONROLLING"

    #: A constant which can be used with the patching_status property of a MaintenanceRunSummary.
    #: This constant has a value of "PATCHING"
    PATCHING_STATUS_PATCHING = "PATCHING"

    #: A constant which can be used with the patching_status property of a MaintenanceRunSummary.
    #: This constant has a value of "WAITING"
    PATCHING_STATUS_WAITING = "WAITING"

    #: A constant which can be used with the patching_status property of a MaintenanceRunSummary.
    #: This constant has a value of "SCHEDULED"
    PATCHING_STATUS_SCHEDULED = "SCHEDULED"

    def __init__(self, **kwargs):
        """
        Initializes a new MaintenanceRunSummary object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param id:
            The value to assign to the id property of this MaintenanceRunSummary.
        :type id: str

        :param compartment_id:
            The value to assign to the compartment_id property of this MaintenanceRunSummary.
        :type compartment_id: str

        :param display_name:
            The value to assign to the display_name property of this MaintenanceRunSummary.
        :type display_name: str

        :param description:
            The value to assign to the description property of this MaintenanceRunSummary.
        :type description: str

        :param lifecycle_state:
            The value to assign to the lifecycle_state property of this MaintenanceRunSummary.
            Allowed values for this property are: "SCHEDULED", "IN_PROGRESS", "SUCCEEDED", "SKIPPED", "FAILED", "UPDATING", "DELETING", "DELETED", "CANCELED", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type lifecycle_state: str

        :param lifecycle_details:
            The value to assign to the lifecycle_details property of this MaintenanceRunSummary.
        :type lifecycle_details: str

        :param time_scheduled:
            The value to assign to the time_scheduled property of this MaintenanceRunSummary.
        :type time_scheduled: datetime

        :param time_started:
            The value to assign to the time_started property of this MaintenanceRunSummary.
        :type time_started: datetime

        :param time_ended:
            The value to assign to the time_ended property of this MaintenanceRunSummary.
        :type time_ended: datetime

        :param target_resource_type:
            The value to assign to the target_resource_type property of this MaintenanceRunSummary.
            Allowed values for this property are: "AUTONOMOUS_EXADATA_INFRASTRUCTURE", "AUTONOMOUS_CONTAINER_DATABASE", "EXADATA_DB_SYSTEM", "CLOUD_EXADATA_INFRASTRUCTURE", "EXACC_INFRASTRUCTURE", "AUTONOMOUS_VM_CLUSTER", "AUTONOMOUS_DATABASE", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type target_resource_type: str

        :param target_resource_id:
            The value to assign to the target_resource_id property of this MaintenanceRunSummary.
        :type target_resource_id: str

        :param maintenance_type:
            The value to assign to the maintenance_type property of this MaintenanceRunSummary.
            Allowed values for this property are: "PLANNED", "UNPLANNED", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type maintenance_type: str

        :param patch_id:
            The value to assign to the patch_id property of this MaintenanceRunSummary.
        :type patch_id: str

        :param maintenance_subtype:
            The value to assign to the maintenance_subtype property of this MaintenanceRunSummary.
            Allowed values for this property are: "QUARTERLY", "HARDWARE", "CRITICAL", "INFRASTRUCTURE", "DATABASE", "ONEOFF", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type maintenance_subtype: str

        :param peer_maintenance_run_id:
            The value to assign to the peer_maintenance_run_id property of this MaintenanceRunSummary.
        :type peer_maintenance_run_id: str

        :param patching_mode:
            The value to assign to the patching_mode property of this MaintenanceRunSummary.
            Allowed values for this property are: "ROLLING", "NONROLLING", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type patching_mode: str

        :param patch_failure_count:
            The value to assign to the patch_failure_count property of this MaintenanceRunSummary.
        :type patch_failure_count: int

        :param target_db_server_version:
            The value to assign to the target_db_server_version property of this MaintenanceRunSummary.
        :type target_db_server_version: str

        :param target_storage_server_version:
            The value to assign to the target_storage_server_version property of this MaintenanceRunSummary.
        :type target_storage_server_version: str

        :param is_custom_action_timeout_enabled:
            The value to assign to the is_custom_action_timeout_enabled property of this MaintenanceRunSummary.
        :type is_custom_action_timeout_enabled: bool

        :param custom_action_timeout_in_mins:
            The value to assign to the custom_action_timeout_in_mins property of this MaintenanceRunSummary.
        :type custom_action_timeout_in_mins: int

        :param current_custom_action_timeout_in_mins:
            The value to assign to the current_custom_action_timeout_in_mins property of this MaintenanceRunSummary.
        :type current_custom_action_timeout_in_mins: int

        :param patching_status:
            The value to assign to the patching_status property of this MaintenanceRunSummary.
            Allowed values for this property are: "PATCHING", "WAITING", "SCHEDULED", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type patching_status: str

        :param patching_start_time:
            The value to assign to the patching_start_time property of this MaintenanceRunSummary.
        :type patching_start_time: datetime

        :param patching_end_time:
            The value to assign to the patching_end_time property of this MaintenanceRunSummary.
        :type patching_end_time: datetime

        :param estimated_patching_time:
            The value to assign to the estimated_patching_time property of this MaintenanceRunSummary.
        :type estimated_patching_time: oci.database.models.EstimatedPatchingTime

        :param current_patching_component:
            The value to assign to the current_patching_component property of this MaintenanceRunSummary.
        :type current_patching_component: str

        :param estimated_component_patching_start_time:
            The value to assign to the estimated_component_patching_start_time property of this MaintenanceRunSummary.
        :type estimated_component_patching_start_time: datetime

        """
        self.swagger_types = {
            'id': 'str',
            'compartment_id': 'str',
            'display_name': 'str',
            'description': 'str',
            'lifecycle_state': 'str',
            'lifecycle_details': 'str',
            'time_scheduled': 'datetime',
            'time_started': 'datetime',
            'time_ended': 'datetime',
            'target_resource_type': 'str',
            'target_resource_id': 'str',
            'maintenance_type': 'str',
            'patch_id': 'str',
            'maintenance_subtype': 'str',
            'peer_maintenance_run_id': 'str',
            'patching_mode': 'str',
            'patch_failure_count': 'int',
            'target_db_server_version': 'str',
            'target_storage_server_version': 'str',
            'is_custom_action_timeout_enabled': 'bool',
            'custom_action_timeout_in_mins': 'int',
            'current_custom_action_timeout_in_mins': 'int',
            'patching_status': 'str',
            'patching_start_time': 'datetime',
            'patching_end_time': 'datetime',
            'estimated_patching_time': 'EstimatedPatchingTime',
            'current_patching_component': 'str',
            'estimated_component_patching_start_time': 'datetime'
        }

        self.attribute_map = {
            'id': 'id',
            'compartment_id': 'compartmentId',
            'display_name': 'displayName',
            'description': 'description',
            'lifecycle_state': 'lifecycleState',
            'lifecycle_details': 'lifecycleDetails',
            'time_scheduled': 'timeScheduled',
            'time_started': 'timeStarted',
            'time_ended': 'timeEnded',
            'target_resource_type': 'targetResourceType',
            'target_resource_id': 'targetResourceId',
            'maintenance_type': 'maintenanceType',
            'patch_id': 'patchId',
            'maintenance_subtype': 'maintenanceSubtype',
            'peer_maintenance_run_id': 'peerMaintenanceRunId',
            'patching_mode': 'patchingMode',
            'patch_failure_count': 'patchFailureCount',
            'target_db_server_version': 'targetDbServerVersion',
            'target_storage_server_version': 'targetStorageServerVersion',
            'is_custom_action_timeout_enabled': 'isCustomActionTimeoutEnabled',
            'custom_action_timeout_in_mins': 'customActionTimeoutInMins',
            'current_custom_action_timeout_in_mins': 'currentCustomActionTimeoutInMins',
            'patching_status': 'patchingStatus',
            'patching_start_time': 'patchingStartTime',
            'patching_end_time': 'patchingEndTime',
            'estimated_patching_time': 'estimatedPatchingTime',
            'current_patching_component': 'currentPatchingComponent',
            'estimated_component_patching_start_time': 'estimatedComponentPatchingStartTime'
        }

        self._id = None
        self._compartment_id = None
        self._display_name = None
        self._description = None
        self._lifecycle_state = None
        self._lifecycle_details = None
        self._time_scheduled = None
        self._time_started = None
        self._time_ended = None
        self._target_resource_type = None
        self._target_resource_id = None
        self._maintenance_type = None
        self._patch_id = None
        self._maintenance_subtype = None
        self._peer_maintenance_run_id = None
        self._patching_mode = None
        self._patch_failure_count = None
        self._target_db_server_version = None
        self._target_storage_server_version = None
        self._is_custom_action_timeout_enabled = None
        self._custom_action_timeout_in_mins = None
        self._current_custom_action_timeout_in_mins = None
        self._patching_status = None
        self._patching_start_time = None
        self._patching_end_time = None
        self._estimated_patching_time = None
        self._current_patching_component = None
        self._estimated_component_patching_start_time = None

    @property
    def id(self):
        """
        **[Required]** Gets the id of this MaintenanceRunSummary.
        The OCID of the maintenance run.


        :return: The id of this MaintenanceRunSummary.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this MaintenanceRunSummary.
        The OCID of the maintenance run.


        :param id: The id of this MaintenanceRunSummary.
        :type: str
        """
        self._id = id

    @property
    def compartment_id(self):
        """
        **[Required]** Gets the compartment_id of this MaintenanceRunSummary.
        The OCID of the compartment.


        :return: The compartment_id of this MaintenanceRunSummary.
        :rtype: str
        """
        return self._compartment_id

    @compartment_id.setter
    def compartment_id(self, compartment_id):
        """
        Sets the compartment_id of this MaintenanceRunSummary.
        The OCID of the compartment.


        :param compartment_id: The compartment_id of this MaintenanceRunSummary.
        :type: str
        """
        self._compartment_id = compartment_id

    @property
    def display_name(self):
        """
        **[Required]** Gets the display_name of this MaintenanceRunSummary.
        The user-friendly name for the maintenance run.


        :return: The display_name of this MaintenanceRunSummary.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """
        Sets the display_name of this MaintenanceRunSummary.
        The user-friendly name for the maintenance run.


        :param display_name: The display_name of this MaintenanceRunSummary.
        :type: str
        """
        self._display_name = display_name

    @property
    def description(self):
        """
        Gets the description of this MaintenanceRunSummary.
        Description of the maintenance run.


        :return: The description of this MaintenanceRunSummary.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this MaintenanceRunSummary.
        Description of the maintenance run.


        :param description: The description of this MaintenanceRunSummary.
        :type: str
        """
        self._description = description

    @property
    def lifecycle_state(self):
        """
        **[Required]** Gets the lifecycle_state of this MaintenanceRunSummary.
        The current state of the maintenance run. For Autonomous Database on shared Exadata infrastructure, valid states are IN_PROGRESS, SUCCEEDED and FAILED.

        Allowed values for this property are: "SCHEDULED", "IN_PROGRESS", "SUCCEEDED", "SKIPPED", "FAILED", "UPDATING", "DELETING", "DELETED", "CANCELED", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The lifecycle_state of this MaintenanceRunSummary.
        :rtype: str
        """
        return self._lifecycle_state

    @lifecycle_state.setter
    def lifecycle_state(self, lifecycle_state):
        """
        Sets the lifecycle_state of this MaintenanceRunSummary.
        The current state of the maintenance run. For Autonomous Database on shared Exadata infrastructure, valid states are IN_PROGRESS, SUCCEEDED and FAILED.


        :param lifecycle_state: The lifecycle_state of this MaintenanceRunSummary.
        :type: str
        """
        allowed_values = ["SCHEDULED", "IN_PROGRESS", "SUCCEEDED", "SKIPPED", "FAILED", "UPDATING", "DELETING", "DELETED", "CANCELED"]
        if not value_allowed_none_or_none_sentinel(lifecycle_state, allowed_values):
            lifecycle_state = 'UNKNOWN_ENUM_VALUE'
        self._lifecycle_state = lifecycle_state

    @property
    def lifecycle_details(self):
        """
        Gets the lifecycle_details of this MaintenanceRunSummary.
        Additional information about the current lifecycle state.


        :return: The lifecycle_details of this MaintenanceRunSummary.
        :rtype: str
        """
        return self._lifecycle_details

    @lifecycle_details.setter
    def lifecycle_details(self, lifecycle_details):
        """
        Sets the lifecycle_details of this MaintenanceRunSummary.
        Additional information about the current lifecycle state.


        :param lifecycle_details: The lifecycle_details of this MaintenanceRunSummary.
        :type: str
        """
        self._lifecycle_details = lifecycle_details

    @property
    def time_scheduled(self):
        """
        **[Required]** Gets the time_scheduled of this MaintenanceRunSummary.
        The date and time the maintenance run is scheduled to occur.


        :return: The time_scheduled of this MaintenanceRunSummary.
        :rtype: datetime
        """
        return self._time_scheduled

    @time_scheduled.setter
    def time_scheduled(self, time_scheduled):
        """
        Sets the time_scheduled of this MaintenanceRunSummary.
        The date and time the maintenance run is scheduled to occur.


        :param time_scheduled: The time_scheduled of this MaintenanceRunSummary.
        :type: datetime
        """
        self._time_scheduled = time_scheduled

    @property
    def time_started(self):
        """
        Gets the time_started of this MaintenanceRunSummary.
        The date and time the maintenance run starts.


        :return: The time_started of this MaintenanceRunSummary.
        :rtype: datetime
        """
        return self._time_started

    @time_started.setter
    def time_started(self, time_started):
        """
        Sets the time_started of this MaintenanceRunSummary.
        The date and time the maintenance run starts.


        :param time_started: The time_started of this MaintenanceRunSummary.
        :type: datetime
        """
        self._time_started = time_started

    @property
    def time_ended(self):
        """
        Gets the time_ended of this MaintenanceRunSummary.
        The date and time the maintenance run was completed.


        :return: The time_ended of this MaintenanceRunSummary.
        :rtype: datetime
        """
        return self._time_ended

    @time_ended.setter
    def time_ended(self, time_ended):
        """
        Sets the time_ended of this MaintenanceRunSummary.
        The date and time the maintenance run was completed.


        :param time_ended: The time_ended of this MaintenanceRunSummary.
        :type: datetime
        """
        self._time_ended = time_ended

    @property
    def target_resource_type(self):
        """
        Gets the target_resource_type of this MaintenanceRunSummary.
        The type of the target resource on which the maintenance run occurs.

        Allowed values for this property are: "AUTONOMOUS_EXADATA_INFRASTRUCTURE", "AUTONOMOUS_CONTAINER_DATABASE", "EXADATA_DB_SYSTEM", "CLOUD_EXADATA_INFRASTRUCTURE", "EXACC_INFRASTRUCTURE", "AUTONOMOUS_VM_CLUSTER", "AUTONOMOUS_DATABASE", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The target_resource_type of this MaintenanceRunSummary.
        :rtype: str
        """
        return self._target_resource_type

    @target_resource_type.setter
    def target_resource_type(self, target_resource_type):
        """
        Sets the target_resource_type of this MaintenanceRunSummary.
        The type of the target resource on which the maintenance run occurs.


        :param target_resource_type: The target_resource_type of this MaintenanceRunSummary.
        :type: str
        """
        allowed_values = ["AUTONOMOUS_EXADATA_INFRASTRUCTURE", "AUTONOMOUS_CONTAINER_DATABASE", "EXADATA_DB_SYSTEM", "CLOUD_EXADATA_INFRASTRUCTURE", "EXACC_INFRASTRUCTURE", "AUTONOMOUS_VM_CLUSTER", "AUTONOMOUS_DATABASE"]
        if not value_allowed_none_or_none_sentinel(target_resource_type, allowed_values):
            target_resource_type = 'UNKNOWN_ENUM_VALUE'
        self._target_resource_type = target_resource_type

    @property
    def target_resource_id(self):
        """
        Gets the target_resource_id of this MaintenanceRunSummary.
        The ID of the target resource on which the maintenance run occurs.


        :return: The target_resource_id of this MaintenanceRunSummary.
        :rtype: str
        """
        return self._target_resource_id

    @target_resource_id.setter
    def target_resource_id(self, target_resource_id):
        """
        Sets the target_resource_id of this MaintenanceRunSummary.
        The ID of the target resource on which the maintenance run occurs.


        :param target_resource_id: The target_resource_id of this MaintenanceRunSummary.
        :type: str
        """
        self._target_resource_id = target_resource_id

    @property
    def maintenance_type(self):
        """
        Gets the maintenance_type of this MaintenanceRunSummary.
        Maintenance type.

        Allowed values for this property are: "PLANNED", "UNPLANNED", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The maintenance_type of this MaintenanceRunSummary.
        :rtype: str
        """
        return self._maintenance_type

    @maintenance_type.setter
    def maintenance_type(self, maintenance_type):
        """
        Sets the maintenance_type of this MaintenanceRunSummary.
        Maintenance type.


        :param maintenance_type: The maintenance_type of this MaintenanceRunSummary.
        :type: str
        """
        allowed_values = ["PLANNED", "UNPLANNED"]
        if not value_allowed_none_or_none_sentinel(maintenance_type, allowed_values):
            maintenance_type = 'UNKNOWN_ENUM_VALUE'
        self._maintenance_type = maintenance_type

    @property
    def patch_id(self):
        """
        Gets the patch_id of this MaintenanceRunSummary.
        The unique identifier of the patch. The identifier string includes the patch type, the Oracle Database version, and the patch creation date (using the format YYMMDD). For example, the identifier `ru_patch_19.9.0.0_201030` is used for an RU patch for Oracle Database 19.9.0.0 that was released October 30, 2020.


        :return: The patch_id of this MaintenanceRunSummary.
        :rtype: str
        """
        return self._patch_id

    @patch_id.setter
    def patch_id(self, patch_id):
        """
        Sets the patch_id of this MaintenanceRunSummary.
        The unique identifier of the patch. The identifier string includes the patch type, the Oracle Database version, and the patch creation date (using the format YYMMDD). For example, the identifier `ru_patch_19.9.0.0_201030` is used for an RU patch for Oracle Database 19.9.0.0 that was released October 30, 2020.


        :param patch_id: The patch_id of this MaintenanceRunSummary.
        :type: str
        """
        self._patch_id = patch_id

    @property
    def maintenance_subtype(self):
        """
        Gets the maintenance_subtype of this MaintenanceRunSummary.
        Maintenance sub-type.

        Allowed values for this property are: "QUARTERLY", "HARDWARE", "CRITICAL", "INFRASTRUCTURE", "DATABASE", "ONEOFF", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The maintenance_subtype of this MaintenanceRunSummary.
        :rtype: str
        """
        return self._maintenance_subtype

    @maintenance_subtype.setter
    def maintenance_subtype(self, maintenance_subtype):
        """
        Sets the maintenance_subtype of this MaintenanceRunSummary.
        Maintenance sub-type.


        :param maintenance_subtype: The maintenance_subtype of this MaintenanceRunSummary.
        :type: str
        """
        allowed_values = ["QUARTERLY", "HARDWARE", "CRITICAL", "INFRASTRUCTURE", "DATABASE", "ONEOFF"]
        if not value_allowed_none_or_none_sentinel(maintenance_subtype, allowed_values):
            maintenance_subtype = 'UNKNOWN_ENUM_VALUE'
        self._maintenance_subtype = maintenance_subtype

    @property
    def peer_maintenance_run_id(self):
        """
        Gets the peer_maintenance_run_id of this MaintenanceRunSummary.
        The `OCID`__ of the maintenance run for the Autonomous Data Guard association's peer container database.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :return: The peer_maintenance_run_id of this MaintenanceRunSummary.
        :rtype: str
        """
        return self._peer_maintenance_run_id

    @peer_maintenance_run_id.setter
    def peer_maintenance_run_id(self, peer_maintenance_run_id):
        """
        Sets the peer_maintenance_run_id of this MaintenanceRunSummary.
        The `OCID`__ of the maintenance run for the Autonomous Data Guard association's peer container database.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :param peer_maintenance_run_id: The peer_maintenance_run_id of this MaintenanceRunSummary.
        :type: str
        """
        self._peer_maintenance_run_id = peer_maintenance_run_id

    @property
    def patching_mode(self):
        """
        Gets the patching_mode of this MaintenanceRunSummary.
        Cloud Exadata infrastructure node patching method, either \"ROLLING\" or \"NONROLLING\". Default value is ROLLING.

        *IMPORTANT*: Non-rolling infrastructure patching involves system down time. See `Oracle-Managed Infrastructure Maintenance Updates`__ for more information.

        __ https://docs.cloud.oracle.com/iaas/Content/Database/Concepts/examaintenance.htm#Oracle

        Allowed values for this property are: "ROLLING", "NONROLLING", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The patching_mode of this MaintenanceRunSummary.
        :rtype: str
        """
        return self._patching_mode

    @patching_mode.setter
    def patching_mode(self, patching_mode):
        """
        Sets the patching_mode of this MaintenanceRunSummary.
        Cloud Exadata infrastructure node patching method, either \"ROLLING\" or \"NONROLLING\". Default value is ROLLING.

        *IMPORTANT*: Non-rolling infrastructure patching involves system down time. See `Oracle-Managed Infrastructure Maintenance Updates`__ for more information.

        __ https://docs.cloud.oracle.com/iaas/Content/Database/Concepts/examaintenance.htm#Oracle


        :param patching_mode: The patching_mode of this MaintenanceRunSummary.
        :type: str
        """
        allowed_values = ["ROLLING", "NONROLLING"]
        if not value_allowed_none_or_none_sentinel(patching_mode, allowed_values):
            patching_mode = 'UNKNOWN_ENUM_VALUE'
        self._patching_mode = patching_mode

    @property
    def patch_failure_count(self):
        """
        Gets the patch_failure_count of this MaintenanceRunSummary.
        Contain the patch failure count.


        :return: The patch_failure_count of this MaintenanceRunSummary.
        :rtype: int
        """
        return self._patch_failure_count

    @patch_failure_count.setter
    def patch_failure_count(self, patch_failure_count):
        """
        Sets the patch_failure_count of this MaintenanceRunSummary.
        Contain the patch failure count.


        :param patch_failure_count: The patch_failure_count of this MaintenanceRunSummary.
        :type: int
        """
        self._patch_failure_count = patch_failure_count

    @property
    def target_db_server_version(self):
        """
        Gets the target_db_server_version of this MaintenanceRunSummary.
        The target software version for the database server patching operation.


        :return: The target_db_server_version of this MaintenanceRunSummary.
        :rtype: str
        """
        return self._target_db_server_version

    @target_db_server_version.setter
    def target_db_server_version(self, target_db_server_version):
        """
        Sets the target_db_server_version of this MaintenanceRunSummary.
        The target software version for the database server patching operation.


        :param target_db_server_version: The target_db_server_version of this MaintenanceRunSummary.
        :type: str
        """
        self._target_db_server_version = target_db_server_version

    @property
    def target_storage_server_version(self):
        """
        Gets the target_storage_server_version of this MaintenanceRunSummary.
        The target Cell version that is to be patched to.


        :return: The target_storage_server_version of this MaintenanceRunSummary.
        :rtype: str
        """
        return self._target_storage_server_version

    @target_storage_server_version.setter
    def target_storage_server_version(self, target_storage_server_version):
        """
        Sets the target_storage_server_version of this MaintenanceRunSummary.
        The target Cell version that is to be patched to.


        :param target_storage_server_version: The target_storage_server_version of this MaintenanceRunSummary.
        :type: str
        """
        self._target_storage_server_version = target_storage_server_version

    @property
    def is_custom_action_timeout_enabled(self):
        """
        Gets the is_custom_action_timeout_enabled of this MaintenanceRunSummary.
        If true, enables the configuration of a custom action timeout (waiting period) between database servers patching operations.


        :return: The is_custom_action_timeout_enabled of this MaintenanceRunSummary.
        :rtype: bool
        """
        return self._is_custom_action_timeout_enabled

    @is_custom_action_timeout_enabled.setter
    def is_custom_action_timeout_enabled(self, is_custom_action_timeout_enabled):
        """
        Sets the is_custom_action_timeout_enabled of this MaintenanceRunSummary.
        If true, enables the configuration of a custom action timeout (waiting period) between database servers patching operations.


        :param is_custom_action_timeout_enabled: The is_custom_action_timeout_enabled of this MaintenanceRunSummary.
        :type: bool
        """
        self._is_custom_action_timeout_enabled = is_custom_action_timeout_enabled

    @property
    def custom_action_timeout_in_mins(self):
        """
        Gets the custom_action_timeout_in_mins of this MaintenanceRunSummary.
        Determines the amount of time the system will wait before the start of each database server patching operation.
        Specify a number of minutes, from 15 to 120.


        :return: The custom_action_timeout_in_mins of this MaintenanceRunSummary.
        :rtype: int
        """
        return self._custom_action_timeout_in_mins

    @custom_action_timeout_in_mins.setter
    def custom_action_timeout_in_mins(self, custom_action_timeout_in_mins):
        """
        Sets the custom_action_timeout_in_mins of this MaintenanceRunSummary.
        Determines the amount of time the system will wait before the start of each database server patching operation.
        Specify a number of minutes, from 15 to 120.


        :param custom_action_timeout_in_mins: The custom_action_timeout_in_mins of this MaintenanceRunSummary.
        :type: int
        """
        self._custom_action_timeout_in_mins = custom_action_timeout_in_mins

    @property
    def current_custom_action_timeout_in_mins(self):
        """
        Gets the current_custom_action_timeout_in_mins of this MaintenanceRunSummary.
        Extend current custom action timeout between the current database servers during waiting state, from 0 (zero) to 30 minutes.


        :return: The current_custom_action_timeout_in_mins of this MaintenanceRunSummary.
        :rtype: int
        """
        return self._current_custom_action_timeout_in_mins

    @current_custom_action_timeout_in_mins.setter
    def current_custom_action_timeout_in_mins(self, current_custom_action_timeout_in_mins):
        """
        Sets the current_custom_action_timeout_in_mins of this MaintenanceRunSummary.
        Extend current custom action timeout between the current database servers during waiting state, from 0 (zero) to 30 minutes.


        :param current_custom_action_timeout_in_mins: The current_custom_action_timeout_in_mins of this MaintenanceRunSummary.
        :type: int
        """
        self._current_custom_action_timeout_in_mins = current_custom_action_timeout_in_mins

    @property
    def patching_status(self):
        """
        Gets the patching_status of this MaintenanceRunSummary.
        The status of the patching operation.

        Allowed values for this property are: "PATCHING", "WAITING", "SCHEDULED", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The patching_status of this MaintenanceRunSummary.
        :rtype: str
        """
        return self._patching_status

    @patching_status.setter
    def patching_status(self, patching_status):
        """
        Sets the patching_status of this MaintenanceRunSummary.
        The status of the patching operation.


        :param patching_status: The patching_status of this MaintenanceRunSummary.
        :type: str
        """
        allowed_values = ["PATCHING", "WAITING", "SCHEDULED"]
        if not value_allowed_none_or_none_sentinel(patching_status, allowed_values):
            patching_status = 'UNKNOWN_ENUM_VALUE'
        self._patching_status = patching_status

    @property
    def patching_start_time(self):
        """
        Gets the patching_start_time of this MaintenanceRunSummary.
        The time when the patching operation started.


        :return: The patching_start_time of this MaintenanceRunSummary.
        :rtype: datetime
        """
        return self._patching_start_time

    @patching_start_time.setter
    def patching_start_time(self, patching_start_time):
        """
        Sets the patching_start_time of this MaintenanceRunSummary.
        The time when the patching operation started.


        :param patching_start_time: The patching_start_time of this MaintenanceRunSummary.
        :type: datetime
        """
        self._patching_start_time = patching_start_time

    @property
    def patching_end_time(self):
        """
        Gets the patching_end_time of this MaintenanceRunSummary.
        The time when the patching operation ended.


        :return: The patching_end_time of this MaintenanceRunSummary.
        :rtype: datetime
        """
        return self._patching_end_time

    @patching_end_time.setter
    def patching_end_time(self, patching_end_time):
        """
        Sets the patching_end_time of this MaintenanceRunSummary.
        The time when the patching operation ended.


        :param patching_end_time: The patching_end_time of this MaintenanceRunSummary.
        :type: datetime
        """
        self._patching_end_time = patching_end_time

    @property
    def estimated_patching_time(self):
        """
        Gets the estimated_patching_time of this MaintenanceRunSummary.

        :return: The estimated_patching_time of this MaintenanceRunSummary.
        :rtype: oci.database.models.EstimatedPatchingTime
        """
        return self._estimated_patching_time

    @estimated_patching_time.setter
    def estimated_patching_time(self, estimated_patching_time):
        """
        Sets the estimated_patching_time of this MaintenanceRunSummary.

        :param estimated_patching_time: The estimated_patching_time of this MaintenanceRunSummary.
        :type: oci.database.models.EstimatedPatchingTime
        """
        self._estimated_patching_time = estimated_patching_time

    @property
    def current_patching_component(self):
        """
        Gets the current_patching_component of this MaintenanceRunSummary.
        The name of the current infrastruture component that is getting patched.


        :return: The current_patching_component of this MaintenanceRunSummary.
        :rtype: str
        """
        return self._current_patching_component

    @current_patching_component.setter
    def current_patching_component(self, current_patching_component):
        """
        Sets the current_patching_component of this MaintenanceRunSummary.
        The name of the current infrastruture component that is getting patched.


        :param current_patching_component: The current_patching_component of this MaintenanceRunSummary.
        :type: str
        """
        self._current_patching_component = current_patching_component

    @property
    def estimated_component_patching_start_time(self):
        """
        Gets the estimated_component_patching_start_time of this MaintenanceRunSummary.
        The estimated start time of the next infrastruture component patching operation.


        :return: The estimated_component_patching_start_time of this MaintenanceRunSummary.
        :rtype: datetime
        """
        return self._estimated_component_patching_start_time

    @estimated_component_patching_start_time.setter
    def estimated_component_patching_start_time(self, estimated_component_patching_start_time):
        """
        Sets the estimated_component_patching_start_time of this MaintenanceRunSummary.
        The estimated start time of the next infrastruture component patching operation.


        :param estimated_component_patching_start_time: The estimated_component_patching_start_time of this MaintenanceRunSummary.
        :type: datetime
        """
        self._estimated_component_patching_start_time = estimated_component_patching_start_time

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
