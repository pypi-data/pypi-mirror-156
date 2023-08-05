# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

from __future__ import absolute_import

from .attached_view import AttachedView
from .attached_view_details import AttachedViewDetails
from .change_resolver_compartment_details import ChangeResolverCompartmentDetails
from .change_steering_policy_compartment_details import ChangeSteeringPolicyCompartmentDetails
from .change_tsig_key_compartment_details import ChangeTsigKeyCompartmentDetails
from .change_view_compartment_details import ChangeViewCompartmentDetails
from .change_zone_compartment_details import ChangeZoneCompartmentDetails
from .create_migrated_dynect_zone_details import CreateMigratedDynectZoneDetails
from .create_resolver_endpoint_details import CreateResolverEndpointDetails
from .create_resolver_vnic_endpoint_details import CreateResolverVnicEndpointDetails
from .create_steering_policy_attachment_details import CreateSteeringPolicyAttachmentDetails
from .create_steering_policy_details import CreateSteeringPolicyDetails
from .create_tsig_key_details import CreateTsigKeyDetails
from .create_view_details import CreateViewDetails
from .create_zone_base_details import CreateZoneBaseDetails
from .create_zone_details import CreateZoneDetails
from .dynect_migration_details import DynectMigrationDetails
from .external_master import ExternalMaster
from .migration_replacement import MigrationReplacement
from .nameserver import Nameserver
from .patch_domain_records_details import PatchDomainRecordsDetails
from .patch_rr_set_details import PatchRRSetDetails
from .patch_zone_records_details import PatchZoneRecordsDetails
from .rr_set import RRSet
from .record import Record
from .record_collection import RecordCollection
from .record_details import RecordDetails
from .record_operation import RecordOperation
from .resolver import Resolver
from .resolver_endpoint import ResolverEndpoint
from .resolver_endpoint_summary import ResolverEndpointSummary
from .resolver_forward_rule import ResolverForwardRule
from .resolver_forward_rule_details import ResolverForwardRuleDetails
from .resolver_rule import ResolverRule
from .resolver_rule_details import ResolverRuleDetails
from .resolver_summary import ResolverSummary
from .resolver_vnic_endpoint import ResolverVnicEndpoint
from .resolver_vnic_endpoint_summary import ResolverVnicEndpointSummary
from .steering_policy import SteeringPolicy
from .steering_policy_answer import SteeringPolicyAnswer
from .steering_policy_attachment import SteeringPolicyAttachment
from .steering_policy_attachment_summary import SteeringPolicyAttachmentSummary
from .steering_policy_filter_answer_data import SteeringPolicyFilterAnswerData
from .steering_policy_filter_rule import SteeringPolicyFilterRule
from .steering_policy_filter_rule_case import SteeringPolicyFilterRuleCase
from .steering_policy_health_rule import SteeringPolicyHealthRule
from .steering_policy_health_rule_case import SteeringPolicyHealthRuleCase
from .steering_policy_limit_rule import SteeringPolicyLimitRule
from .steering_policy_limit_rule_case import SteeringPolicyLimitRuleCase
from .steering_policy_priority_answer_data import SteeringPolicyPriorityAnswerData
from .steering_policy_priority_rule import SteeringPolicyPriorityRule
from .steering_policy_priority_rule_case import SteeringPolicyPriorityRuleCase
from .steering_policy_rule import SteeringPolicyRule
from .steering_policy_summary import SteeringPolicySummary
from .steering_policy_weighted_answer_data import SteeringPolicyWeightedAnswerData
from .steering_policy_weighted_rule import SteeringPolicyWeightedRule
from .steering_policy_weighted_rule_case import SteeringPolicyWeightedRuleCase
from .tsig_key import TsigKey
from .tsig_key_summary import TsigKeySummary
from .update_domain_records_details import UpdateDomainRecordsDetails
from .update_rr_set_details import UpdateRRSetDetails
from .update_resolver_details import UpdateResolverDetails
from .update_resolver_endpoint_details import UpdateResolverEndpointDetails
from .update_resolver_vnic_endpoint_details import UpdateResolverVnicEndpointDetails
from .update_steering_policy_attachment_details import UpdateSteeringPolicyAttachmentDetails
from .update_steering_policy_details import UpdateSteeringPolicyDetails
from .update_tsig_key_details import UpdateTsigKeyDetails
from .update_view_details import UpdateViewDetails
from .update_zone_details import UpdateZoneDetails
from .update_zone_records_details import UpdateZoneRecordsDetails
from .view import View
from .view_summary import ViewSummary
from .zone import Zone
from .zone_summary import ZoneSummary
from .zone_transfer_server import ZoneTransferServer

# Maps type names to classes for dns services.
dns_type_mapping = {
    "AttachedView": AttachedView,
    "AttachedViewDetails": AttachedViewDetails,
    "ChangeResolverCompartmentDetails": ChangeResolverCompartmentDetails,
    "ChangeSteeringPolicyCompartmentDetails": ChangeSteeringPolicyCompartmentDetails,
    "ChangeTsigKeyCompartmentDetails": ChangeTsigKeyCompartmentDetails,
    "ChangeViewCompartmentDetails": ChangeViewCompartmentDetails,
    "ChangeZoneCompartmentDetails": ChangeZoneCompartmentDetails,
    "CreateMigratedDynectZoneDetails": CreateMigratedDynectZoneDetails,
    "CreateResolverEndpointDetails": CreateResolverEndpointDetails,
    "CreateResolverVnicEndpointDetails": CreateResolverVnicEndpointDetails,
    "CreateSteeringPolicyAttachmentDetails": CreateSteeringPolicyAttachmentDetails,
    "CreateSteeringPolicyDetails": CreateSteeringPolicyDetails,
    "CreateTsigKeyDetails": CreateTsigKeyDetails,
    "CreateViewDetails": CreateViewDetails,
    "CreateZoneBaseDetails": CreateZoneBaseDetails,
    "CreateZoneDetails": CreateZoneDetails,
    "DynectMigrationDetails": DynectMigrationDetails,
    "ExternalMaster": ExternalMaster,
    "MigrationReplacement": MigrationReplacement,
    "Nameserver": Nameserver,
    "PatchDomainRecordsDetails": PatchDomainRecordsDetails,
    "PatchRRSetDetails": PatchRRSetDetails,
    "PatchZoneRecordsDetails": PatchZoneRecordsDetails,
    "RRSet": RRSet,
    "Record": Record,
    "RecordCollection": RecordCollection,
    "RecordDetails": RecordDetails,
    "RecordOperation": RecordOperation,
    "Resolver": Resolver,
    "ResolverEndpoint": ResolverEndpoint,
    "ResolverEndpointSummary": ResolverEndpointSummary,
    "ResolverForwardRule": ResolverForwardRule,
    "ResolverForwardRuleDetails": ResolverForwardRuleDetails,
    "ResolverRule": ResolverRule,
    "ResolverRuleDetails": ResolverRuleDetails,
    "ResolverSummary": ResolverSummary,
    "ResolverVnicEndpoint": ResolverVnicEndpoint,
    "ResolverVnicEndpointSummary": ResolverVnicEndpointSummary,
    "SteeringPolicy": SteeringPolicy,
    "SteeringPolicyAnswer": SteeringPolicyAnswer,
    "SteeringPolicyAttachment": SteeringPolicyAttachment,
    "SteeringPolicyAttachmentSummary": SteeringPolicyAttachmentSummary,
    "SteeringPolicyFilterAnswerData": SteeringPolicyFilterAnswerData,
    "SteeringPolicyFilterRule": SteeringPolicyFilterRule,
    "SteeringPolicyFilterRuleCase": SteeringPolicyFilterRuleCase,
    "SteeringPolicyHealthRule": SteeringPolicyHealthRule,
    "SteeringPolicyHealthRuleCase": SteeringPolicyHealthRuleCase,
    "SteeringPolicyLimitRule": SteeringPolicyLimitRule,
    "SteeringPolicyLimitRuleCase": SteeringPolicyLimitRuleCase,
    "SteeringPolicyPriorityAnswerData": SteeringPolicyPriorityAnswerData,
    "SteeringPolicyPriorityRule": SteeringPolicyPriorityRule,
    "SteeringPolicyPriorityRuleCase": SteeringPolicyPriorityRuleCase,
    "SteeringPolicyRule": SteeringPolicyRule,
    "SteeringPolicySummary": SteeringPolicySummary,
    "SteeringPolicyWeightedAnswerData": SteeringPolicyWeightedAnswerData,
    "SteeringPolicyWeightedRule": SteeringPolicyWeightedRule,
    "SteeringPolicyWeightedRuleCase": SteeringPolicyWeightedRuleCase,
    "TsigKey": TsigKey,
    "TsigKeySummary": TsigKeySummary,
    "UpdateDomainRecordsDetails": UpdateDomainRecordsDetails,
    "UpdateRRSetDetails": UpdateRRSetDetails,
    "UpdateResolverDetails": UpdateResolverDetails,
    "UpdateResolverEndpointDetails": UpdateResolverEndpointDetails,
    "UpdateResolverVnicEndpointDetails": UpdateResolverVnicEndpointDetails,
    "UpdateSteeringPolicyAttachmentDetails": UpdateSteeringPolicyAttachmentDetails,
    "UpdateSteeringPolicyDetails": UpdateSteeringPolicyDetails,
    "UpdateTsigKeyDetails": UpdateTsigKeyDetails,
    "UpdateViewDetails": UpdateViewDetails,
    "UpdateZoneDetails": UpdateZoneDetails,
    "UpdateZoneRecordsDetails": UpdateZoneRecordsDetails,
    "View": View,
    "ViewSummary": ViewSummary,
    "Zone": Zone,
    "ZoneSummary": ZoneSummary,
    "ZoneTransferServer": ZoneTransferServer
}
