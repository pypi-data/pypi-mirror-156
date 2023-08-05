# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class ImportDataAssetJobResult(object):
    """
    Information about a data asset import operation.
    """

    #: A constant which can be used with the import_job_execution_status property of a ImportDataAssetJobResult.
    #: This constant has a value of "CREATED"
    IMPORT_JOB_EXECUTION_STATUS_CREATED = "CREATED"

    #: A constant which can be used with the import_job_execution_status property of a ImportDataAssetJobResult.
    #: This constant has a value of "IN_PROGRESS"
    IMPORT_JOB_EXECUTION_STATUS_IN_PROGRESS = "IN_PROGRESS"

    #: A constant which can be used with the import_job_execution_status property of a ImportDataAssetJobResult.
    #: This constant has a value of "INACTIVE"
    IMPORT_JOB_EXECUTION_STATUS_INACTIVE = "INACTIVE"

    #: A constant which can be used with the import_job_execution_status property of a ImportDataAssetJobResult.
    #: This constant has a value of "FAILED"
    IMPORT_JOB_EXECUTION_STATUS_FAILED = "FAILED"

    #: A constant which can be used with the import_job_execution_status property of a ImportDataAssetJobResult.
    #: This constant has a value of "SUCCEEDED"
    IMPORT_JOB_EXECUTION_STATUS_SUCCEEDED = "SUCCEEDED"

    #: A constant which can be used with the import_job_execution_status property of a ImportDataAssetJobResult.
    #: This constant has a value of "CANCELED"
    IMPORT_JOB_EXECUTION_STATUS_CANCELED = "CANCELED"

    #: A constant which can be used with the import_job_execution_status property of a ImportDataAssetJobResult.
    #: This constant has a value of "SUCCEEDED_WITH_WARNINGS"
    IMPORT_JOB_EXECUTION_STATUS_SUCCEEDED_WITH_WARNINGS = "SUCCEEDED_WITH_WARNINGS"

    def __init__(self, **kwargs):
        """
        Initializes a new ImportDataAssetJobResult object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param data_asset_key:
            The value to assign to the data_asset_key property of this ImportDataAssetJobResult.
        :type data_asset_key: str

        :param import_job_definition_key:
            The value to assign to the import_job_definition_key property of this ImportDataAssetJobResult.
        :type import_job_definition_key: str

        :param import_job_key:
            The value to assign to the import_job_key property of this ImportDataAssetJobResult.
        :type import_job_key: str

        :param import_job_execution_key:
            The value to assign to the import_job_execution_key property of this ImportDataAssetJobResult.
        :type import_job_execution_key: str

        :param import_job_execution_status:
            The value to assign to the import_job_execution_status property of this ImportDataAssetJobResult.
            Allowed values for this property are: "CREATED", "IN_PROGRESS", "INACTIVE", "FAILED", "SUCCEEDED", "CANCELED", "SUCCEEDED_WITH_WARNINGS", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type import_job_execution_status: str

        """
        self.swagger_types = {
            'data_asset_key': 'str',
            'import_job_definition_key': 'str',
            'import_job_key': 'str',
            'import_job_execution_key': 'str',
            'import_job_execution_status': 'str'
        }

        self.attribute_map = {
            'data_asset_key': 'dataAssetKey',
            'import_job_definition_key': 'importJobDefinitionKey',
            'import_job_key': 'importJobKey',
            'import_job_execution_key': 'importJobExecutionKey',
            'import_job_execution_status': 'importJobExecutionStatus'
        }

        self._data_asset_key = None
        self._import_job_definition_key = None
        self._import_job_key = None
        self._import_job_execution_key = None
        self._import_job_execution_status = None

    @property
    def data_asset_key(self):
        """
        **[Required]** Gets the data_asset_key of this ImportDataAssetJobResult.
        The unique key of the data asset on which import is triggered.


        :return: The data_asset_key of this ImportDataAssetJobResult.
        :rtype: str
        """
        return self._data_asset_key

    @data_asset_key.setter
    def data_asset_key(self, data_asset_key):
        """
        Sets the data_asset_key of this ImportDataAssetJobResult.
        The unique key of the data asset on which import is triggered.


        :param data_asset_key: The data_asset_key of this ImportDataAssetJobResult.
        :type: str
        """
        self._data_asset_key = data_asset_key

    @property
    def import_job_definition_key(self):
        """
        Gets the import_job_definition_key of this ImportDataAssetJobResult.
        The unique key of the job definition resource that is used for the import.


        :return: The import_job_definition_key of this ImportDataAssetJobResult.
        :rtype: str
        """
        return self._import_job_definition_key

    @import_job_definition_key.setter
    def import_job_definition_key(self, import_job_definition_key):
        """
        Sets the import_job_definition_key of this ImportDataAssetJobResult.
        The unique key of the job definition resource that is used for the import.


        :param import_job_definition_key: The import_job_definition_key of this ImportDataAssetJobResult.
        :type: str
        """
        self._import_job_definition_key = import_job_definition_key

    @property
    def import_job_key(self):
        """
        Gets the import_job_key of this ImportDataAssetJobResult.
        The unique key of the job policy for the import.


        :return: The import_job_key of this ImportDataAssetJobResult.
        :rtype: str
        """
        return self._import_job_key

    @import_job_key.setter
    def import_job_key(self, import_job_key):
        """
        Sets the import_job_key of this ImportDataAssetJobResult.
        The unique key of the job policy for the import.


        :param import_job_key: The import_job_key of this ImportDataAssetJobResult.
        :type: str
        """
        self._import_job_key = import_job_key

    @property
    def import_job_execution_key(self):
        """
        Gets the import_job_execution_key of this ImportDataAssetJobResult.
        The unique key of the parent job execution for which the log resource is created.


        :return: The import_job_execution_key of this ImportDataAssetJobResult.
        :rtype: str
        """
        return self._import_job_execution_key

    @import_job_execution_key.setter
    def import_job_execution_key(self, import_job_execution_key):
        """
        Sets the import_job_execution_key of this ImportDataAssetJobResult.
        The unique key of the parent job execution for which the log resource is created.


        :param import_job_execution_key: The import_job_execution_key of this ImportDataAssetJobResult.
        :type: str
        """
        self._import_job_execution_key = import_job_execution_key

    @property
    def import_job_execution_status(self):
        """
        Gets the import_job_execution_status of this ImportDataAssetJobResult.
        The status of the import job execution.

        Allowed values for this property are: "CREATED", "IN_PROGRESS", "INACTIVE", "FAILED", "SUCCEEDED", "CANCELED", "SUCCEEDED_WITH_WARNINGS", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The import_job_execution_status of this ImportDataAssetJobResult.
        :rtype: str
        """
        return self._import_job_execution_status

    @import_job_execution_status.setter
    def import_job_execution_status(self, import_job_execution_status):
        """
        Sets the import_job_execution_status of this ImportDataAssetJobResult.
        The status of the import job execution.


        :param import_job_execution_status: The import_job_execution_status of this ImportDataAssetJobResult.
        :type: str
        """
        allowed_values = ["CREATED", "IN_PROGRESS", "INACTIVE", "FAILED", "SUCCEEDED", "CANCELED", "SUCCEEDED_WITH_WARNINGS"]
        if not value_allowed_none_or_none_sentinel(import_job_execution_status, allowed_values):
            import_job_execution_status = 'UNKNOWN_ENUM_VALUE'
        self._import_job_execution_status = import_job_execution_status

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
