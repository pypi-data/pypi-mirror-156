# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

from __future__ import absolute_import

from .change_database_tools_connection_compartment_details import ChangeDatabaseToolsConnectionCompartmentDetails
from .change_database_tools_private_endpoint_compartment_details import ChangeDatabaseToolsPrivateEndpointCompartmentDetails
from .create_database_tools_connection_details import CreateDatabaseToolsConnectionDetails
from .create_database_tools_connection_my_sql_details import CreateDatabaseToolsConnectionMySqlDetails
from .create_database_tools_connection_oracle_database_details import CreateDatabaseToolsConnectionOracleDatabaseDetails
from .create_database_tools_private_endpoint_details import CreateDatabaseToolsPrivateEndpointDetails
from .create_database_tools_related_resource_details import CreateDatabaseToolsRelatedResourceDetails
from .create_database_tools_related_resource_my_sql_details import CreateDatabaseToolsRelatedResourceMySqlDetails
from .database_tools_connection import DatabaseToolsConnection
from .database_tools_connection_collection import DatabaseToolsConnectionCollection
from .database_tools_connection_my_sql import DatabaseToolsConnectionMySql
from .database_tools_connection_my_sql_summary import DatabaseToolsConnectionMySqlSummary
from .database_tools_connection_oracle_database import DatabaseToolsConnectionOracleDatabase
from .database_tools_connection_oracle_database_summary import DatabaseToolsConnectionOracleDatabaseSummary
from .database_tools_connection_summary import DatabaseToolsConnectionSummary
from .database_tools_endpoint_service import DatabaseToolsEndpointService
from .database_tools_endpoint_service_collection import DatabaseToolsEndpointServiceCollection
from .database_tools_endpoint_service_summary import DatabaseToolsEndpointServiceSummary
from .database_tools_key_store import DatabaseToolsKeyStore
from .database_tools_key_store_content import DatabaseToolsKeyStoreContent
from .database_tools_key_store_content_details import DatabaseToolsKeyStoreContentDetails
from .database_tools_key_store_content_my_sql import DatabaseToolsKeyStoreContentMySql
from .database_tools_key_store_content_my_sql_details import DatabaseToolsKeyStoreContentMySqlDetails
from .database_tools_key_store_content_my_sql_summary import DatabaseToolsKeyStoreContentMySqlSummary
from .database_tools_key_store_content_secret_id import DatabaseToolsKeyStoreContentSecretId
from .database_tools_key_store_content_secret_id_details import DatabaseToolsKeyStoreContentSecretIdDetails
from .database_tools_key_store_content_secret_id_my_sql import DatabaseToolsKeyStoreContentSecretIdMySql
from .database_tools_key_store_content_secret_id_my_sql_details import DatabaseToolsKeyStoreContentSecretIdMySqlDetails
from .database_tools_key_store_content_secret_id_my_sql_summary import DatabaseToolsKeyStoreContentSecretIdMySqlSummary
from .database_tools_key_store_content_secret_id_summary import DatabaseToolsKeyStoreContentSecretIdSummary
from .database_tools_key_store_content_summary import DatabaseToolsKeyStoreContentSummary
from .database_tools_key_store_details import DatabaseToolsKeyStoreDetails
from .database_tools_key_store_my_sql import DatabaseToolsKeyStoreMySql
from .database_tools_key_store_my_sql_details import DatabaseToolsKeyStoreMySqlDetails
from .database_tools_key_store_my_sql_summary import DatabaseToolsKeyStoreMySqlSummary
from .database_tools_key_store_password import DatabaseToolsKeyStorePassword
from .database_tools_key_store_password_details import DatabaseToolsKeyStorePasswordDetails
from .database_tools_key_store_password_my_sql import DatabaseToolsKeyStorePasswordMySql
from .database_tools_key_store_password_my_sql_details import DatabaseToolsKeyStorePasswordMySqlDetails
from .database_tools_key_store_password_my_sql_summary import DatabaseToolsKeyStorePasswordMySqlSummary
from .database_tools_key_store_password_secret_id import DatabaseToolsKeyStorePasswordSecretId
from .database_tools_key_store_password_secret_id_details import DatabaseToolsKeyStorePasswordSecretIdDetails
from .database_tools_key_store_password_secret_id_my_sql import DatabaseToolsKeyStorePasswordSecretIdMySql
from .database_tools_key_store_password_secret_id_my_sql_details import DatabaseToolsKeyStorePasswordSecretIdMySqlDetails
from .database_tools_key_store_password_secret_id_my_sql_summary import DatabaseToolsKeyStorePasswordSecretIdMySqlSummary
from .database_tools_key_store_password_secret_id_summary import DatabaseToolsKeyStorePasswordSecretIdSummary
from .database_tools_key_store_password_summary import DatabaseToolsKeyStorePasswordSummary
from .database_tools_key_store_summary import DatabaseToolsKeyStoreSummary
from .database_tools_private_endpoint import DatabaseToolsPrivateEndpoint
from .database_tools_private_endpoint_collection import DatabaseToolsPrivateEndpointCollection
from .database_tools_private_endpoint_reverse_connection_configuration import DatabaseToolsPrivateEndpointReverseConnectionConfiguration
from .database_tools_private_endpoint_reverse_connections_source_ip import DatabaseToolsPrivateEndpointReverseConnectionsSourceIp
from .database_tools_private_endpoint_summary import DatabaseToolsPrivateEndpointSummary
from .database_tools_related_resource import DatabaseToolsRelatedResource
from .database_tools_related_resource_my_sql import DatabaseToolsRelatedResourceMySql
from .database_tools_user_password import DatabaseToolsUserPassword
from .database_tools_user_password_details import DatabaseToolsUserPasswordDetails
from .database_tools_user_password_secret_id import DatabaseToolsUserPasswordSecretId
from .database_tools_user_password_secret_id_details import DatabaseToolsUserPasswordSecretIdDetails
from .database_tools_user_password_secret_id_summary import DatabaseToolsUserPasswordSecretIdSummary
from .database_tools_user_password_summary import DatabaseToolsUserPasswordSummary
from .update_database_tools_connection_details import UpdateDatabaseToolsConnectionDetails
from .update_database_tools_connection_my_sql_details import UpdateDatabaseToolsConnectionMySqlDetails
from .update_database_tools_connection_oracle_database_details import UpdateDatabaseToolsConnectionOracleDatabaseDetails
from .update_database_tools_private_endpoint_details import UpdateDatabaseToolsPrivateEndpointDetails
from .update_database_tools_related_resource_details import UpdateDatabaseToolsRelatedResourceDetails
from .update_database_tools_related_resource_my_sql_details import UpdateDatabaseToolsRelatedResourceMySqlDetails
from .validate_database_tools_connection_details import ValidateDatabaseToolsConnectionDetails
from .validate_database_tools_connection_my_sql_details import ValidateDatabaseToolsConnectionMySqlDetails
from .validate_database_tools_connection_my_sql_result import ValidateDatabaseToolsConnectionMySqlResult
from .validate_database_tools_connection_oracle_database_details import ValidateDatabaseToolsConnectionOracleDatabaseDetails
from .validate_database_tools_connection_oracle_database_result import ValidateDatabaseToolsConnectionOracleDatabaseResult
from .validate_database_tools_connection_result import ValidateDatabaseToolsConnectionResult
from .work_request import WorkRequest
from .work_request_collection import WorkRequestCollection
from .work_request_error import WorkRequestError
from .work_request_error_collection import WorkRequestErrorCollection
from .work_request_log_entry import WorkRequestLogEntry
from .work_request_log_entry_collection import WorkRequestLogEntryCollection
from .work_request_resource import WorkRequestResource
from .work_request_summary import WorkRequestSummary

# Maps type names to classes for database_tools services.
database_tools_type_mapping = {
    "ChangeDatabaseToolsConnectionCompartmentDetails": ChangeDatabaseToolsConnectionCompartmentDetails,
    "ChangeDatabaseToolsPrivateEndpointCompartmentDetails": ChangeDatabaseToolsPrivateEndpointCompartmentDetails,
    "CreateDatabaseToolsConnectionDetails": CreateDatabaseToolsConnectionDetails,
    "CreateDatabaseToolsConnectionMySqlDetails": CreateDatabaseToolsConnectionMySqlDetails,
    "CreateDatabaseToolsConnectionOracleDatabaseDetails": CreateDatabaseToolsConnectionOracleDatabaseDetails,
    "CreateDatabaseToolsPrivateEndpointDetails": CreateDatabaseToolsPrivateEndpointDetails,
    "CreateDatabaseToolsRelatedResourceDetails": CreateDatabaseToolsRelatedResourceDetails,
    "CreateDatabaseToolsRelatedResourceMySqlDetails": CreateDatabaseToolsRelatedResourceMySqlDetails,
    "DatabaseToolsConnection": DatabaseToolsConnection,
    "DatabaseToolsConnectionCollection": DatabaseToolsConnectionCollection,
    "DatabaseToolsConnectionMySql": DatabaseToolsConnectionMySql,
    "DatabaseToolsConnectionMySqlSummary": DatabaseToolsConnectionMySqlSummary,
    "DatabaseToolsConnectionOracleDatabase": DatabaseToolsConnectionOracleDatabase,
    "DatabaseToolsConnectionOracleDatabaseSummary": DatabaseToolsConnectionOracleDatabaseSummary,
    "DatabaseToolsConnectionSummary": DatabaseToolsConnectionSummary,
    "DatabaseToolsEndpointService": DatabaseToolsEndpointService,
    "DatabaseToolsEndpointServiceCollection": DatabaseToolsEndpointServiceCollection,
    "DatabaseToolsEndpointServiceSummary": DatabaseToolsEndpointServiceSummary,
    "DatabaseToolsKeyStore": DatabaseToolsKeyStore,
    "DatabaseToolsKeyStoreContent": DatabaseToolsKeyStoreContent,
    "DatabaseToolsKeyStoreContentDetails": DatabaseToolsKeyStoreContentDetails,
    "DatabaseToolsKeyStoreContentMySql": DatabaseToolsKeyStoreContentMySql,
    "DatabaseToolsKeyStoreContentMySqlDetails": DatabaseToolsKeyStoreContentMySqlDetails,
    "DatabaseToolsKeyStoreContentMySqlSummary": DatabaseToolsKeyStoreContentMySqlSummary,
    "DatabaseToolsKeyStoreContentSecretId": DatabaseToolsKeyStoreContentSecretId,
    "DatabaseToolsKeyStoreContentSecretIdDetails": DatabaseToolsKeyStoreContentSecretIdDetails,
    "DatabaseToolsKeyStoreContentSecretIdMySql": DatabaseToolsKeyStoreContentSecretIdMySql,
    "DatabaseToolsKeyStoreContentSecretIdMySqlDetails": DatabaseToolsKeyStoreContentSecretIdMySqlDetails,
    "DatabaseToolsKeyStoreContentSecretIdMySqlSummary": DatabaseToolsKeyStoreContentSecretIdMySqlSummary,
    "DatabaseToolsKeyStoreContentSecretIdSummary": DatabaseToolsKeyStoreContentSecretIdSummary,
    "DatabaseToolsKeyStoreContentSummary": DatabaseToolsKeyStoreContentSummary,
    "DatabaseToolsKeyStoreDetails": DatabaseToolsKeyStoreDetails,
    "DatabaseToolsKeyStoreMySql": DatabaseToolsKeyStoreMySql,
    "DatabaseToolsKeyStoreMySqlDetails": DatabaseToolsKeyStoreMySqlDetails,
    "DatabaseToolsKeyStoreMySqlSummary": DatabaseToolsKeyStoreMySqlSummary,
    "DatabaseToolsKeyStorePassword": DatabaseToolsKeyStorePassword,
    "DatabaseToolsKeyStorePasswordDetails": DatabaseToolsKeyStorePasswordDetails,
    "DatabaseToolsKeyStorePasswordMySql": DatabaseToolsKeyStorePasswordMySql,
    "DatabaseToolsKeyStorePasswordMySqlDetails": DatabaseToolsKeyStorePasswordMySqlDetails,
    "DatabaseToolsKeyStorePasswordMySqlSummary": DatabaseToolsKeyStorePasswordMySqlSummary,
    "DatabaseToolsKeyStorePasswordSecretId": DatabaseToolsKeyStorePasswordSecretId,
    "DatabaseToolsKeyStorePasswordSecretIdDetails": DatabaseToolsKeyStorePasswordSecretIdDetails,
    "DatabaseToolsKeyStorePasswordSecretIdMySql": DatabaseToolsKeyStorePasswordSecretIdMySql,
    "DatabaseToolsKeyStorePasswordSecretIdMySqlDetails": DatabaseToolsKeyStorePasswordSecretIdMySqlDetails,
    "DatabaseToolsKeyStorePasswordSecretIdMySqlSummary": DatabaseToolsKeyStorePasswordSecretIdMySqlSummary,
    "DatabaseToolsKeyStorePasswordSecretIdSummary": DatabaseToolsKeyStorePasswordSecretIdSummary,
    "DatabaseToolsKeyStorePasswordSummary": DatabaseToolsKeyStorePasswordSummary,
    "DatabaseToolsKeyStoreSummary": DatabaseToolsKeyStoreSummary,
    "DatabaseToolsPrivateEndpoint": DatabaseToolsPrivateEndpoint,
    "DatabaseToolsPrivateEndpointCollection": DatabaseToolsPrivateEndpointCollection,
    "DatabaseToolsPrivateEndpointReverseConnectionConfiguration": DatabaseToolsPrivateEndpointReverseConnectionConfiguration,
    "DatabaseToolsPrivateEndpointReverseConnectionsSourceIp": DatabaseToolsPrivateEndpointReverseConnectionsSourceIp,
    "DatabaseToolsPrivateEndpointSummary": DatabaseToolsPrivateEndpointSummary,
    "DatabaseToolsRelatedResource": DatabaseToolsRelatedResource,
    "DatabaseToolsRelatedResourceMySql": DatabaseToolsRelatedResourceMySql,
    "DatabaseToolsUserPassword": DatabaseToolsUserPassword,
    "DatabaseToolsUserPasswordDetails": DatabaseToolsUserPasswordDetails,
    "DatabaseToolsUserPasswordSecretId": DatabaseToolsUserPasswordSecretId,
    "DatabaseToolsUserPasswordSecretIdDetails": DatabaseToolsUserPasswordSecretIdDetails,
    "DatabaseToolsUserPasswordSecretIdSummary": DatabaseToolsUserPasswordSecretIdSummary,
    "DatabaseToolsUserPasswordSummary": DatabaseToolsUserPasswordSummary,
    "UpdateDatabaseToolsConnectionDetails": UpdateDatabaseToolsConnectionDetails,
    "UpdateDatabaseToolsConnectionMySqlDetails": UpdateDatabaseToolsConnectionMySqlDetails,
    "UpdateDatabaseToolsConnectionOracleDatabaseDetails": UpdateDatabaseToolsConnectionOracleDatabaseDetails,
    "UpdateDatabaseToolsPrivateEndpointDetails": UpdateDatabaseToolsPrivateEndpointDetails,
    "UpdateDatabaseToolsRelatedResourceDetails": UpdateDatabaseToolsRelatedResourceDetails,
    "UpdateDatabaseToolsRelatedResourceMySqlDetails": UpdateDatabaseToolsRelatedResourceMySqlDetails,
    "ValidateDatabaseToolsConnectionDetails": ValidateDatabaseToolsConnectionDetails,
    "ValidateDatabaseToolsConnectionMySqlDetails": ValidateDatabaseToolsConnectionMySqlDetails,
    "ValidateDatabaseToolsConnectionMySqlResult": ValidateDatabaseToolsConnectionMySqlResult,
    "ValidateDatabaseToolsConnectionOracleDatabaseDetails": ValidateDatabaseToolsConnectionOracleDatabaseDetails,
    "ValidateDatabaseToolsConnectionOracleDatabaseResult": ValidateDatabaseToolsConnectionOracleDatabaseResult,
    "ValidateDatabaseToolsConnectionResult": ValidateDatabaseToolsConnectionResult,
    "WorkRequest": WorkRequest,
    "WorkRequestCollection": WorkRequestCollection,
    "WorkRequestError": WorkRequestError,
    "WorkRequestErrorCollection": WorkRequestErrorCollection,
    "WorkRequestLogEntry": WorkRequestLogEntry,
    "WorkRequestLogEntryCollection": WorkRequestLogEntryCollection,
    "WorkRequestResource": WorkRequestResource,
    "WorkRequestSummary": WorkRequestSummary
}
