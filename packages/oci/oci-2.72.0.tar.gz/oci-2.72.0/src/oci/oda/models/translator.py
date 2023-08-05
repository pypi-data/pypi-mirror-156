# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class Translator(object):
    """
    The properties for a Translator.
    """

    #: A constant which can be used with the type property of a Translator.
    #: This constant has a value of "GOOGLE"
    TYPE_GOOGLE = "GOOGLE"

    #: A constant which can be used with the type property of a Translator.
    #: This constant has a value of "MICROSOFT"
    TYPE_MICROSOFT = "MICROSOFT"

    #: A constant which can be used with the lifecycle_state property of a Translator.
    #: This constant has a value of "CREATING"
    LIFECYCLE_STATE_CREATING = "CREATING"

    #: A constant which can be used with the lifecycle_state property of a Translator.
    #: This constant has a value of "UPDATING"
    LIFECYCLE_STATE_UPDATING = "UPDATING"

    #: A constant which can be used with the lifecycle_state property of a Translator.
    #: This constant has a value of "ACTIVE"
    LIFECYCLE_STATE_ACTIVE = "ACTIVE"

    #: A constant which can be used with the lifecycle_state property of a Translator.
    #: This constant has a value of "INACTIVE"
    LIFECYCLE_STATE_INACTIVE = "INACTIVE"

    #: A constant which can be used with the lifecycle_state property of a Translator.
    #: This constant has a value of "DELETING"
    LIFECYCLE_STATE_DELETING = "DELETING"

    #: A constant which can be used with the lifecycle_state property of a Translator.
    #: This constant has a value of "DELETED"
    LIFECYCLE_STATE_DELETED = "DELETED"

    #: A constant which can be used with the lifecycle_state property of a Translator.
    #: This constant has a value of "FAILED"
    LIFECYCLE_STATE_FAILED = "FAILED"

    def __init__(self, **kwargs):
        """
        Initializes a new Translator object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param id:
            The value to assign to the id property of this Translator.
        :type id: str

        :param type:
            The value to assign to the type property of this Translator.
            Allowed values for this property are: "GOOGLE", "MICROSOFT", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type type: str

        :param name:
            The value to assign to the name property of this Translator.
        :type name: str

        :param base_url:
            The value to assign to the base_url property of this Translator.
        :type base_url: str

        :param lifecycle_state:
            The value to assign to the lifecycle_state property of this Translator.
            Allowed values for this property are: "CREATING", "UPDATING", "ACTIVE", "INACTIVE", "DELETING", "DELETED", "FAILED", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type lifecycle_state: str

        :param properties:
            The value to assign to the properties property of this Translator.
        :type properties: dict(str, str)

        :param time_created:
            The value to assign to the time_created property of this Translator.
        :type time_created: datetime

        :param time_updated:
            The value to assign to the time_updated property of this Translator.
        :type time_updated: datetime

        :param freeform_tags:
            The value to assign to the freeform_tags property of this Translator.
        :type freeform_tags: dict(str, str)

        :param defined_tags:
            The value to assign to the defined_tags property of this Translator.
        :type defined_tags: dict(str, dict(str, object))

        """
        self.swagger_types = {
            'id': 'str',
            'type': 'str',
            'name': 'str',
            'base_url': 'str',
            'lifecycle_state': 'str',
            'properties': 'dict(str, str)',
            'time_created': 'datetime',
            'time_updated': 'datetime',
            'freeform_tags': 'dict(str, str)',
            'defined_tags': 'dict(str, dict(str, object))'
        }

        self.attribute_map = {
            'id': 'id',
            'type': 'type',
            'name': 'name',
            'base_url': 'baseUrl',
            'lifecycle_state': 'lifecycleState',
            'properties': 'properties',
            'time_created': 'timeCreated',
            'time_updated': 'timeUpdated',
            'freeform_tags': 'freeformTags',
            'defined_tags': 'definedTags'
        }

        self._id = None
        self._type = None
        self._name = None
        self._base_url = None
        self._lifecycle_state = None
        self._properties = None
        self._time_created = None
        self._time_updated = None
        self._freeform_tags = None
        self._defined_tags = None

    @property
    def id(self):
        """
        **[Required]** Gets the id of this Translator.
        Unique immutable identifier that was assigned when the Translator was created.


        :return: The id of this Translator.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this Translator.
        Unique immutable identifier that was assigned when the Translator was created.


        :param id: The id of this Translator.
        :type: str
        """
        self._id = id

    @property
    def type(self):
        """
        **[Required]** Gets the type of this Translator.
        The Translation Service to use for this Translator.

        Allowed values for this property are: "GOOGLE", "MICROSOFT", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The type of this Translator.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """
        Sets the type of this Translator.
        The Translation Service to use for this Translator.


        :param type: The type of this Translator.
        :type: str
        """
        allowed_values = ["GOOGLE", "MICROSOFT"]
        if not value_allowed_none_or_none_sentinel(type, allowed_values):
            type = 'UNKNOWN_ENUM_VALUE'
        self._type = type

    @property
    def name(self):
        """
        **[Required]** Gets the name of this Translator.
        The descriptive name for this Translator.


        :return: The name of this Translator.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this Translator.
        The descriptive name for this Translator.


        :param name: The name of this Translator.
        :type: str
        """
        self._name = name

    @property
    def base_url(self):
        """
        **[Required]** Gets the base_url of this Translator.
        The base URL for invoking the Translation Service.


        :return: The base_url of this Translator.
        :rtype: str
        """
        return self._base_url

    @base_url.setter
    def base_url(self, base_url):
        """
        Sets the base_url of this Translator.
        The base URL for invoking the Translation Service.


        :param base_url: The base_url of this Translator.
        :type: str
        """
        self._base_url = base_url

    @property
    def lifecycle_state(self):
        """
        **[Required]** Gets the lifecycle_state of this Translator.
        The Translator's current state.

        Allowed values for this property are: "CREATING", "UPDATING", "ACTIVE", "INACTIVE", "DELETING", "DELETED", "FAILED", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The lifecycle_state of this Translator.
        :rtype: str
        """
        return self._lifecycle_state

    @lifecycle_state.setter
    def lifecycle_state(self, lifecycle_state):
        """
        Sets the lifecycle_state of this Translator.
        The Translator's current state.


        :param lifecycle_state: The lifecycle_state of this Translator.
        :type: str
        """
        allowed_values = ["CREATING", "UPDATING", "ACTIVE", "INACTIVE", "DELETING", "DELETED", "FAILED"]
        if not value_allowed_none_or_none_sentinel(lifecycle_state, allowed_values):
            lifecycle_state = 'UNKNOWN_ENUM_VALUE'
        self._lifecycle_state = lifecycle_state

    @property
    def properties(self):
        """
        Gets the properties of this Translator.
        Properties used when invoking the translation service.
        Each property is a simple key-value pair.


        :return: The properties of this Translator.
        :rtype: dict(str, str)
        """
        return self._properties

    @properties.setter
    def properties(self, properties):
        """
        Sets the properties of this Translator.
        Properties used when invoking the translation service.
        Each property is a simple key-value pair.


        :param properties: The properties of this Translator.
        :type: dict(str, str)
        """
        self._properties = properties

    @property
    def time_created(self):
        """
        **[Required]** Gets the time_created of this Translator.
        When the resource was created. A date-time string as described in `RFC 3339`__, section 14.29.

        __ https://tools.ietf.org/rfc/rfc3339


        :return: The time_created of this Translator.
        :rtype: datetime
        """
        return self._time_created

    @time_created.setter
    def time_created(self, time_created):
        """
        Sets the time_created of this Translator.
        When the resource was created. A date-time string as described in `RFC 3339`__, section 14.29.

        __ https://tools.ietf.org/rfc/rfc3339


        :param time_created: The time_created of this Translator.
        :type: datetime
        """
        self._time_created = time_created

    @property
    def time_updated(self):
        """
        **[Required]** Gets the time_updated of this Translator.
        When the resource was last updated. A date-time string as described in `RFC 3339`__, section 14.29.

        __ https://tools.ietf.org/rfc/rfc3339


        :return: The time_updated of this Translator.
        :rtype: datetime
        """
        return self._time_updated

    @time_updated.setter
    def time_updated(self, time_updated):
        """
        Sets the time_updated of this Translator.
        When the resource was last updated. A date-time string as described in `RFC 3339`__, section 14.29.

        __ https://tools.ietf.org/rfc/rfc3339


        :param time_updated: The time_updated of this Translator.
        :type: datetime
        """
        self._time_updated = time_updated

    @property
    def freeform_tags(self):
        """
        Gets the freeform_tags of this Translator.
        Simple key-value pair that is applied without any predefined name, type, or scope.
        Example: `{\"bar-key\": \"value\"}`


        :return: The freeform_tags of this Translator.
        :rtype: dict(str, str)
        """
        return self._freeform_tags

    @freeform_tags.setter
    def freeform_tags(self, freeform_tags):
        """
        Sets the freeform_tags of this Translator.
        Simple key-value pair that is applied without any predefined name, type, or scope.
        Example: `{\"bar-key\": \"value\"}`


        :param freeform_tags: The freeform_tags of this Translator.
        :type: dict(str, str)
        """
        self._freeform_tags = freeform_tags

    @property
    def defined_tags(self):
        """
        Gets the defined_tags of this Translator.
        Usage of predefined tag keys. These predefined keys are scoped to namespaces.
        Example: `{\"foo-namespace\": {\"bar-key\": \"value\"}}`


        :return: The defined_tags of this Translator.
        :rtype: dict(str, dict(str, object))
        """
        return self._defined_tags

    @defined_tags.setter
    def defined_tags(self, defined_tags):
        """
        Sets the defined_tags of this Translator.
        Usage of predefined tag keys. These predefined keys are scoped to namespaces.
        Example: `{\"foo-namespace\": {\"bar-key\": \"value\"}}`


        :param defined_tags: The defined_tags of this Translator.
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
