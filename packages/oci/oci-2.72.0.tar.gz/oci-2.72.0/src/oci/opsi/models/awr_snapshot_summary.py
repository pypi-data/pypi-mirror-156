# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class AwrSnapshotSummary(object):
    """
    The AWR snapshot summary of one snapshot.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new AwrSnapshotSummary object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param awr_source_database_id:
            The value to assign to the awr_source_database_id property of this AwrSnapshotSummary.
        :type awr_source_database_id: str

        :param instance_number:
            The value to assign to the instance_number property of this AwrSnapshotSummary.
        :type instance_number: int

        :param time_db_startup:
            The value to assign to the time_db_startup property of this AwrSnapshotSummary.
        :type time_db_startup: datetime

        :param time_snapshot_begin:
            The value to assign to the time_snapshot_begin property of this AwrSnapshotSummary.
        :type time_snapshot_begin: datetime

        :param time_snapshot_end:
            The value to assign to the time_snapshot_end property of this AwrSnapshotSummary.
        :type time_snapshot_end: datetime

        :param snapshot_identifier:
            The value to assign to the snapshot_identifier property of this AwrSnapshotSummary.
        :type snapshot_identifier: int

        :param error_count:
            The value to assign to the error_count property of this AwrSnapshotSummary.
        :type error_count: int

        """
        self.swagger_types = {
            'awr_source_database_id': 'str',
            'instance_number': 'int',
            'time_db_startup': 'datetime',
            'time_snapshot_begin': 'datetime',
            'time_snapshot_end': 'datetime',
            'snapshot_identifier': 'int',
            'error_count': 'int'
        }

        self.attribute_map = {
            'awr_source_database_id': 'awrSourceDatabaseId',
            'instance_number': 'instanceNumber',
            'time_db_startup': 'timeDbStartup',
            'time_snapshot_begin': 'timeSnapshotBegin',
            'time_snapshot_end': 'timeSnapshotEnd',
            'snapshot_identifier': 'snapshotIdentifier',
            'error_count': 'errorCount'
        }

        self._awr_source_database_id = None
        self._instance_number = None
        self._time_db_startup = None
        self._time_snapshot_begin = None
        self._time_snapshot_end = None
        self._snapshot_identifier = None
        self._error_count = None

    @property
    def awr_source_database_id(self):
        """
        **[Required]** Gets the awr_source_database_id of this AwrSnapshotSummary.
        DatabaseId of the Source database for which AWR Data will be uploaded to AWR Hub.


        :return: The awr_source_database_id of this AwrSnapshotSummary.
        :rtype: str
        """
        return self._awr_source_database_id

    @awr_source_database_id.setter
    def awr_source_database_id(self, awr_source_database_id):
        """
        Sets the awr_source_database_id of this AwrSnapshotSummary.
        DatabaseId of the Source database for which AWR Data will be uploaded to AWR Hub.


        :param awr_source_database_id: The awr_source_database_id of this AwrSnapshotSummary.
        :type: str
        """
        self._awr_source_database_id = awr_source_database_id

    @property
    def instance_number(self):
        """
        Gets the instance_number of this AwrSnapshotSummary.
        The database instance number.


        :return: The instance_number of this AwrSnapshotSummary.
        :rtype: int
        """
        return self._instance_number

    @instance_number.setter
    def instance_number(self, instance_number):
        """
        Sets the instance_number of this AwrSnapshotSummary.
        The database instance number.


        :param instance_number: The instance_number of this AwrSnapshotSummary.
        :type: int
        """
        self._instance_number = instance_number

    @property
    def time_db_startup(self):
        """
        Gets the time_db_startup of this AwrSnapshotSummary.
        The timestamp of the database startup.


        :return: The time_db_startup of this AwrSnapshotSummary.
        :rtype: datetime
        """
        return self._time_db_startup

    @time_db_startup.setter
    def time_db_startup(self, time_db_startup):
        """
        Sets the time_db_startup of this AwrSnapshotSummary.
        The timestamp of the database startup.


        :param time_db_startup: The time_db_startup of this AwrSnapshotSummary.
        :type: datetime
        """
        self._time_db_startup = time_db_startup

    @property
    def time_snapshot_begin(self):
        """
        Gets the time_snapshot_begin of this AwrSnapshotSummary.
        The start time of the snapshot.


        :return: The time_snapshot_begin of this AwrSnapshotSummary.
        :rtype: datetime
        """
        return self._time_snapshot_begin

    @time_snapshot_begin.setter
    def time_snapshot_begin(self, time_snapshot_begin):
        """
        Sets the time_snapshot_begin of this AwrSnapshotSummary.
        The start time of the snapshot.


        :param time_snapshot_begin: The time_snapshot_begin of this AwrSnapshotSummary.
        :type: datetime
        """
        self._time_snapshot_begin = time_snapshot_begin

    @property
    def time_snapshot_end(self):
        """
        Gets the time_snapshot_end of this AwrSnapshotSummary.
        The end time of the snapshot.


        :return: The time_snapshot_end of this AwrSnapshotSummary.
        :rtype: datetime
        """
        return self._time_snapshot_end

    @time_snapshot_end.setter
    def time_snapshot_end(self, time_snapshot_end):
        """
        Sets the time_snapshot_end of this AwrSnapshotSummary.
        The end time of the snapshot.


        :param time_snapshot_end: The time_snapshot_end of this AwrSnapshotSummary.
        :type: datetime
        """
        self._time_snapshot_end = time_snapshot_end

    @property
    def snapshot_identifier(self):
        """
        **[Required]** Gets the snapshot_identifier of this AwrSnapshotSummary.
        The identifier of the snapshot.


        :return: The snapshot_identifier of this AwrSnapshotSummary.
        :rtype: int
        """
        return self._snapshot_identifier

    @snapshot_identifier.setter
    def snapshot_identifier(self, snapshot_identifier):
        """
        Sets the snapshot_identifier of this AwrSnapshotSummary.
        The identifier of the snapshot.


        :param snapshot_identifier: The snapshot_identifier of this AwrSnapshotSummary.
        :type: int
        """
        self._snapshot_identifier = snapshot_identifier

    @property
    def error_count(self):
        """
        Gets the error_count of this AwrSnapshotSummary.
        The total number of errors.


        :return: The error_count of this AwrSnapshotSummary.
        :rtype: int
        """
        return self._error_count

    @error_count.setter
    def error_count(self, error_count):
        """
        Sets the error_count of this AwrSnapshotSummary.
        The total number of errors.


        :param error_count: The error_count of this AwrSnapshotSummary.
        :type: int
        """
        self._error_count = error_count

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
