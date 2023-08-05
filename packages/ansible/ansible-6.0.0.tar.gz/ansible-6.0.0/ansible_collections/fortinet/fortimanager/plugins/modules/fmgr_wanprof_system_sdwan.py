#!/usr/bin/python
from __future__ import absolute_import, division, print_function
# Copyright 2019-2021 Fortinet, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.1'}

DOCUMENTATION = '''
---
module: fmgr_wanprof_system_sdwan
short_description: Configure redundant internet connections using SD-WAN
description:
    - This module is able to configure a FortiManager device.
    - Examples include all parameters and values which need to be adjusted to data sources before usage.

version_added: "2.10"
author:
    - Link Zheng (@chillancezen)
    - Jie Xue (@JieX19)
    - Frank Shen (@fshen01)
    - Hongbin Lu (@fgtdev-hblu)
notes:
    - Running in workspace locking mode is supported in this FortiManager module, the top
      level parameters workspace_locking_adom and workspace_locking_timeout help do the work.
    - To create or update an object, use state present directive.
    - To delete an object, use state absent directive.
    - Normally, running one module can fail when a non-zero rc is returned. you can also override
      the conditions to fail or succeed with parameters rc_failed and rc_succeeded

options:
    enable_log:
        description: Enable/Disable logging for task
        required: false
        type: bool
        default: false
    proposed_method:
        description: The overridden method for the underlying Json RPC request
        required: false
        type: str
        choices:
          - update
          - set
          - add
    bypass_validation:
        description: only set to True when module schema diffs with FortiManager API structure, module continues to execute without validating parameters
        required: false
        type: bool
        default: false
    workspace_locking_adom:
        description: the adom to lock for FortiManager running in workspace mode, the value can be global and others including root
        required: false
        type: str
    workspace_locking_timeout:
        description: the maximum time in seconds to wait for other user to release the workspace lock
        required: false
        type: int
        default: 300
    state:
        description: the directive to create, update or delete an object
        type: str
        required: true
        choices:
          - present
          - absent
    rc_succeeded:
        description: the rc codes list with which the conditions to succeed will be overriden
        type: list
        required: false
    rc_failed:
        description: the rc codes list with which the conditions to fail will be overriden
        type: list
        required: false
    adom:
        description: the parameter (adom) in requested url
        type: str
        required: true
    wanprof:
        description: the parameter (wanprof) in requested url
        type: str
        required: true
    wanprof_system_sdwan:
        description: the top level parameters set
        required: false
        type: dict
        suboptions:
            duplication:
                description: no description
                type: list
                suboptions:
                    dstaddr:
                        type: str
                        description: 'Destination address or address group names.'
                    dstaddr6:
                        type: str
                        description: 'Destination address6 or address6 group names.'
                    dstintf:
                        type: str
                        description: 'Outgoing (egress) interfaces or zones.'
                    id:
                        type: int
                        description: 'Duplication rule ID (1 - 255).'
                    packet-de-duplication:
                        type: str
                        description: 'Enable/disable discarding of packets that have been duplicated.'
                        choices:
                            - 'disable'
                            - 'enable'
                    packet-duplication:
                        type: str
                        description: 'Configure packet duplication method.'
                        choices:
                            - 'disable'
                            - 'force'
                            - 'on-demand'
                    service:
                        type: str
                        description: 'Service and service group name.'
                    srcaddr:
                        type: str
                        description: 'Source address or address group names.'
                    srcaddr6:
                        type: str
                        description: 'Source address6 or address6 group names.'
                    srcintf:
                        type: str
                        description: 'Incoming (ingress) interfaces or zones.'
                    service-id:
                        type: str
                        description: 'SD-WAN service rule ID list.'
            duplication-max-num:
                type: int
                description: 'Maximum number of interface members a packet is duplicated in the SD-WAN zone (2 - 4, default = 2; if set to 3, the original p...'
            fail-detect:
                type: str
                description: 'Enable/disable SD-WAN Internet connection status checking (failure detection).'
                choices:
                    - 'disable'
                    - 'enable'
            health-check:
                description: no description
                type: list
                suboptions:
                    _dynamic-server:
                        type: str
                        description: no description
                    addr-mode:
                        type: str
                        description: 'Address mode (IPv4 or IPv6).'
                        choices:
                            - 'ipv4'
                            - 'ipv6'
                    diffservcode:
                        type: str
                        description: 'Differentiated services code point (DSCP) in the IP header of the probe packet.'
                    dns-match-ip:
                        type: str
                        description: 'Response IP expected from DNS server if the protocol is DNS.'
                    dns-request-domain:
                        type: str
                        description: 'Fully qualified domain name to resolve for the DNS probe.'
                    failtime:
                        type: int
                        description: 'Number of failures before server is considered lost (1 - 3600, default = 5).'
                    ftp-file:
                        type: str
                        description: 'Full path and file name on the FTP server to download for FTP health-check to probe.'
                    ftp-mode:
                        type: str
                        description: 'FTP mode.'
                        choices:
                            - 'passive'
                            - 'port'
                    ha-priority:
                        type: int
                        description: 'HA election priority (1 - 50).'
                    http-agent:
                        type: str
                        description: 'String in the http-agent field in the HTTP header.'
                    http-get:
                        type: str
                        description: 'URL used to communicate with the server if the protocol if the protocol is HTTP.'
                    http-match:
                        type: str
                        description: 'Response string expected from the server if the protocol is HTTP.'
                    interval:
                        type: int
                        description: 'Status check interval in milliseconds, or the time between attempting to connect to the server (500 - 3600*1000 msec, ...'
                    members:
                        type: str
                        description: 'Member sequence number list.'
                    name:
                        type: str
                        description: 'Status check or health check name.'
                    packet-size:
                        type: int
                        description: 'Packet size of a twamp test session,'
                    password:
                        description: no description
                        type: str
                    port:
                        type: int
                        description: 'Port number used to communicate with the server over the selected protocol (0-65535, default = 0, auto select. http, t...'
                    probe-count:
                        type: int
                        description: 'Number of most recent probes that should be used to calculate latency and jitter (5 - 30, default = 30).'
                    probe-packets:
                        type: str
                        description: 'Enable/disable transmission of probe packets.'
                        choices:
                            - 'disable'
                            - 'enable'
                    probe-timeout:
                        type: int
                        description: 'Time to wait before a probe packet is considered lost (500 - 3600*1000 msec, default = 500).'
                    protocol:
                        type: str
                        description: 'Protocol used to determine if the FortiGate can communicate with the server.'
                        choices:
                            - 'ping'
                            - 'tcp-echo'
                            - 'udp-echo'
                            - 'http'
                            - 'twamp'
                            - 'ping6'
                            - 'dns'
                            - 'tcp-connect'
                            - 'ftp'
                    quality-measured-method:
                        type: str
                        description: 'Method to measure the quality of tcp-connect.'
                        choices:
                            - 'half-close'
                            - 'half-open'
                    recoverytime:
                        type: int
                        description: 'Number of successful responses received before server is considered recovered (1 - 3600, default = 5).'
                    security-mode:
                        type: str
                        description: 'Twamp controller security mode.'
                        choices:
                            - 'none'
                            - 'authentication'
                    server:
                        description: no description
                        type: str
                    sla:
                        description: no description
                        type: list
                        suboptions:
                            id:
                                type: int
                                description: 'SLA ID.'
                            jitter-threshold:
                                type: int
                                description: 'Jitter for SLA to make decision in milliseconds. (0 - 10000000, default = 5).'
                            latency-threshold:
                                type: int
                                description: 'Latency for SLA to make decision in milliseconds. (0 - 10000000, default = 5).'
                            link-cost-factor:
                                description: no description
                                type: list
                                choices:
                                 - latency
                                 - jitter
                                 - packet-loss
                            packetloss-threshold:
                                type: int
                                description: 'Packet loss for SLA to make decision in percentage. (0 - 100, default = 0).'
                    sla-fail-log-period:
                        type: int
                        description: 'Time interval in seconds that SLA fail log messages will be generated (0 - 3600, default = 0).'
                    sla-pass-log-period:
                        type: int
                        description: 'Time interval in seconds that SLA pass log messages will be generated (0 - 3600, default = 0).'
                    system-dns:
                        type: str
                        description: 'Enable/disable system DNS as the probe server.'
                        choices:
                            - 'disable'
                            - 'enable'
                    threshold-alert-jitter:
                        type: int
                        description: 'Alert threshold for jitter (ms, default = 0).'
                    threshold-alert-latency:
                        type: int
                        description: 'Alert threshold for latency (ms, default = 0).'
                    threshold-alert-packetloss:
                        type: int
                        description: 'Alert threshold for packet loss (percentage, default = 0).'
                    threshold-warning-jitter:
                        type: int
                        description: 'Warning threshold for jitter (ms, default = 0).'
                    threshold-warning-latency:
                        type: int
                        description: 'Warning threshold for latency (ms, default = 0).'
                    threshold-warning-packetloss:
                        type: int
                        description: 'Warning threshold for packet loss (percentage, default = 0).'
                    update-cascade-interface:
                        type: str
                        description: 'Enable/disable update cascade interface.'
                        choices:
                            - 'disable'
                            - 'enable'
                    update-static-route:
                        type: str
                        description: 'Enable/disable updating the static route.'
                        choices:
                            - 'disable'
                            - 'enable'
                    user:
                        type: str
                        description: 'The user name to access probe server.'
                    detect-mode:
                        type: str
                        description: 'The mode determining how to detect the server.'
                        choices:
                            - 'active'
                            - 'passive'
                            - 'prefer-passive'
            load-balance-mode:
                type: str
                description: 'Algorithm or mode to use for load balancing Internet traffic to SD-WAN members.'
                choices:
                    - 'source-ip-based'
                    - 'weight-based'
                    - 'usage-based'
                    - 'source-dest-ip-based'
                    - 'measured-volume-based'
            members:
                description: no description
                type: list
                suboptions:
                    _dynamic-member:
                        type: str
                        description: no description
                    comment:
                        type: str
                        description: 'Comments.'
                    cost:
                        type: int
                        description: 'Cost of this interface for services in SLA mode (0 - 4294967295, default = 0).'
                    gateway:
                        type: str
                        description: 'The default gateway for this interface. Usually the default gateway of the Internet service provider that this interfa...'
                    gateway6:
                        type: str
                        description: 'IPv6 gateway.'
                    ingress-spillover-threshold:
                        type: int
                        description: 'Ingress spillover threshold for this interface (0 - 16776000 kbit/s). When this traffic volume threshold is reached, n...'
                    interface:
                        type: str
                        description: 'Interface name.'
                    priority:
                        type: int
                        description: 'Priority of the interface (0 - 65535). Used for SD-WAN rules or priority rules.'
                    seq-num:
                        type: int
                        description: 'Sequence number(1-512).'
                    source:
                        type: str
                        description: 'Source IP address used in the health-check packet to the server.'
                    source6:
                        type: str
                        description: 'Source IPv6 address used in the health-check packet to the server.'
                    spillover-threshold:
                        type: int
                        description: 'Egress spillover threshold for this interface (0 - 16776000 kbit/s). When this traffic volume threshold is reached, ne...'
                    status:
                        type: str
                        description: 'Enable/disable this interface in the SD-WAN.'
                        choices:
                            - 'disable'
                            - 'enable'
                    volume-ratio:
                        type: int
                        description: 'Measured volume ratio (this value / sum of all values = percentage of link volume, 1 - 255).'
                    weight:
                        type: int
                        description: 'Weight of this interface for weighted load balancing. (1 - 255) More traffic is directed to interfaces with higher wei...'
                    zone:
                        type: str
                        description: 'Zone name.'
                    priority6:
                        type: int
                        description: 'Priority of the interface for IPv6 (1 - 65535, default = 1024). Used for SD-WAN rules or priority rules.'
            neighbor:
                description: no description
                type: list
                suboptions:
                    health-check:
                        type: str
                        description: 'SD-WAN health-check name.'
                    ip:
                        type: str
                        description: 'IP/IPv6 address of neighbor.'
                    member:
                        type: str
                        description: 'Member sequence number.'
                    role:
                        type: str
                        description: 'Role of neighbor.'
                        choices:
                            - 'primary'
                            - 'secondary'
                            - 'standalone'
                    sla-id:
                        type: int
                        description: 'SLA ID.'
            neighbor-hold-boot-time:
                type: int
                description: 'Waiting period in seconds when switching from the primary neighbor to the secondary neighbor from the neighbor start. (0 - 100...'
            neighbor-hold-down:
                type: str
                description: 'Enable/disable hold switching from the secondary neighbor to the primary neighbor.'
                choices:
                    - 'disable'
                    - 'enable'
            neighbor-hold-down-time:
                type: int
                description: 'Waiting period in seconds when switching from the secondary neighbor to the primary neighbor when hold-down is disabled. (0 - ...'
            service:
                description: no description
                type: list
                suboptions:
                    addr-mode:
                        type: str
                        description: 'Address mode (IPv4 or IPv6).'
                        choices:
                            - 'ipv4'
                            - 'ipv6'
                    bandwidth-weight:
                        type: int
                        description: 'Coefficient of reciprocal of available bidirectional bandwidth in the formula of custom-profile-1.'
                    default:
                        type: str
                        description: 'Enable/disable use of SD-WAN as default service.'
                        choices:
                            - 'disable'
                            - 'enable'
                    dscp-forward:
                        type: str
                        description: 'Enable/disable forward traffic DSCP tag.'
                        choices:
                            - 'disable'
                            - 'enable'
                    dscp-forward-tag:
                        type: str
                        description: 'Forward traffic DSCP tag.'
                    dscp-reverse:
                        type: str
                        description: 'Enable/disable reverse traffic DSCP tag.'
                        choices:
                            - 'disable'
                            - 'enable'
                    dscp-reverse-tag:
                        type: str
                        description: 'Reverse traffic DSCP tag.'
                    dst:
                        type: str
                        description: 'Destination address name.'
                    dst-negate:
                        type: str
                        description: 'Enable/disable negation of destination address match.'
                        choices:
                            - 'disable'
                            - 'enable'
                    dst6:
                        type: str
                        description: 'Destination address6 name.'
                    end-port:
                        type: int
                        description: 'End destination port number.'
                    gateway:
                        type: str
                        description: 'Enable/disable SD-WAN service gateway.'
                        choices:
                            - 'disable'
                            - 'enable'
                    groups:
                        type: str
                        description: 'User groups.'
                    hash-mode:
                        type: str
                        description: 'Hash algorithm for selected priority members for load balance mode.'
                        choices:
                            - 'round-robin'
                            - 'source-ip-based'
                            - 'source-dest-ip-based'
                            - 'inbandwidth'
                            - 'outbandwidth'
                            - 'bibandwidth'
                    health-check:
                        type: str
                        description: 'Health check list.'
                    hold-down-time:
                        type: int
                        description: 'Waiting period in seconds when switching from the back-up member to the primary member (0 - 10000000, default = 0).'
                    id:
                        type: int
                        description: 'SD-WAN rule ID (1 - 4000).'
                    input-device:
                        type: str
                        description: 'Source interface name.'
                    input-device-negate:
                        type: str
                        description: 'Enable/disable negation of input device match.'
                        choices:
                            - 'disable'
                            - 'enable'
                    internet-service:
                        type: str
                        description: 'Enable/disable use of Internet service for application-based load balancing.'
                        choices:
                            - 'disable'
                            - 'enable'
                    internet-service-app-ctrl:
                        description: no description
                        type: int
                    internet-service-app-ctrl-group:
                        type: str
                        description: 'Application control based Internet Service group list.'
                    internet-service-custom:
                        type: str
                        description: 'Custom Internet service name list.'
                    internet-service-custom-group:
                        type: str
                        description: 'Custom Internet Service group list.'
                    internet-service-group:
                        type: str
                        description: 'Internet Service group list.'
                    internet-service-name:
                        type: str
                        description: 'Internet service name list.'
                    jitter-weight:
                        type: int
                        description: 'Coefficient of jitter in the formula of custom-profile-1.'
                    latency-weight:
                        type: int
                        description: 'Coefficient of latency in the formula of custom-profile-1.'
                    link-cost-factor:
                        type: str
                        description: 'Link cost factor.'
                        choices:
                            - 'latency'
                            - 'jitter'
                            - 'packet-loss'
                            - 'inbandwidth'
                            - 'outbandwidth'
                            - 'bibandwidth'
                            - 'custom-profile-1'
                    link-cost-threshold:
                        type: int
                        description: 'Percentage threshold change of link cost values that will result in policy route regeneration (0 - 10000000, default =...'
                    minimum-sla-meet-members:
                        type: int
                        description: 'Minimum number of members which meet SLA.'
                    mode:
                        type: str
                        description: 'Control how the SD-WAN rule sets the priority of interfaces in the SD-WAN.'
                        choices:
                            - 'auto'
                            - 'manual'
                            - 'priority'
                            - 'sla'
                            - 'load-balance'
                    name:
                        type: str
                        description: 'SD-WAN rule name.'
                    packet-loss-weight:
                        type: int
                        description: 'Coefficient of packet-loss in the formula of custom-profile-1.'
                    priority-members:
                        type: str
                        description: 'Member sequence number list.'
                    protocol:
                        type: int
                        description: 'Protocol number.'
                    quality-link:
                        type: int
                        description: 'Quality grade.'
                    role:
                        type: str
                        description: 'Service role to work with neighbor.'
                        choices:
                            - 'primary'
                            - 'secondary'
                            - 'standalone'
                    route-tag:
                        type: int
                        description: 'IPv4 route map route-tag.'
                    sla:
                        description: no description
                        type: list
                        suboptions:
                            health-check:
                                type: str
                                description: 'SD-WAN health-check.'
                            id:
                                type: int
                                description: 'SLA ID.'
                    sla-compare-method:
                        type: str
                        description: 'Method to compare SLA value for SLA mode.'
                        choices:
                            - 'order'
                            - 'number'
                    src:
                        type: str
                        description: 'Source address name.'
                    src-negate:
                        type: str
                        description: 'Enable/disable negation of source address match.'
                        choices:
                            - 'disable'
                            - 'enable'
                    src6:
                        type: str
                        description: 'Source address6 name.'
                    standalone-action:
                        type: str
                        description: 'Enable/disable service when selected neighbor role is standalone while service role is not standalone.'
                        choices:
                            - 'disable'
                            - 'enable'
                    start-port:
                        type: int
                        description: 'Start destination port number.'
                    status:
                        type: str
                        description: 'Enable/disable SD-WAN service.'
                        choices:
                            - 'disable'
                            - 'enable'
                    tos:
                        type: str
                        description: 'Type of service bit pattern.'
                    tos-mask:
                        type: str
                        description: 'Type of service evaluated bits.'
                    users:
                        type: str
                        description: 'User name.'
                    tie-break:
                        type: str
                        description: 'Method of selecting member if more than one meets the SLA.'
                        choices:
                            - 'zone'
                            - 'cfg-order'
                            - 'fib-best-match'
                    use-shortcut-sla:
                        type: str
                        description: 'Enable/disable use of ADVPN shortcut for quality comparison.'
                        choices:
                            - 'disable'
                            - 'enable'
            status:
                type: str
                description: 'Enable/disable SD-WAN.'
                choices:
                    - 'disable'
                    - 'enable'
            zone:
                description: no description
                type: list
                suboptions:
                    name:
                        type: str
                        description: 'Zone name.'
                    service-sla-tie-break:
                        type: str
                        description: 'Method of selecting member if more than one meets the SLA.'
                        choices:
                            - 'cfg-order'
                            - 'fib-best-match'

'''

EXAMPLES = '''
 - hosts: fortimanager-inventory
   collections:
     - fortinet.fortimanager
   connection: httpapi
   vars:
      ansible_httpapi_use_ssl: True
      ansible_httpapi_validate_certs: False
      ansible_httpapi_port: 443
   tasks:
    - name: Configure redundant internet connections using SD-WAN
      fmgr_wanprof_system_sdwan:
         bypass_validation: False
         workspace_locking_adom: <value in [global, custom adom including root]>
         workspace_locking_timeout: 300
         rc_succeeded: [0, -2, -3, ...]
         rc_failed: [-2, -3, ...]
         adom: <your own value>
         wanprof: <your own value>
         wanprof_system_sdwan:
            duplication:
              -
                  dstaddr: <value of string>
                  dstaddr6: <value of string>
                  dstintf: <value of string>
                  id: <value of integer>
                  packet-de-duplication: <value in [disable, enable]>
                  packet-duplication: <value in [disable, force, on-demand]>
                  service: <value of string>
                  srcaddr: <value of string>
                  srcaddr6: <value of string>
                  srcintf: <value of string>
                  service-id: <value of string>
            duplication-max-num: <value of integer>
            fail-detect: <value in [disable, enable]>
            health-check:
              -
                  _dynamic-server: <value of string>
                  addr-mode: <value in [ipv4, ipv6]>
                  diffservcode: <value of string>
                  dns-match-ip: <value of string>
                  dns-request-domain: <value of string>
                  failtime: <value of integer>
                  ftp-file: <value of string>
                  ftp-mode: <value in [passive, port]>
                  ha-priority: <value of integer>
                  http-agent: <value of string>
                  http-get: <value of string>
                  http-match: <value of string>
                  interval: <value of integer>
                  members: <value of string>
                  name: <value of string>
                  packet-size: <value of integer>
                  password: <value of string>
                  port: <value of integer>
                  probe-count: <value of integer>
                  probe-packets: <value in [disable, enable]>
                  probe-timeout: <value of integer>
                  protocol: <value in [ping, tcp-echo, udp-echo, ...]>
                  quality-measured-method: <value in [half-close, half-open]>
                  recoverytime: <value of integer>
                  security-mode: <value in [none, authentication]>
                  server: <value of string>
                  sla:
                    -
                        id: <value of integer>
                        jitter-threshold: <value of integer>
                        latency-threshold: <value of integer>
                        link-cost-factor:
                          - latency
                          - jitter
                          - packet-loss
                        packetloss-threshold: <value of integer>
                  sla-fail-log-period: <value of integer>
                  sla-pass-log-period: <value of integer>
                  system-dns: <value in [disable, enable]>
                  threshold-alert-jitter: <value of integer>
                  threshold-alert-latency: <value of integer>
                  threshold-alert-packetloss: <value of integer>
                  threshold-warning-jitter: <value of integer>
                  threshold-warning-latency: <value of integer>
                  threshold-warning-packetloss: <value of integer>
                  update-cascade-interface: <value in [disable, enable]>
                  update-static-route: <value in [disable, enable]>
                  user: <value of string>
                  detect-mode: <value in [active, passive, prefer-passive]>
            load-balance-mode: <value in [source-ip-based, weight-based, usage-based, ...]>
            members:
              -
                  _dynamic-member: <value of string>
                  comment: <value of string>
                  cost: <value of integer>
                  gateway: <value of string>
                  gateway6: <value of string>
                  ingress-spillover-threshold: <value of integer>
                  interface: <value of string>
                  priority: <value of integer>
                  seq-num: <value of integer>
                  source: <value of string>
                  source6: <value of string>
                  spillover-threshold: <value of integer>
                  status: <value in [disable, enable]>
                  volume-ratio: <value of integer>
                  weight: <value of integer>
                  zone: <value of string>
                  priority6: <value of integer>
            neighbor:
              -
                  health-check: <value of string>
                  ip: <value of string>
                  member: <value of string>
                  role: <value in [primary, secondary, standalone]>
                  sla-id: <value of integer>
            neighbor-hold-boot-time: <value of integer>
            neighbor-hold-down: <value in [disable, enable]>
            neighbor-hold-down-time: <value of integer>
            service:
              -
                  addr-mode: <value in [ipv4, ipv6]>
                  bandwidth-weight: <value of integer>
                  default: <value in [disable, enable]>
                  dscp-forward: <value in [disable, enable]>
                  dscp-forward-tag: <value of string>
                  dscp-reverse: <value in [disable, enable]>
                  dscp-reverse-tag: <value of string>
                  dst: <value of string>
                  dst-negate: <value in [disable, enable]>
                  dst6: <value of string>
                  end-port: <value of integer>
                  gateway: <value in [disable, enable]>
                  groups: <value of string>
                  hash-mode: <value in [round-robin, source-ip-based, source-dest-ip-based, ...]>
                  health-check: <value of string>
                  hold-down-time: <value of integer>
                  id: <value of integer>
                  input-device: <value of string>
                  input-device-negate: <value in [disable, enable]>
                  internet-service: <value in [disable, enable]>
                  internet-service-app-ctrl: <value of integer>
                  internet-service-app-ctrl-group: <value of string>
                  internet-service-custom: <value of string>
                  internet-service-custom-group: <value of string>
                  internet-service-group: <value of string>
                  internet-service-name: <value of string>
                  jitter-weight: <value of integer>
                  latency-weight: <value of integer>
                  link-cost-factor: <value in [latency, jitter, packet-loss, ...]>
                  link-cost-threshold: <value of integer>
                  minimum-sla-meet-members: <value of integer>
                  mode: <value in [auto, manual, priority, ...]>
                  name: <value of string>
                  packet-loss-weight: <value of integer>
                  priority-members: <value of string>
                  protocol: <value of integer>
                  quality-link: <value of integer>
                  role: <value in [primary, secondary, standalone]>
                  route-tag: <value of integer>
                  sla:
                    -
                        health-check: <value of string>
                        id: <value of integer>
                  sla-compare-method: <value in [order, number]>
                  src: <value of string>
                  src-negate: <value in [disable, enable]>
                  src6: <value of string>
                  standalone-action: <value in [disable, enable]>
                  start-port: <value of integer>
                  status: <value in [disable, enable]>
                  tos: <value of string>
                  tos-mask: <value of string>
                  users: <value of string>
                  tie-break: <value in [zone, cfg-order, fib-best-match]>
                  use-shortcut-sla: <value in [disable, enable]>
            status: <value in [disable, enable]>
            zone:
              -
                  name: <value of string>
                  service-sla-tie-break: <value in [cfg-order, fib-best-match]>

'''

RETURN = '''
request_url:
    description: The full url requested
    returned: always
    type: str
    sample: /sys/login/user
response_code:
    description: The status of api request
    returned: always
    type: int
    sample: 0
response_message:
    description: The descriptive message of the api response
    type: str
    returned: always
    sample: OK.

'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection
from ansible_collections.fortinet.fortimanager.plugins.module_utils.napi import NAPIManager
from ansible_collections.fortinet.fortimanager.plugins.module_utils.napi import check_galaxy_version
from ansible_collections.fortinet.fortimanager.plugins.module_utils.napi import check_parameter_bypass


def main():
    jrpc_urls = [
        '/pm/config/adom/{adom}/wanprof/{wanprof}/system/sdwan'
    ]

    perobject_jrpc_urls = [
        '/pm/config/adom/{adom}/wanprof/{wanprof}/system/sdwan/{sdwan}'
    ]

    url_params = ['adom', 'wanprof']
    module_primary_key = None
    module_arg_spec = {
        'enable_log': {
            'type': 'bool',
            'required': False,
            'default': False
        },
        'forticloud_access_token': {
            'type': 'str',
            'required': False,
            'no_log': True
        },
        'proposed_method': {
            'type': 'str',
            'required': False,
            'choices': [
                'set',
                'update',
                'add'
            ]
        },
        'bypass_validation': {
            'type': 'bool',
            'required': False,
            'default': False
        },
        'workspace_locking_adom': {
            'type': 'str',
            'required': False
        },
        'workspace_locking_timeout': {
            'type': 'int',
            'required': False,
            'default': 300
        },
        'rc_succeeded': {
            'required': False,
            'type': 'list'
        },
        'rc_failed': {
            'required': False,
            'type': 'list'
        },
        'adom': {
            'required': True,
            'type': 'str'
        },
        'wanprof': {
            'required': True,
            'type': 'str'
        },
        'wanprof_system_sdwan': {
            'required': False,
            'type': 'dict',
            'revision': {
                '6.4.2': True,
                '6.4.5': True,
                '7.0.0': True
            },
            'options': {
                'duplication': {
                    'required': False,
                    'revision': {
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'options': {
                        'dstaddr': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'dstaddr6': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'dstintf': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'id': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'packet-de-duplication': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        },
                        'packet-duplication': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'force',
                                'on-demand'
                            ],
                            'type': 'str'
                        },
                        'service': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'srcaddr': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'srcaddr6': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'srcintf': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'service-id': {
                            'required': False,
                            'revision': {
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        }
                    }
                },
                'duplication-max-num': {
                    'required': False,
                    'revision': {
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'fail-detect': {
                    'required': False,
                    'revision': {
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'disable',
                        'enable'
                    ],
                    'type': 'str'
                },
                'health-check': {
                    'required': False,
                    'revision': {
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'options': {
                        '_dynamic-server': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': False
                            },
                            'type': 'str'
                        },
                        'addr-mode': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'ipv4',
                                'ipv6'
                            ],
                            'type': 'str'
                        },
                        'diffservcode': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'dns-match-ip': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'dns-request-domain': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'failtime': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'ftp-file': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'ftp-mode': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'passive',
                                'port'
                            ],
                            'type': 'str'
                        },
                        'ha-priority': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'http-agent': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'http-get': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'http-match': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'interval': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'members': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'name': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'packet-size': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'password': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'port': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'probe-count': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'probe-packets': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        },
                        'probe-timeout': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'protocol': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'ping',
                                'tcp-echo',
                                'udp-echo',
                                'http',
                                'twamp',
                                'ping6',
                                'dns',
                                'tcp-connect',
                                'ftp'
                            ],
                            'type': 'str'
                        },
                        'quality-measured-method': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'half-close',
                                'half-open'
                            ],
                            'type': 'str'
                        },
                        'recoverytime': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'security-mode': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'none',
                                'authentication'
                            ],
                            'type': 'str'
                        },
                        'server': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'sla': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'list',
                            'options': {
                                'id': {
                                    'required': False,
                                    'revision': {
                                        '6.4.2': True,
                                        '6.4.5': True,
                                        '7.0.0': True
                                    },
                                    'type': 'int'
                                },
                                'jitter-threshold': {
                                    'required': False,
                                    'revision': {
                                        '6.4.2': True,
                                        '6.4.5': True,
                                        '7.0.0': True
                                    },
                                    'type': 'int'
                                },
                                'latency-threshold': {
                                    'required': False,
                                    'revision': {
                                        '6.4.2': True,
                                        '6.4.5': True,
                                        '7.0.0': True
                                    },
                                    'type': 'int'
                                },
                                'link-cost-factor': {
                                    'required': False,
                                    'revision': {
                                        '6.4.2': True,
                                        '6.4.5': True,
                                        '7.0.0': True
                                    },
                                    'type': 'list',
                                    'choices': [
                                        'latency',
                                        'jitter',
                                        'packet-loss'
                                    ]
                                },
                                'packetloss-threshold': {
                                    'required': False,
                                    'revision': {
                                        '6.4.2': True,
                                        '6.4.5': True,
                                        '7.0.0': True
                                    },
                                    'type': 'int'
                                }
                            }
                        },
                        'sla-fail-log-period': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'sla-pass-log-period': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'system-dns': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        },
                        'threshold-alert-jitter': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'threshold-alert-latency': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'threshold-alert-packetloss': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'threshold-warning-jitter': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'threshold-warning-latency': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'threshold-warning-packetloss': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'update-cascade-interface': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        },
                        'update-static-route': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        },
                        'user': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'detect-mode': {
                            'required': False,
                            'revision': {
                                '7.0.0': True
                            },
                            'choices': [
                                'active',
                                'passive',
                                'prefer-passive'
                            ],
                            'type': 'str'
                        }
                    }
                },
                'load-balance-mode': {
                    'required': False,
                    'revision': {
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'source-ip-based',
                        'weight-based',
                        'usage-based',
                        'source-dest-ip-based',
                        'measured-volume-based'
                    ],
                    'type': 'str'
                },
                'members': {
                    'required': False,
                    'revision': {
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'options': {
                        '_dynamic-member': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': False
                            },
                            'type': 'str'
                        },
                        'comment': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'cost': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'gateway': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'gateway6': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'ingress-spillover-threshold': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'interface': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'priority': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'seq-num': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'source': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'source6': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'spillover-threshold': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'status': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        },
                        'volume-ratio': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'weight': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'zone': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'priority6': {
                            'required': False,
                            'revision': {
                                '7.0.0': True
                            },
                            'type': 'int'
                        }
                    }
                },
                'neighbor': {
                    'required': False,
                    'revision': {
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'options': {
                        'health-check': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'ip': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'member': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'role': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'primary',
                                'secondary',
                                'standalone'
                            ],
                            'type': 'str'
                        },
                        'sla-id': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        }
                    }
                },
                'neighbor-hold-boot-time': {
                    'required': False,
                    'revision': {
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'neighbor-hold-down': {
                    'required': False,
                    'revision': {
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'disable',
                        'enable'
                    ],
                    'type': 'str'
                },
                'neighbor-hold-down-time': {
                    'required': False,
                    'revision': {
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'service': {
                    'required': False,
                    'revision': {
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'options': {
                        'addr-mode': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'ipv4',
                                'ipv6'
                            ],
                            'type': 'str'
                        },
                        'bandwidth-weight': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'default': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        },
                        'dscp-forward': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        },
                        'dscp-forward-tag': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'dscp-reverse': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        },
                        'dscp-reverse-tag': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'dst': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'dst-negate': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        },
                        'dst6': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'end-port': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'gateway': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        },
                        'groups': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'hash-mode': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'round-robin',
                                'source-ip-based',
                                'source-dest-ip-based',
                                'inbandwidth',
                                'outbandwidth',
                                'bibandwidth'
                            ],
                            'type': 'str'
                        },
                        'health-check': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'hold-down-time': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'id': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'input-device': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'input-device-negate': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        },
                        'internet-service': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        },
                        'internet-service-app-ctrl': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'internet-service-app-ctrl-group': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'internet-service-custom': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'internet-service-custom-group': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'internet-service-group': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'internet-service-name': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'jitter-weight': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'latency-weight': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'link-cost-factor': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'latency',
                                'jitter',
                                'packet-loss',
                                'inbandwidth',
                                'outbandwidth',
                                'bibandwidth',
                                'custom-profile-1'
                            ],
                            'type': 'str'
                        },
                        'link-cost-threshold': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'minimum-sla-meet-members': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'mode': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'auto',
                                'manual',
                                'priority',
                                'sla',
                                'load-balance'
                            ],
                            'type': 'str'
                        },
                        'name': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'packet-loss-weight': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'priority-members': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'protocol': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'quality-link': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'role': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'primary',
                                'secondary',
                                'standalone'
                            ],
                            'type': 'str'
                        },
                        'route-tag': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'sla': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'list',
                            'options': {
                                'health-check': {
                                    'required': False,
                                    'revision': {
                                        '6.4.2': True,
                                        '6.4.5': True,
                                        '7.0.0': True
                                    },
                                    'type': 'str'
                                },
                                'id': {
                                    'required': False,
                                    'revision': {
                                        '6.4.2': True,
                                        '6.4.5': True,
                                        '7.0.0': True
                                    },
                                    'type': 'int'
                                }
                            }
                        },
                        'sla-compare-method': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'order',
                                'number'
                            ],
                            'type': 'str'
                        },
                        'src': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'src-negate': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        },
                        'src6': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'standalone-action': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        },
                        'start-port': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'int'
                        },
                        'status': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        },
                        'tos': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'tos-mask': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'users': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'tie-break': {
                            'required': False,
                            'revision': {
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'zone',
                                'cfg-order',
                                'fib-best-match'
                            ],
                            'type': 'str'
                        },
                        'use-shortcut-sla': {
                            'required': False,
                            'revision': {
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        }
                    }
                },
                'status': {
                    'required': False,
                    'revision': {
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'disable',
                        'enable'
                    ],
                    'type': 'str'
                },
                'zone': {
                    'required': False,
                    'revision': {
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'options': {
                        'name': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'service-sla-tie-break': {
                            'required': False,
                            'revision': {
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'choices': [
                                'cfg-order',
                                'fib-best-match'
                            ],
                            'type': 'str'
                        }
                    }
                }
            }

        }
    }

    params_validation_blob = []
    check_galaxy_version(module_arg_spec)
    module = AnsibleModule(argument_spec=check_parameter_bypass(module_arg_spec, 'wanprof_system_sdwan'),
                           supports_check_mode=False)

    fmgr = None
    if module._socket_path:
        connection = Connection(module._socket_path)
        connection.set_option('enable_log', module.params['enable_log'] if 'enable_log' in module.params else False)
        connection.set_option('forticloud_access_token',
                              module.params['forticloud_access_token'] if 'forticloud_access_token' in module.params else None)
        fmgr = NAPIManager(jrpc_urls, perobject_jrpc_urls, module_primary_key, url_params, module, connection, top_level_schema_name='data')
        fmgr.validate_parameters(params_validation_blob)
        fmgr.process_partial_curd(argument_specs=module_arg_spec)
    else:
        module.fail_json(msg='MUST RUN IN HTTPAPI MODE')
    module.exit_json(meta=module.params)


if __name__ == '__main__':
    main()
