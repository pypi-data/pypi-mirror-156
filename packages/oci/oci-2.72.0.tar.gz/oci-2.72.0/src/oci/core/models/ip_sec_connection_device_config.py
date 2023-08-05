# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class IPSecConnectionDeviceConfig(object):
    """
    Deprecated. For tunnel information, instead see:

    * :class:`IPSecConnectionTunnel`
    * :class:`IPSecConnectionTunnelSharedSecret`
    """

    def __init__(self, **kwargs):
        """
        Initializes a new IPSecConnectionDeviceConfig object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param compartment_id:
            The value to assign to the compartment_id property of this IPSecConnectionDeviceConfig.
        :type compartment_id: str

        :param id:
            The value to assign to the id property of this IPSecConnectionDeviceConfig.
        :type id: str

        :param time_created:
            The value to assign to the time_created property of this IPSecConnectionDeviceConfig.
        :type time_created: datetime

        :param tunnels:
            The value to assign to the tunnels property of this IPSecConnectionDeviceConfig.
        :type tunnels: list[oci.core.models.TunnelConfig]

        """
        self.swagger_types = {
            'compartment_id': 'str',
            'id': 'str',
            'time_created': 'datetime',
            'tunnels': 'list[TunnelConfig]'
        }

        self.attribute_map = {
            'compartment_id': 'compartmentId',
            'id': 'id',
            'time_created': 'timeCreated',
            'tunnels': 'tunnels'
        }

        self._compartment_id = None
        self._id = None
        self._time_created = None
        self._tunnels = None

    @property
    def compartment_id(self):
        """
        **[Required]** Gets the compartment_id of this IPSecConnectionDeviceConfig.
        The `OCID`__ of the compartment containing the IPSec connection.

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :return: The compartment_id of this IPSecConnectionDeviceConfig.
        :rtype: str
        """
        return self._compartment_id

    @compartment_id.setter
    def compartment_id(self, compartment_id):
        """
        Sets the compartment_id of this IPSecConnectionDeviceConfig.
        The `OCID`__ of the compartment containing the IPSec connection.

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :param compartment_id: The compartment_id of this IPSecConnectionDeviceConfig.
        :type: str
        """
        self._compartment_id = compartment_id

    @property
    def id(self):
        """
        **[Required]** Gets the id of this IPSecConnectionDeviceConfig.
        The IPSec connection's Oracle ID (`OCID`__).

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :return: The id of this IPSecConnectionDeviceConfig.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this IPSecConnectionDeviceConfig.
        The IPSec connection's Oracle ID (`OCID`__).

        __ https://docs.cloud.oracle.com/iaas/Content/General/Concepts/identifiers.htm


        :param id: The id of this IPSecConnectionDeviceConfig.
        :type: str
        """
        self._id = id

    @property
    def time_created(self):
        """
        Gets the time_created of this IPSecConnectionDeviceConfig.
        The date and time the IPSec connection was created.


        :return: The time_created of this IPSecConnectionDeviceConfig.
        :rtype: datetime
        """
        return self._time_created

    @time_created.setter
    def time_created(self, time_created):
        """
        Sets the time_created of this IPSecConnectionDeviceConfig.
        The date and time the IPSec connection was created.


        :param time_created: The time_created of this IPSecConnectionDeviceConfig.
        :type: datetime
        """
        self._time_created = time_created

    @property
    def tunnels(self):
        """
        Gets the tunnels of this IPSecConnectionDeviceConfig.
        Two :class:`TunnelConfig` objects.


        :return: The tunnels of this IPSecConnectionDeviceConfig.
        :rtype: list[oci.core.models.TunnelConfig]
        """
        return self._tunnels

    @tunnels.setter
    def tunnels(self, tunnels):
        """
        Sets the tunnels of this IPSecConnectionDeviceConfig.
        Two :class:`TunnelConfig` objects.


        :param tunnels: The tunnels of this IPSecConnectionDeviceConfig.
        :type: list[oci.core.models.TunnelConfig]
        """
        self._tunnels = tunnels

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
