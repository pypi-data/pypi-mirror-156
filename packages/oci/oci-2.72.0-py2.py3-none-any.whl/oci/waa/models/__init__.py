# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

from __future__ import absolute_import

from .change_resource_compartment_details import ChangeResourceCompartmentDetails
from .change_web_app_acceleration_compartment_details import ChangeWebAppAccelerationCompartmentDetails
from .change_web_app_acceleration_policy_compartment_details import ChangeWebAppAccelerationPolicyCompartmentDetails
from .create_web_app_acceleration_details import CreateWebAppAccelerationDetails
from .create_web_app_acceleration_load_balancer_details import CreateWebAppAccelerationLoadBalancerDetails
from .create_web_app_acceleration_policy_details import CreateWebAppAccelerationPolicyDetails
from .gzip_compression_policy import GzipCompressionPolicy
from .purge_entire_web_app_acceleration_cache_details import PurgeEntireWebAppAccelerationCacheDetails
from .purge_web_app_acceleration_cache_details import PurgeWebAppAccelerationCacheDetails
from .response_caching_policy import ResponseCachingPolicy
from .response_compression_policy import ResponseCompressionPolicy
from .update_web_app_acceleration_details import UpdateWebAppAccelerationDetails
from .update_web_app_acceleration_policy_details import UpdateWebAppAccelerationPolicyDetails
from .web_app_acceleration import WebAppAcceleration
from .web_app_acceleration_collection import WebAppAccelerationCollection
from .web_app_acceleration_load_balancer import WebAppAccelerationLoadBalancer
from .web_app_acceleration_load_balancer_summary import WebAppAccelerationLoadBalancerSummary
from .web_app_acceleration_policy import WebAppAccelerationPolicy
from .web_app_acceleration_policy_collection import WebAppAccelerationPolicyCollection
from .web_app_acceleration_policy_summary import WebAppAccelerationPolicySummary
from .web_app_acceleration_summary import WebAppAccelerationSummary
from .work_request import WorkRequest
from .work_request_collection import WorkRequestCollection
from .work_request_error import WorkRequestError
from .work_request_error_collection import WorkRequestErrorCollection
from .work_request_log_entry import WorkRequestLogEntry
from .work_request_log_entry_collection import WorkRequestLogEntryCollection
from .work_request_resource import WorkRequestResource

# Maps type names to classes for waa services.
waa_type_mapping = {
    "ChangeResourceCompartmentDetails": ChangeResourceCompartmentDetails,
    "ChangeWebAppAccelerationCompartmentDetails": ChangeWebAppAccelerationCompartmentDetails,
    "ChangeWebAppAccelerationPolicyCompartmentDetails": ChangeWebAppAccelerationPolicyCompartmentDetails,
    "CreateWebAppAccelerationDetails": CreateWebAppAccelerationDetails,
    "CreateWebAppAccelerationLoadBalancerDetails": CreateWebAppAccelerationLoadBalancerDetails,
    "CreateWebAppAccelerationPolicyDetails": CreateWebAppAccelerationPolicyDetails,
    "GzipCompressionPolicy": GzipCompressionPolicy,
    "PurgeEntireWebAppAccelerationCacheDetails": PurgeEntireWebAppAccelerationCacheDetails,
    "PurgeWebAppAccelerationCacheDetails": PurgeWebAppAccelerationCacheDetails,
    "ResponseCachingPolicy": ResponseCachingPolicy,
    "ResponseCompressionPolicy": ResponseCompressionPolicy,
    "UpdateWebAppAccelerationDetails": UpdateWebAppAccelerationDetails,
    "UpdateWebAppAccelerationPolicyDetails": UpdateWebAppAccelerationPolicyDetails,
    "WebAppAcceleration": WebAppAcceleration,
    "WebAppAccelerationCollection": WebAppAccelerationCollection,
    "WebAppAccelerationLoadBalancer": WebAppAccelerationLoadBalancer,
    "WebAppAccelerationLoadBalancerSummary": WebAppAccelerationLoadBalancerSummary,
    "WebAppAccelerationPolicy": WebAppAccelerationPolicy,
    "WebAppAccelerationPolicyCollection": WebAppAccelerationPolicyCollection,
    "WebAppAccelerationPolicySummary": WebAppAccelerationPolicySummary,
    "WebAppAccelerationSummary": WebAppAccelerationSummary,
    "WorkRequest": WorkRequest,
    "WorkRequestCollection": WorkRequestCollection,
    "WorkRequestError": WorkRequestError,
    "WorkRequestErrorCollection": WorkRequestErrorCollection,
    "WorkRequestLogEntry": WorkRequestLogEntry,
    "WorkRequestLogEntryCollection": WorkRequestLogEntryCollection,
    "WorkRequestResource": WorkRequestResource
}
