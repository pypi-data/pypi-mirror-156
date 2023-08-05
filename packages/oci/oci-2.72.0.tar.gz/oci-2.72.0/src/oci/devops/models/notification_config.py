# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class NotificationConfig(object):
    """
    Notification configuration for the project.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new NotificationConfig object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param topic_id:
            The value to assign to the topic_id property of this NotificationConfig.
        :type topic_id: str

        """
        self.swagger_types = {
            'topic_id': 'str'
        }

        self.attribute_map = {
            'topic_id': 'topicId'
        }

        self._topic_id = None

    @property
    def topic_id(self):
        """
        **[Required]** Gets the topic_id of this NotificationConfig.
        The topic ID for notifications.


        :return: The topic_id of this NotificationConfig.
        :rtype: str
        """
        return self._topic_id

    @topic_id.setter
    def topic_id(self, topic_id):
        """
        Sets the topic_id of this NotificationConfig.
        The topic ID for notifications.


        :param topic_id: The topic_id of this NotificationConfig.
        :type: str
        """
        self._topic_id = topic_id

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
