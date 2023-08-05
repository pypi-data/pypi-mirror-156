# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class PhaseStatus(object):
    """
    Job phase status details.
    """

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_VALIDATE_TGT"
    NAME_ODMS_VALIDATE_TGT = "ODMS_VALIDATE_TGT"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_VALIDATE_SRC"
    NAME_ODMS_VALIDATE_SRC = "ODMS_VALIDATE_SRC"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_VALIDATE_PREMIGRATION_ADVISOR"
    NAME_ODMS_VALIDATE_PREMIGRATION_ADVISOR = "ODMS_VALIDATE_PREMIGRATION_ADVISOR"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_VALIDATE_GG_HUB"
    NAME_ODMS_VALIDATE_GG_HUB = "ODMS_VALIDATE_GG_HUB"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_VALIDATE_DATAPUMP_SETTINGS"
    NAME_ODMS_VALIDATE_DATAPUMP_SETTINGS = "ODMS_VALIDATE_DATAPUMP_SETTINGS"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_VALIDATE_DATAPUMP_SETTINGS_SRC"
    NAME_ODMS_VALIDATE_DATAPUMP_SETTINGS_SRC = "ODMS_VALIDATE_DATAPUMP_SETTINGS_SRC"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_VALIDATE_DATAPUMP_SETTINGS_TGT"
    NAME_ODMS_VALIDATE_DATAPUMP_SETTINGS_TGT = "ODMS_VALIDATE_DATAPUMP_SETTINGS_TGT"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_VALIDATE_DATAPUMP_SRC"
    NAME_ODMS_VALIDATE_DATAPUMP_SRC = "ODMS_VALIDATE_DATAPUMP_SRC"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_VALIDATE_DATAPUMP_ESTIMATE_SRC"
    NAME_ODMS_VALIDATE_DATAPUMP_ESTIMATE_SRC = "ODMS_VALIDATE_DATAPUMP_ESTIMATE_SRC"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_VALIDATE"
    NAME_ODMS_VALIDATE = "ODMS_VALIDATE"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_PREPARE"
    NAME_ODMS_PREPARE = "ODMS_PREPARE"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_INITIAL_LOAD_EXPORT"
    NAME_ODMS_INITIAL_LOAD_EXPORT = "ODMS_INITIAL_LOAD_EXPORT"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_DATA_UPLOAD"
    NAME_ODMS_DATA_UPLOAD = "ODMS_DATA_UPLOAD"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_INITIAL_LOAD_IMPORT"
    NAME_ODMS_INITIAL_LOAD_IMPORT = "ODMS_INITIAL_LOAD_IMPORT"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_POST_INITIAL_LOAD"
    NAME_ODMS_POST_INITIAL_LOAD = "ODMS_POST_INITIAL_LOAD"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_PREPARE_REPLICATION_TARGET"
    NAME_ODMS_PREPARE_REPLICATION_TARGET = "ODMS_PREPARE_REPLICATION_TARGET"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_MONITOR_REPLICATION_LAG"
    NAME_ODMS_MONITOR_REPLICATION_LAG = "ODMS_MONITOR_REPLICATION_LAG"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_SWITCHOVER"
    NAME_ODMS_SWITCHOVER = "ODMS_SWITCHOVER"

    #: A constant which can be used with the name property of a PhaseStatus.
    #: This constant has a value of "ODMS_CLEANUP"
    NAME_ODMS_CLEANUP = "ODMS_CLEANUP"

    #: A constant which can be used with the status property of a PhaseStatus.
    #: This constant has a value of "PENDING"
    STATUS_PENDING = "PENDING"

    #: A constant which can be used with the status property of a PhaseStatus.
    #: This constant has a value of "STARTED"
    STATUS_STARTED = "STARTED"

    #: A constant which can be used with the status property of a PhaseStatus.
    #: This constant has a value of "COMPLETED"
    STATUS_COMPLETED = "COMPLETED"

    #: A constant which can be used with the status property of a PhaseStatus.
    #: This constant has a value of "FAILED"
    STATUS_FAILED = "FAILED"

    def __init__(self, **kwargs):
        """
        Initializes a new PhaseStatus object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param name:
            The value to assign to the name property of this PhaseStatus.
            Allowed values for this property are: "ODMS_VALIDATE_TGT", "ODMS_VALIDATE_SRC", "ODMS_VALIDATE_PREMIGRATION_ADVISOR", "ODMS_VALIDATE_GG_HUB", "ODMS_VALIDATE_DATAPUMP_SETTINGS", "ODMS_VALIDATE_DATAPUMP_SETTINGS_SRC", "ODMS_VALIDATE_DATAPUMP_SETTINGS_TGT", "ODMS_VALIDATE_DATAPUMP_SRC", "ODMS_VALIDATE_DATAPUMP_ESTIMATE_SRC", "ODMS_VALIDATE", "ODMS_PREPARE", "ODMS_INITIAL_LOAD_EXPORT", "ODMS_DATA_UPLOAD", "ODMS_INITIAL_LOAD_IMPORT", "ODMS_POST_INITIAL_LOAD", "ODMS_PREPARE_REPLICATION_TARGET", "ODMS_MONITOR_REPLICATION_LAG", "ODMS_SWITCHOVER", "ODMS_CLEANUP", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type name: str

        :param status:
            The value to assign to the status property of this PhaseStatus.
            Allowed values for this property are: "PENDING", "STARTED", "COMPLETED", "FAILED", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type status: str

        :param duration_in_ms:
            The value to assign to the duration_in_ms property of this PhaseStatus.
        :type duration_in_ms: int

        :param is_advisor_report_available:
            The value to assign to the is_advisor_report_available property of this PhaseStatus.
        :type is_advisor_report_available: bool

        :param extract:
            The value to assign to the extract property of this PhaseStatus.
        :type extract: list[oci.database_migration.models.PhaseExtractEntry]

        :param log_location:
            The value to assign to the log_location property of this PhaseStatus.
        :type log_location: oci.database_migration.models.LogLocationBucketDetails

        :param progress:
            The value to assign to the progress property of this PhaseStatus.
        :type progress: int

        """
        self.swagger_types = {
            'name': 'str',
            'status': 'str',
            'duration_in_ms': 'int',
            'is_advisor_report_available': 'bool',
            'extract': 'list[PhaseExtractEntry]',
            'log_location': 'LogLocationBucketDetails',
            'progress': 'int'
        }

        self.attribute_map = {
            'name': 'name',
            'status': 'status',
            'duration_in_ms': 'durationInMs',
            'is_advisor_report_available': 'isAdvisorReportAvailable',
            'extract': 'extract',
            'log_location': 'logLocation',
            'progress': 'progress'
        }

        self._name = None
        self._status = None
        self._duration_in_ms = None
        self._is_advisor_report_available = None
        self._extract = None
        self._log_location = None
        self._progress = None

    @property
    def name(self):
        """
        **[Required]** Gets the name of this PhaseStatus.
        Phase name

        Allowed values for this property are: "ODMS_VALIDATE_TGT", "ODMS_VALIDATE_SRC", "ODMS_VALIDATE_PREMIGRATION_ADVISOR", "ODMS_VALIDATE_GG_HUB", "ODMS_VALIDATE_DATAPUMP_SETTINGS", "ODMS_VALIDATE_DATAPUMP_SETTINGS_SRC", "ODMS_VALIDATE_DATAPUMP_SETTINGS_TGT", "ODMS_VALIDATE_DATAPUMP_SRC", "ODMS_VALIDATE_DATAPUMP_ESTIMATE_SRC", "ODMS_VALIDATE", "ODMS_PREPARE", "ODMS_INITIAL_LOAD_EXPORT", "ODMS_DATA_UPLOAD", "ODMS_INITIAL_LOAD_IMPORT", "ODMS_POST_INITIAL_LOAD", "ODMS_PREPARE_REPLICATION_TARGET", "ODMS_MONITOR_REPLICATION_LAG", "ODMS_SWITCHOVER", "ODMS_CLEANUP", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The name of this PhaseStatus.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this PhaseStatus.
        Phase name


        :param name: The name of this PhaseStatus.
        :type: str
        """
        allowed_values = ["ODMS_VALIDATE_TGT", "ODMS_VALIDATE_SRC", "ODMS_VALIDATE_PREMIGRATION_ADVISOR", "ODMS_VALIDATE_GG_HUB", "ODMS_VALIDATE_DATAPUMP_SETTINGS", "ODMS_VALIDATE_DATAPUMP_SETTINGS_SRC", "ODMS_VALIDATE_DATAPUMP_SETTINGS_TGT", "ODMS_VALIDATE_DATAPUMP_SRC", "ODMS_VALIDATE_DATAPUMP_ESTIMATE_SRC", "ODMS_VALIDATE", "ODMS_PREPARE", "ODMS_INITIAL_LOAD_EXPORT", "ODMS_DATA_UPLOAD", "ODMS_INITIAL_LOAD_IMPORT", "ODMS_POST_INITIAL_LOAD", "ODMS_PREPARE_REPLICATION_TARGET", "ODMS_MONITOR_REPLICATION_LAG", "ODMS_SWITCHOVER", "ODMS_CLEANUP"]
        if not value_allowed_none_or_none_sentinel(name, allowed_values):
            name = 'UNKNOWN_ENUM_VALUE'
        self._name = name

    @property
    def status(self):
        """
        **[Required]** Gets the status of this PhaseStatus.
        Phase status

        Allowed values for this property are: "PENDING", "STARTED", "COMPLETED", "FAILED", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The status of this PhaseStatus.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """
        Sets the status of this PhaseStatus.
        Phase status


        :param status: The status of this PhaseStatus.
        :type: str
        """
        allowed_values = ["PENDING", "STARTED", "COMPLETED", "FAILED"]
        if not value_allowed_none_or_none_sentinel(status, allowed_values):
            status = 'UNKNOWN_ENUM_VALUE'
        self._status = status

    @property
    def duration_in_ms(self):
        """
        **[Required]** Gets the duration_in_ms of this PhaseStatus.
        Duration of the phase in milliseconds


        :return: The duration_in_ms of this PhaseStatus.
        :rtype: int
        """
        return self._duration_in_ms

    @duration_in_ms.setter
    def duration_in_ms(self, duration_in_ms):
        """
        Sets the duration_in_ms of this PhaseStatus.
        Duration of the phase in milliseconds


        :param duration_in_ms: The duration_in_ms of this PhaseStatus.
        :type: int
        """
        self._duration_in_ms = duration_in_ms

    @property
    def is_advisor_report_available(self):
        """
        Gets the is_advisor_report_available of this PhaseStatus.
        True if a Pre-Migration Advisor report is available for this phase. False or null if no report is available.


        :return: The is_advisor_report_available of this PhaseStatus.
        :rtype: bool
        """
        return self._is_advisor_report_available

    @is_advisor_report_available.setter
    def is_advisor_report_available(self, is_advisor_report_available):
        """
        Sets the is_advisor_report_available of this PhaseStatus.
        True if a Pre-Migration Advisor report is available for this phase. False or null if no report is available.


        :param is_advisor_report_available: The is_advisor_report_available of this PhaseStatus.
        :type: bool
        """
        self._is_advisor_report_available = is_advisor_report_available

    @property
    def extract(self):
        """
        Gets the extract of this PhaseStatus.
        Summary of phase status results.


        :return: The extract of this PhaseStatus.
        :rtype: list[oci.database_migration.models.PhaseExtractEntry]
        """
        return self._extract

    @extract.setter
    def extract(self, extract):
        """
        Sets the extract of this PhaseStatus.
        Summary of phase status results.


        :param extract: The extract of this PhaseStatus.
        :type: list[oci.database_migration.models.PhaseExtractEntry]
        """
        self._extract = extract

    @property
    def log_location(self):
        """
        Gets the log_location of this PhaseStatus.

        :return: The log_location of this PhaseStatus.
        :rtype: oci.database_migration.models.LogLocationBucketDetails
        """
        return self._log_location

    @log_location.setter
    def log_location(self, log_location):
        """
        Sets the log_location of this PhaseStatus.

        :param log_location: The log_location of this PhaseStatus.
        :type: oci.database_migration.models.LogLocationBucketDetails
        """
        self._log_location = log_location

    @property
    def progress(self):
        """
        Gets the progress of this PhaseStatus.
        Percent progress of job phase.


        :return: The progress of this PhaseStatus.
        :rtype: int
        """
        return self._progress

    @progress.setter
    def progress(self, progress):
        """
        Sets the progress of this PhaseStatus.
        Percent progress of job phase.


        :param progress: The progress of this PhaseStatus.
        :type: int
        """
        self._progress = progress

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
