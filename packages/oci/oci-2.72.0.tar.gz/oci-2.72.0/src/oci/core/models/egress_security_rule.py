# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class EgressSecurityRule(object):
    """
    A rule for allowing outbound IP packets.
    """

    #: A constant which can be used with the destination_type property of a EgressSecurityRule.
    #: This constant has a value of "CIDR_BLOCK"
    DESTINATION_TYPE_CIDR_BLOCK = "CIDR_BLOCK"

    #: A constant which can be used with the destination_type property of a EgressSecurityRule.
    #: This constant has a value of "SERVICE_CIDR_BLOCK"
    DESTINATION_TYPE_SERVICE_CIDR_BLOCK = "SERVICE_CIDR_BLOCK"

    def __init__(self, **kwargs):
        """
        Initializes a new EgressSecurityRule object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param destination:
            The value to assign to the destination property of this EgressSecurityRule.
        :type destination: str

        :param destination_type:
            The value to assign to the destination_type property of this EgressSecurityRule.
            Allowed values for this property are: "CIDR_BLOCK", "SERVICE_CIDR_BLOCK", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type destination_type: str

        :param icmp_options:
            The value to assign to the icmp_options property of this EgressSecurityRule.
        :type icmp_options: oci.core.models.IcmpOptions

        :param is_stateless:
            The value to assign to the is_stateless property of this EgressSecurityRule.
        :type is_stateless: bool

        :param protocol:
            The value to assign to the protocol property of this EgressSecurityRule.
        :type protocol: str

        :param tcp_options:
            The value to assign to the tcp_options property of this EgressSecurityRule.
        :type tcp_options: oci.core.models.TcpOptions

        :param udp_options:
            The value to assign to the udp_options property of this EgressSecurityRule.
        :type udp_options: oci.core.models.UdpOptions

        :param description:
            The value to assign to the description property of this EgressSecurityRule.
        :type description: str

        """
        self.swagger_types = {
            'destination': 'str',
            'destination_type': 'str',
            'icmp_options': 'IcmpOptions',
            'is_stateless': 'bool',
            'protocol': 'str',
            'tcp_options': 'TcpOptions',
            'udp_options': 'UdpOptions',
            'description': 'str'
        }

        self.attribute_map = {
            'destination': 'destination',
            'destination_type': 'destinationType',
            'icmp_options': 'icmpOptions',
            'is_stateless': 'isStateless',
            'protocol': 'protocol',
            'tcp_options': 'tcpOptions',
            'udp_options': 'udpOptions',
            'description': 'description'
        }

        self._destination = None
        self._destination_type = None
        self._icmp_options = None
        self._is_stateless = None
        self._protocol = None
        self._tcp_options = None
        self._udp_options = None
        self._description = None

    @property
    def destination(self):
        """
        **[Required]** Gets the destination of this EgressSecurityRule.
        Conceptually, this is the range of IP addresses that a packet originating from the instance
        can go to.

        Allowed values:

          * IP address range in CIDR notation. For example: `192.168.1.0/24` or `2001:0db8:0123:45::/56`
            Note that IPv6 addressing is currently supported only in certain regions. See
            `IPv6 Addresses`__.

          * The `cidrBlock` value for a :class:`Service`, if you're
            setting up a security list rule for traffic destined for a particular `Service` through
            a service gateway. For example: `oci-phx-objectstorage`.

        __ https://docs.cloud.oracle.com/iaas/Content/Network/Concepts/ipv6.htm


        :return: The destination of this EgressSecurityRule.
        :rtype: str
        """
        return self._destination

    @destination.setter
    def destination(self, destination):
        """
        Sets the destination of this EgressSecurityRule.
        Conceptually, this is the range of IP addresses that a packet originating from the instance
        can go to.

        Allowed values:

          * IP address range in CIDR notation. For example: `192.168.1.0/24` or `2001:0db8:0123:45::/56`
            Note that IPv6 addressing is currently supported only in certain regions. See
            `IPv6 Addresses`__.

          * The `cidrBlock` value for a :class:`Service`, if you're
            setting up a security list rule for traffic destined for a particular `Service` through
            a service gateway. For example: `oci-phx-objectstorage`.

        __ https://docs.cloud.oracle.com/iaas/Content/Network/Concepts/ipv6.htm


        :param destination: The destination of this EgressSecurityRule.
        :type: str
        """
        self._destination = destination

    @property
    def destination_type(self):
        """
        Gets the destination_type of this EgressSecurityRule.
        Type of destination for the rule. The default is `CIDR_BLOCK`.

        Allowed values:

          * `CIDR_BLOCK`: If the rule's `destination` is an IP address range in CIDR notation.

          * `SERVICE_CIDR_BLOCK`: If the rule's `destination` is the `cidrBlock` value for a
            :class:`Service` (the rule is for traffic destined for a
            particular `Service` through a service gateway).

        Allowed values for this property are: "CIDR_BLOCK", "SERVICE_CIDR_BLOCK", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The destination_type of this EgressSecurityRule.
        :rtype: str
        """
        return self._destination_type

    @destination_type.setter
    def destination_type(self, destination_type):
        """
        Sets the destination_type of this EgressSecurityRule.
        Type of destination for the rule. The default is `CIDR_BLOCK`.

        Allowed values:

          * `CIDR_BLOCK`: If the rule's `destination` is an IP address range in CIDR notation.

          * `SERVICE_CIDR_BLOCK`: If the rule's `destination` is the `cidrBlock` value for a
            :class:`Service` (the rule is for traffic destined for a
            particular `Service` through a service gateway).


        :param destination_type: The destination_type of this EgressSecurityRule.
        :type: str
        """
        allowed_values = ["CIDR_BLOCK", "SERVICE_CIDR_BLOCK"]
        if not value_allowed_none_or_none_sentinel(destination_type, allowed_values):
            destination_type = 'UNKNOWN_ENUM_VALUE'
        self._destination_type = destination_type

    @property
    def icmp_options(self):
        """
        Gets the icmp_options of this EgressSecurityRule.

        :return: The icmp_options of this EgressSecurityRule.
        :rtype: oci.core.models.IcmpOptions
        """
        return self._icmp_options

    @icmp_options.setter
    def icmp_options(self, icmp_options):
        """
        Sets the icmp_options of this EgressSecurityRule.

        :param icmp_options: The icmp_options of this EgressSecurityRule.
        :type: oci.core.models.IcmpOptions
        """
        self._icmp_options = icmp_options

    @property
    def is_stateless(self):
        """
        Gets the is_stateless of this EgressSecurityRule.
        A stateless rule allows traffic in one direction. Remember to add a corresponding
        stateless rule in the other direction if you need to support bidirectional traffic. For
        example, if egress traffic allows TCP destination port 80, there should be an ingress
        rule to allow TCP source port 80. Defaults to false, which means the rule is stateful
        and a corresponding rule is not necessary for bidirectional traffic.


        :return: The is_stateless of this EgressSecurityRule.
        :rtype: bool
        """
        return self._is_stateless

    @is_stateless.setter
    def is_stateless(self, is_stateless):
        """
        Sets the is_stateless of this EgressSecurityRule.
        A stateless rule allows traffic in one direction. Remember to add a corresponding
        stateless rule in the other direction if you need to support bidirectional traffic. For
        example, if egress traffic allows TCP destination port 80, there should be an ingress
        rule to allow TCP source port 80. Defaults to false, which means the rule is stateful
        and a corresponding rule is not necessary for bidirectional traffic.


        :param is_stateless: The is_stateless of this EgressSecurityRule.
        :type: bool
        """
        self._is_stateless = is_stateless

    @property
    def protocol(self):
        """
        **[Required]** Gets the protocol of this EgressSecurityRule.
        The transport protocol. Specify either `all` or an IPv4 protocol number as
        defined in
        `Protocol Numbers`__.
        Options are supported only for ICMP (\"1\"), TCP (\"6\"), UDP (\"17\"), and ICMPv6 (\"58\").

        __ http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml


        :return: The protocol of this EgressSecurityRule.
        :rtype: str
        """
        return self._protocol

    @protocol.setter
    def protocol(self, protocol):
        """
        Sets the protocol of this EgressSecurityRule.
        The transport protocol. Specify either `all` or an IPv4 protocol number as
        defined in
        `Protocol Numbers`__.
        Options are supported only for ICMP (\"1\"), TCP (\"6\"), UDP (\"17\"), and ICMPv6 (\"58\").

        __ http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml


        :param protocol: The protocol of this EgressSecurityRule.
        :type: str
        """
        self._protocol = protocol

    @property
    def tcp_options(self):
        """
        Gets the tcp_options of this EgressSecurityRule.

        :return: The tcp_options of this EgressSecurityRule.
        :rtype: oci.core.models.TcpOptions
        """
        return self._tcp_options

    @tcp_options.setter
    def tcp_options(self, tcp_options):
        """
        Sets the tcp_options of this EgressSecurityRule.

        :param tcp_options: The tcp_options of this EgressSecurityRule.
        :type: oci.core.models.TcpOptions
        """
        self._tcp_options = tcp_options

    @property
    def udp_options(self):
        """
        Gets the udp_options of this EgressSecurityRule.

        :return: The udp_options of this EgressSecurityRule.
        :rtype: oci.core.models.UdpOptions
        """
        return self._udp_options

    @udp_options.setter
    def udp_options(self, udp_options):
        """
        Sets the udp_options of this EgressSecurityRule.

        :param udp_options: The udp_options of this EgressSecurityRule.
        :type: oci.core.models.UdpOptions
        """
        self._udp_options = udp_options

    @property
    def description(self):
        """
        Gets the description of this EgressSecurityRule.
        An optional description of your choice for the rule.


        :return: The description of this EgressSecurityRule.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this EgressSecurityRule.
        An optional description of your choice for the rule.


        :param description: The description of this EgressSecurityRule.
        :type: str
        """
        self._description = description

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
