# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class UpdateLicenseRecordDetails(object):
    """
    The details about updates in the license record.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new UpdateLicenseRecordDetails object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param display_name:
            The value to assign to the display_name property of this UpdateLicenseRecordDetails.
        :type display_name: str

        :param is_perpetual:
            The value to assign to the is_perpetual property of this UpdateLicenseRecordDetails.
        :type is_perpetual: bool

        :param expiration_date:
            The value to assign to the expiration_date property of this UpdateLicenseRecordDetails.
        :type expiration_date: datetime

        :param support_end_date:
            The value to assign to the support_end_date property of this UpdateLicenseRecordDetails.
        :type support_end_date: datetime

        :param is_unlimited:
            The value to assign to the is_unlimited property of this UpdateLicenseRecordDetails.
        :type is_unlimited: bool

        :param license_count:
            The value to assign to the license_count property of this UpdateLicenseRecordDetails.
        :type license_count: int

        :param product_id:
            The value to assign to the product_id property of this UpdateLicenseRecordDetails.
        :type product_id: str

        :param freeform_tags:
            The value to assign to the freeform_tags property of this UpdateLicenseRecordDetails.
        :type freeform_tags: dict(str, str)

        :param defined_tags:
            The value to assign to the defined_tags property of this UpdateLicenseRecordDetails.
        :type defined_tags: dict(str, dict(str, object))

        """
        self.swagger_types = {
            'display_name': 'str',
            'is_perpetual': 'bool',
            'expiration_date': 'datetime',
            'support_end_date': 'datetime',
            'is_unlimited': 'bool',
            'license_count': 'int',
            'product_id': 'str',
            'freeform_tags': 'dict(str, str)',
            'defined_tags': 'dict(str, dict(str, object))'
        }

        self.attribute_map = {
            'display_name': 'displayName',
            'is_perpetual': 'isPerpetual',
            'expiration_date': 'expirationDate',
            'support_end_date': 'supportEndDate',
            'is_unlimited': 'isUnlimited',
            'license_count': 'licenseCount',
            'product_id': 'productId',
            'freeform_tags': 'freeformTags',
            'defined_tags': 'definedTags'
        }

        self._display_name = None
        self._is_perpetual = None
        self._expiration_date = None
        self._support_end_date = None
        self._is_unlimited = None
        self._license_count = None
        self._product_id = None
        self._freeform_tags = None
        self._defined_tags = None

    @property
    def display_name(self):
        """
        **[Required]** Gets the display_name of this UpdateLicenseRecordDetails.
        License record name.


        :return: The display_name of this UpdateLicenseRecordDetails.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """
        Sets the display_name of this UpdateLicenseRecordDetails.
        License record name.


        :param display_name: The display_name of this UpdateLicenseRecordDetails.
        :type: str
        """
        self._display_name = display_name

    @property
    def is_perpetual(self):
        """
        **[Required]** Gets the is_perpetual of this UpdateLicenseRecordDetails.
        Specifies if the license record term is perpertual.


        :return: The is_perpetual of this UpdateLicenseRecordDetails.
        :rtype: bool
        """
        return self._is_perpetual

    @is_perpetual.setter
    def is_perpetual(self, is_perpetual):
        """
        Sets the is_perpetual of this UpdateLicenseRecordDetails.
        Specifies if the license record term is perpertual.


        :param is_perpetual: The is_perpetual of this UpdateLicenseRecordDetails.
        :type: bool
        """
        self._is_perpetual = is_perpetual

    @property
    def expiration_date(self):
        """
        Gets the expiration_date of this UpdateLicenseRecordDetails.
        The license record end date in `RFC 3339`__
        date format.
        Example: `2018-09-12`

        __ https://tools.ietf.org/html/rfc3339


        :return: The expiration_date of this UpdateLicenseRecordDetails.
        :rtype: datetime
        """
        return self._expiration_date

    @expiration_date.setter
    def expiration_date(self, expiration_date):
        """
        Sets the expiration_date of this UpdateLicenseRecordDetails.
        The license record end date in `RFC 3339`__
        date format.
        Example: `2018-09-12`

        __ https://tools.ietf.org/html/rfc3339


        :param expiration_date: The expiration_date of this UpdateLicenseRecordDetails.
        :type: datetime
        """
        self._expiration_date = expiration_date

    @property
    def support_end_date(self):
        """
        Gets the support_end_date of this UpdateLicenseRecordDetails.
        The license record support end date in `RFC 3339`__
        date format.
        Example: `2018-09-12`

        __ https://tools.ietf.org/html/rfc3339


        :return: The support_end_date of this UpdateLicenseRecordDetails.
        :rtype: datetime
        """
        return self._support_end_date

    @support_end_date.setter
    def support_end_date(self, support_end_date):
        """
        Sets the support_end_date of this UpdateLicenseRecordDetails.
        The license record support end date in `RFC 3339`__
        date format.
        Example: `2018-09-12`

        __ https://tools.ietf.org/html/rfc3339


        :param support_end_date: The support_end_date of this UpdateLicenseRecordDetails.
        :type: datetime
        """
        self._support_end_date = support_end_date

    @property
    def is_unlimited(self):
        """
        **[Required]** Gets the is_unlimited of this UpdateLicenseRecordDetails.
        Specifies if the license count is unlimited.


        :return: The is_unlimited of this UpdateLicenseRecordDetails.
        :rtype: bool
        """
        return self._is_unlimited

    @is_unlimited.setter
    def is_unlimited(self, is_unlimited):
        """
        Sets the is_unlimited of this UpdateLicenseRecordDetails.
        Specifies if the license count is unlimited.


        :param is_unlimited: The is_unlimited of this UpdateLicenseRecordDetails.
        :type: bool
        """
        self._is_unlimited = is_unlimited

    @property
    def license_count(self):
        """
        Gets the license_count of this UpdateLicenseRecordDetails.
        The number of license units added by a user in a license record.
        Default 1


        :return: The license_count of this UpdateLicenseRecordDetails.
        :rtype: int
        """
        return self._license_count

    @license_count.setter
    def license_count(self, license_count):
        """
        Sets the license_count of this UpdateLicenseRecordDetails.
        The number of license units added by a user in a license record.
        Default 1


        :param license_count: The license_count of this UpdateLicenseRecordDetails.
        :type: int
        """
        self._license_count = license_count

    @property
    def product_id(self):
        """
        Gets the product_id of this UpdateLicenseRecordDetails.
        The license record product ID.


        :return: The product_id of this UpdateLicenseRecordDetails.
        :rtype: str
        """
        return self._product_id

    @product_id.setter
    def product_id(self, product_id):
        """
        Sets the product_id of this UpdateLicenseRecordDetails.
        The license record product ID.


        :param product_id: The product_id of this UpdateLicenseRecordDetails.
        :type: str
        """
        self._product_id = product_id

    @property
    def freeform_tags(self):
        """
        Gets the freeform_tags of this UpdateLicenseRecordDetails.
        Simple key-value pair that is applied without any predefined name, type, or scope. Exists for cross-compatibility only.
        Example: `{\"bar-key\": \"value\"}`


        :return: The freeform_tags of this UpdateLicenseRecordDetails.
        :rtype: dict(str, str)
        """
        return self._freeform_tags

    @freeform_tags.setter
    def freeform_tags(self, freeform_tags):
        """
        Sets the freeform_tags of this UpdateLicenseRecordDetails.
        Simple key-value pair that is applied without any predefined name, type, or scope. Exists for cross-compatibility only.
        Example: `{\"bar-key\": \"value\"}`


        :param freeform_tags: The freeform_tags of this UpdateLicenseRecordDetails.
        :type: dict(str, str)
        """
        self._freeform_tags = freeform_tags

    @property
    def defined_tags(self):
        """
        Gets the defined_tags of this UpdateLicenseRecordDetails.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        Example: `{\"foo-namespace\": {\"bar-key\": \"value\"}}`


        :return: The defined_tags of this UpdateLicenseRecordDetails.
        :rtype: dict(str, dict(str, object))
        """
        return self._defined_tags

    @defined_tags.setter
    def defined_tags(self, defined_tags):
        """
        Sets the defined_tags of this UpdateLicenseRecordDetails.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        Example: `{\"foo-namespace\": {\"bar-key\": \"value\"}}`


        :param defined_tags: The defined_tags of this UpdateLicenseRecordDetails.
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
