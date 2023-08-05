# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

from .create_channel_result import CreateChannelResult
from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class CreateWebhookChannelResult(CreateChannelResult):
    """
    The configuration for a Webhook channel.
    """

    #: A constant which can be used with the payload_version property of a CreateWebhookChannelResult.
    #: This constant has a value of "1.0"
    PAYLOAD_VERSION_1_0 = "1.0"

    #: A constant which can be used with the payload_version property of a CreateWebhookChannelResult.
    #: This constant has a value of "1.1"
    PAYLOAD_VERSION_1_1 = "1.1"

    def __init__(self, **kwargs):
        """
        Initializes a new CreateWebhookChannelResult object with values from keyword arguments. The default value of the :py:attr:`~oci.oda.models.CreateWebhookChannelResult.type` attribute
        of this class is ``WEBHOOK`` and it should not be changed.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param id:
            The value to assign to the id property of this CreateWebhookChannelResult.
        :type id: str

        :param name:
            The value to assign to the name property of this CreateWebhookChannelResult.
        :type name: str

        :param description:
            The value to assign to the description property of this CreateWebhookChannelResult.
        :type description: str

        :param category:
            The value to assign to the category property of this CreateWebhookChannelResult.
            Allowed values for this property are: "AGENT", "APPLICATION", "BOT", "BOT_AS_AGENT", "SYSTEM", "EVENT", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type category: str

        :param type:
            The value to assign to the type property of this CreateWebhookChannelResult.
            Allowed values for this property are: "ANDROID", "APPEVENT", "APPLICATION", "CORTANA", "FACEBOOK", "IOS", "MSTEAMS", "OSS", "OSVC", "SERVICECLOUD", "SLACK", "TEST", "TWILIO", "WEB", "WEBHOOK", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type type: str

        :param session_expiry_duration_in_milliseconds:
            The value to assign to the session_expiry_duration_in_milliseconds property of this CreateWebhookChannelResult.
        :type session_expiry_duration_in_milliseconds: int

        :param lifecycle_state:
            The value to assign to the lifecycle_state property of this CreateWebhookChannelResult.
            Allowed values for this property are: "CREATING", "UPDATING", "ACTIVE", "INACTIVE", "DELETING", "DELETED", "FAILED", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type lifecycle_state: str

        :param time_created:
            The value to assign to the time_created property of this CreateWebhookChannelResult.
        :type time_created: datetime

        :param time_updated:
            The value to assign to the time_updated property of this CreateWebhookChannelResult.
        :type time_updated: datetime

        :param freeform_tags:
            The value to assign to the freeform_tags property of this CreateWebhookChannelResult.
        :type freeform_tags: dict(str, str)

        :param defined_tags:
            The value to assign to the defined_tags property of this CreateWebhookChannelResult.
        :type defined_tags: dict(str, dict(str, object))

        :param secret_key:
            The value to assign to the secret_key property of this CreateWebhookChannelResult.
        :type secret_key: str

        :param outbound_url:
            The value to assign to the outbound_url property of this CreateWebhookChannelResult.
        :type outbound_url: str

        :param payload_version:
            The value to assign to the payload_version property of this CreateWebhookChannelResult.
            Allowed values for this property are: "1.0", "1.1", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type payload_version: str

        :param bot_id:
            The value to assign to the bot_id property of this CreateWebhookChannelResult.
        :type bot_id: str

        :param webhook_url:
            The value to assign to the webhook_url property of this CreateWebhookChannelResult.
        :type webhook_url: str

        """
        self.swagger_types = {
            'id': 'str',
            'name': 'str',
            'description': 'str',
            'category': 'str',
            'type': 'str',
            'session_expiry_duration_in_milliseconds': 'int',
            'lifecycle_state': 'str',
            'time_created': 'datetime',
            'time_updated': 'datetime',
            'freeform_tags': 'dict(str, str)',
            'defined_tags': 'dict(str, dict(str, object))',
            'secret_key': 'str',
            'outbound_url': 'str',
            'payload_version': 'str',
            'bot_id': 'str',
            'webhook_url': 'str'
        }

        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'description': 'description',
            'category': 'category',
            'type': 'type',
            'session_expiry_duration_in_milliseconds': 'sessionExpiryDurationInMilliseconds',
            'lifecycle_state': 'lifecycleState',
            'time_created': 'timeCreated',
            'time_updated': 'timeUpdated',
            'freeform_tags': 'freeformTags',
            'defined_tags': 'definedTags',
            'secret_key': 'secretKey',
            'outbound_url': 'outboundUrl',
            'payload_version': 'payloadVersion',
            'bot_id': 'botId',
            'webhook_url': 'webhookUrl'
        }

        self._id = None
        self._name = None
        self._description = None
        self._category = None
        self._type = None
        self._session_expiry_duration_in_milliseconds = None
        self._lifecycle_state = None
        self._time_created = None
        self._time_updated = None
        self._freeform_tags = None
        self._defined_tags = None
        self._secret_key = None
        self._outbound_url = None
        self._payload_version = None
        self._bot_id = None
        self._webhook_url = None
        self._type = 'WEBHOOK'

    @property
    def secret_key(self):
        """
        **[Required]** Gets the secret_key of this CreateWebhookChannelResult.
        The secret key used to verify the authenticity of received messages.
        This is only returned this once.  If it is lost the keys will need to be rotated to generate a new key.


        :return: The secret_key of this CreateWebhookChannelResult.
        :rtype: str
        """
        return self._secret_key

    @secret_key.setter
    def secret_key(self, secret_key):
        """
        Sets the secret_key of this CreateWebhookChannelResult.
        The secret key used to verify the authenticity of received messages.
        This is only returned this once.  If it is lost the keys will need to be rotated to generate a new key.


        :param secret_key: The secret_key of this CreateWebhookChannelResult.
        :type: str
        """
        self._secret_key = secret_key

    @property
    def outbound_url(self):
        """
        **[Required]** Gets the outbound_url of this CreateWebhookChannelResult.
        The URL to send responses to.


        :return: The outbound_url of this CreateWebhookChannelResult.
        :rtype: str
        """
        return self._outbound_url

    @outbound_url.setter
    def outbound_url(self, outbound_url):
        """
        Sets the outbound_url of this CreateWebhookChannelResult.
        The URL to send responses to.


        :param outbound_url: The outbound_url of this CreateWebhookChannelResult.
        :type: str
        """
        self._outbound_url = outbound_url

    @property
    def payload_version(self):
        """
        **[Required]** Gets the payload_version of this CreateWebhookChannelResult.
        The version for payloads.

        Allowed values for this property are: "1.0", "1.1", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The payload_version of this CreateWebhookChannelResult.
        :rtype: str
        """
        return self._payload_version

    @payload_version.setter
    def payload_version(self, payload_version):
        """
        Sets the payload_version of this CreateWebhookChannelResult.
        The version for payloads.


        :param payload_version: The payload_version of this CreateWebhookChannelResult.
        :type: str
        """
        allowed_values = ["1.0", "1.1"]
        if not value_allowed_none_or_none_sentinel(payload_version, allowed_values):
            payload_version = 'UNKNOWN_ENUM_VALUE'
        self._payload_version = payload_version

    @property
    def bot_id(self):
        """
        Gets the bot_id of this CreateWebhookChannelResult.
        The ID of the Skill or Digital Assistant that the Channel is routed to.


        :return: The bot_id of this CreateWebhookChannelResult.
        :rtype: str
        """
        return self._bot_id

    @bot_id.setter
    def bot_id(self, bot_id):
        """
        Sets the bot_id of this CreateWebhookChannelResult.
        The ID of the Skill or Digital Assistant that the Channel is routed to.


        :param bot_id: The bot_id of this CreateWebhookChannelResult.
        :type: str
        """
        self._bot_id = bot_id

    @property
    def webhook_url(self):
        """
        **[Required]** Gets the webhook_url of this CreateWebhookChannelResult.
        The URL to use to send messages to this channel.
        This will be generally be used to configure a webhook in a 3rd party messaging system to send messages to this channel.


        :return: The webhook_url of this CreateWebhookChannelResult.
        :rtype: str
        """
        return self._webhook_url

    @webhook_url.setter
    def webhook_url(self, webhook_url):
        """
        Sets the webhook_url of this CreateWebhookChannelResult.
        The URL to use to send messages to this channel.
        This will be generally be used to configure a webhook in a 3rd party messaging system to send messages to this channel.


        :param webhook_url: The webhook_url of this CreateWebhookChannelResult.
        :type: str
        """
        self._webhook_url = webhook_url

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
