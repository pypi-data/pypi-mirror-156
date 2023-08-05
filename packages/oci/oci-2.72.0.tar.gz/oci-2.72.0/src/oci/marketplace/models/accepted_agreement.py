# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class AcceptedAgreement(object):
    """
    The model for an accepted terms of use agreement.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new AcceptedAgreement object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param id:
            The value to assign to the id property of this AcceptedAgreement.
        :type id: str

        :param display_name:
            The value to assign to the display_name property of this AcceptedAgreement.
        :type display_name: str

        :param compartment_id:
            The value to assign to the compartment_id property of this AcceptedAgreement.
        :type compartment_id: str

        :param listing_id:
            The value to assign to the listing_id property of this AcceptedAgreement.
        :type listing_id: str

        :param package_version:
            The value to assign to the package_version property of this AcceptedAgreement.
        :type package_version: str

        :param agreement_id:
            The value to assign to the agreement_id property of this AcceptedAgreement.
        :type agreement_id: str

        :param time_accepted:
            The value to assign to the time_accepted property of this AcceptedAgreement.
        :type time_accepted: datetime

        :param defined_tags:
            The value to assign to the defined_tags property of this AcceptedAgreement.
        :type defined_tags: dict(str, dict(str, object))

        :param freeform_tags:
            The value to assign to the freeform_tags property of this AcceptedAgreement.
        :type freeform_tags: dict(str, str)

        """
        self.swagger_types = {
            'id': 'str',
            'display_name': 'str',
            'compartment_id': 'str',
            'listing_id': 'str',
            'package_version': 'str',
            'agreement_id': 'str',
            'time_accepted': 'datetime',
            'defined_tags': 'dict(str, dict(str, object))',
            'freeform_tags': 'dict(str, str)'
        }

        self.attribute_map = {
            'id': 'id',
            'display_name': 'displayName',
            'compartment_id': 'compartmentId',
            'listing_id': 'listingId',
            'package_version': 'packageVersion',
            'agreement_id': 'agreementId',
            'time_accepted': 'timeAccepted',
            'defined_tags': 'definedTags',
            'freeform_tags': 'freeformTags'
        }

        self._id = None
        self._display_name = None
        self._compartment_id = None
        self._listing_id = None
        self._package_version = None
        self._agreement_id = None
        self._time_accepted = None
        self._defined_tags = None
        self._freeform_tags = None

    @property
    def id(self):
        """
        Gets the id of this AcceptedAgreement.
        The unique identifier for the acceptance of the agreement within a specific compartment.


        :return: The id of this AcceptedAgreement.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this AcceptedAgreement.
        The unique identifier for the acceptance of the agreement within a specific compartment.


        :param id: The id of this AcceptedAgreement.
        :type: str
        """
        self._id = id

    @property
    def display_name(self):
        """
        Gets the display_name of this AcceptedAgreement.
        A display name for the accepted agreement.


        :return: The display_name of this AcceptedAgreement.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """
        Sets the display_name of this AcceptedAgreement.
        A display name for the accepted agreement.


        :param display_name: The display_name of this AcceptedAgreement.
        :type: str
        """
        self._display_name = display_name

    @property
    def compartment_id(self):
        """
        Gets the compartment_id of this AcceptedAgreement.
        The unique identifier for the compartment where the agreement was accepted.


        :return: The compartment_id of this AcceptedAgreement.
        :rtype: str
        """
        return self._compartment_id

    @compartment_id.setter
    def compartment_id(self, compartment_id):
        """
        Sets the compartment_id of this AcceptedAgreement.
        The unique identifier for the compartment where the agreement was accepted.


        :param compartment_id: The compartment_id of this AcceptedAgreement.
        :type: str
        """
        self._compartment_id = compartment_id

    @property
    def listing_id(self):
        """
        Gets the listing_id of this AcceptedAgreement.
        The unique identifier for the listing associated with the agreement.


        :return: The listing_id of this AcceptedAgreement.
        :rtype: str
        """
        return self._listing_id

    @listing_id.setter
    def listing_id(self, listing_id):
        """
        Sets the listing_id of this AcceptedAgreement.
        The unique identifier for the listing associated with the agreement.


        :param listing_id: The listing_id of this AcceptedAgreement.
        :type: str
        """
        self._listing_id = listing_id

    @property
    def package_version(self):
        """
        Gets the package_version of this AcceptedAgreement.
        The package version associated with the agreement.


        :return: The package_version of this AcceptedAgreement.
        :rtype: str
        """
        return self._package_version

    @package_version.setter
    def package_version(self, package_version):
        """
        Sets the package_version of this AcceptedAgreement.
        The package version associated with the agreement.


        :param package_version: The package_version of this AcceptedAgreement.
        :type: str
        """
        self._package_version = package_version

    @property
    def agreement_id(self):
        """
        Gets the agreement_id of this AcceptedAgreement.
        The unique identifier for the terms of use agreement itself.


        :return: The agreement_id of this AcceptedAgreement.
        :rtype: str
        """
        return self._agreement_id

    @agreement_id.setter
    def agreement_id(self, agreement_id):
        """
        Sets the agreement_id of this AcceptedAgreement.
        The unique identifier for the terms of use agreement itself.


        :param agreement_id: The agreement_id of this AcceptedAgreement.
        :type: str
        """
        self._agreement_id = agreement_id

    @property
    def time_accepted(self):
        """
        Gets the time_accepted of this AcceptedAgreement.
        The time the agreement was accepted.


        :return: The time_accepted of this AcceptedAgreement.
        :rtype: datetime
        """
        return self._time_accepted

    @time_accepted.setter
    def time_accepted(self, time_accepted):
        """
        Sets the time_accepted of this AcceptedAgreement.
        The time the agreement was accepted.


        :param time_accepted: The time_accepted of this AcceptedAgreement.
        :type: datetime
        """
        self._time_accepted = time_accepted

    @property
    def defined_tags(self):
        """
        Gets the defined_tags of this AcceptedAgreement.
        The defined tags associated with this resource, if any. Each key is predefined and scoped to namespaces.
        For more information, see `Resource Tags`__.
        Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :return: The defined_tags of this AcceptedAgreement.
        :rtype: dict(str, dict(str, object))
        """
        return self._defined_tags

    @defined_tags.setter
    def defined_tags(self, defined_tags):
        """
        Sets the defined_tags of this AcceptedAgreement.
        The defined tags associated with this resource, if any. Each key is predefined and scoped to namespaces.
        For more information, see `Resource Tags`__.
        Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :param defined_tags: The defined_tags of this AcceptedAgreement.
        :type: dict(str, dict(str, object))
        """
        self._defined_tags = defined_tags

    @property
    def freeform_tags(self):
        """
        Gets the freeform_tags of this AcceptedAgreement.
        The freeform tags associated with this resource, if any. Each tag is a simple key-value pair with no
        predefined name, type, or namespace. For more information, see `Resource Tags`__.
        Example: `{\"Department\": \"Finance\"}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :return: The freeform_tags of this AcceptedAgreement.
        :rtype: dict(str, str)
        """
        return self._freeform_tags

    @freeform_tags.setter
    def freeform_tags(self, freeform_tags):
        """
        Sets the freeform_tags of this AcceptedAgreement.
        The freeform tags associated with this resource, if any. Each tag is a simple key-value pair with no
        predefined name, type, or namespace. For more information, see `Resource Tags`__.
        Example: `{\"Department\": \"Finance\"}`

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/resourcetags.htm


        :param freeform_tags: The freeform_tags of this AcceptedAgreement.
        :type: dict(str, str)
        """
        self._freeform_tags = freeform_tags

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
