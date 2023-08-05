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
module: fmgr_vap_dynamicmapping
short_description: Configure Virtual Access Points
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
    vap:
        description: the parameter (vap) in requested url
        type: str
        required: true
    vap_dynamicmapping:
        description: the top level parameters set
        required: false
        type: dict
        suboptions:
            _centmgmt:
                type: str
                default: 'disable'
                description: '_Centmgmt.'
                choices:
                    - 'disable'
                    - 'enable'
            _dhcp_svr_id:
                type: str
                description: '_Dhcp_Svr_Id.'
            _intf_allowaccess:
                description: no description
                type: list
                choices:
                 - https
                 - ping
                 - ssh
                 - snmp
                 - http
                 - telnet
                 - fgfm
                 - auto-ipsec
                 - radius-acct
                 - probe-response
                 - capwap
            _intf_device-identification:
                type: str
                default: 'disable'
                description: '_Intf_Device-Identification.'
                choices:
                    - 'disable'
                    - 'enable'
            _intf_device-netscan:
                type: str
                default: 'disable'
                description: '_Intf_Device-Netscan.'
                choices:
                    - 'disable'
                    - 'enable'
            _intf_dhcp-relay-ip:
                description: no description
                type: str
            _intf_dhcp-relay-service:
                type: str
                default: 'disable'
                description: '_Intf_Dhcp-Relay-Service.'
                choices:
                    - 'disable'
                    - 'enable'
            _intf_dhcp-relay-type:
                type: str
                default: 'regular'
                description: '_Intf_Dhcp-Relay-Type.'
                choices:
                    - 'regular'
                    - 'ipsec'
            _intf_dhcp6-relay-ip:
                type: str
                description: '_Intf_Dhcp6-Relay-Ip.'
            _intf_dhcp6-relay-service:
                type: str
                default: 'disable'
                description: '_Intf_Dhcp6-Relay-Service.'
                choices:
                    - 'disable'
                    - 'enable'
            _intf_dhcp6-relay-type:
                type: str
                default: 'regular'
                description: '_Intf_Dhcp6-Relay-Type.'
                choices:
                    - 'regular'
            _intf_ip:
                type: str
                description: '_Intf_Ip.'
            _intf_ip6-address:
                type: str
                description: '_Intf_Ip6-Address.'
            _intf_ip6-allowaccess:
                description: no description
                type: list
                choices:
                 - https
                 - ping
                 - ssh
                 - snmp
                 - http
                 - telnet
                 - any
                 - fgfm
                 - capwap
            _intf_listen-forticlient-connection:
                type: str
                default: 'disable'
                description: '_Intf_Listen-Forticlient-Connection.'
                choices:
                    - 'disable'
                    - 'enable'
            _scope:
                description: no description
                type: list
                suboptions:
                    name:
                        type: str
                        description: 'Name.'
                    vdom:
                        type: str
                        description: 'Vdom.'
            acct-interim-interval:
                type: int
                description: 'WiFi RADIUS accounting interim interval (60 - 86400 sec, default = 0).'
            address-group:
                type: str
                description: 'Address group ID.'
            alias:
                type: str
                description: 'Alias.'
            atf-weight:
                type: int
                description: 'Airtime weight in percentage (default = 20).'
            auth:
                type: str
                description: 'Authentication protocol.'
                choices:
                    - 'PSK'
                    - 'psk'
                    - 'RADIUS'
                    - 'radius'
                    - 'usergroup'
            broadcast-ssid:
                type: str
                description: 'Enable/disable broadcasting the SSID (default = enable).'
                choices:
                    - 'disable'
                    - 'enable'
            broadcast-suppression:
                description: no description
                type: list
                choices:
                 - dhcp
                 - arp
                 - dhcp2
                 - arp2
                 - netbios-ns
                 - netbios-ds
                 - arp3
                 - dhcp-up
                 - dhcp-down
                 - arp-known
                 - arp-unknown
                 - arp-reply
                 - ipv6
                 - dhcp-starvation
                 - arp-poison
                 - all-other-mc
                 - all-other-bc
                 - arp-proxy
                 - dhcp-ucast
            captive-portal-ac-name:
                type: str
                description: 'Local-bridging captive portal ac-name.'
            captive-portal-macauth-radius-secret:
                description: no description
                type: str
            captive-portal-macauth-radius-server:
                type: str
                description: 'Captive portal external RADIUS server domain name or IP address.'
            captive-portal-radius-secret:
                description: no description
                type: str
            captive-portal-radius-server:
                type: str
                description: 'Captive portal RADIUS server domain name or IP address.'
            captive-portal-session-timeout-interval:
                type: int
                description: 'Session timeout interval (0 - 864000 sec, default = 0).'
            client-count:
                type: int
                description: 'Client-Count.'
            dhcp-lease-time:
                type: int
                description: 'DHCP lease time in seconds for NAT IP address.'
            dhcp-option82-circuit-id-insertion:
                type: str
                description: 'Enable/disable DHCP option 82 circuit-id insert (default = disable).'
                choices:
                    - 'disable'
                    - 'style-1'
                    - 'style-2'
                    - 'style-3'
            dhcp-option82-insertion:
                type: str
                description: 'Enable/disable DHCP option 82 insert (default = disable).'
                choices:
                    - 'disable'
                    - 'enable'
            dhcp-option82-remote-id-insertion:
                type: str
                description: 'Enable/disable DHCP option 82 remote-id insert (default = disable).'
                choices:
                    - 'disable'
                    - 'style-1'
            dynamic-vlan:
                type: str
                description: 'Enable/disable dynamic VLAN assignment.'
                choices:
                    - 'disable'
                    - 'enable'
            eap-reauth:
                type: str
                description: 'Enable/disable EAP re-authentication for WPA-Enterprise security.'
                choices:
                    - 'disable'
                    - 'enable'
            eap-reauth-intv:
                type: int
                description: 'EAP re-authentication interval (1800 - 864000 sec, default = 86400).'
            eapol-key-retries:
                type: str
                description: 'Enable/disable retransmission of EAPOL-Key frames (message 3/4 and group message 1/2) (default = enable).'
                choices:
                    - 'disable'
                    - 'enable'
            encrypt:
                type: str
                description: 'Encryption protocol to use (only available when security is set to a WPA type).'
                choices:
                    - 'TKIP'
                    - 'AES'
                    - 'TKIP-AES'
            external-fast-roaming:
                type: str
                description: 'Enable/disable fast roaming or pre-authentication with external APs not managed by the FortiGate (default = disable).'
                choices:
                    - 'disable'
                    - 'enable'
            external-logout:
                type: str
                description: 'URL of external authentication logout server.'
            external-web:
                type: str
                description: 'URL of external authentication web server.'
            fast-bss-transition:
                type: str
                description: 'Enable/disable 802.11r Fast BSS Transition (FT) (default = disable).'
                choices:
                    - 'disable'
                    - 'enable'
            fast-roaming:
                type: str
                description: 'Enable/disable fast-roaming, or pre-authentication, where supported by clients (default = disable).'
                choices:
                    - 'disable'
                    - 'enable'
            ft-mobility-domain:
                type: int
                description: 'Mobility domain identifier in FT (1 - 65535, default = 1000).'
            ft-over-ds:
                type: str
                description: 'Enable/disable FT over the Distribution System (DS).'
                choices:
                    - 'disable'
                    - 'enable'
            ft-r0-key-lifetime:
                type: int
                description: 'Lifetime of the PMK-R0 key in FT, 1-65535 minutes.'
            gtk-rekey:
                type: str
                description: 'Enable/disable GTK rekey for WPA security.'
                choices:
                    - 'disable'
                    - 'enable'
            gtk-rekey-intv:
                type: int
                description: 'GTK rekey interval (1800 - 864000 sec, default = 86400).'
            hotspot20-profile:
                type: str
                description: 'Hotspot 2.0 profile name.'
            intra-vap-privacy:
                type: str
                description: 'Enable/disable blocking communication between clients on the same SSID (called intra-SSID privacy) (default = disable).'
                choices:
                    - 'disable'
                    - 'enable'
            ip:
                type: str
                description: 'IP address and subnet mask for the local standalone NAT subnet.'
            key:
                description: no description
                type: str
            keyindex:
                type: int
                description: 'WEP key index (1 - 4).'
            ldpc:
                type: str
                description: 'VAP low-density parity-check (LDPC) coding configuration.'
                choices:
                    - 'disable'
                    - 'tx'
                    - 'rx'
                    - 'rxtx'
            local-authentication:
                type: str
                description: 'Enable/disable AP local authentication.'
                choices:
                    - 'disable'
                    - 'enable'
            local-bridging:
                type: str
                description: 'Enable/disable bridging of wireless and Ethernet interfaces on the FortiAP (default = disable).'
                choices:
                    - 'disable'
                    - 'enable'
            local-lan:
                type: str
                description: 'Allow/deny traffic destined for a Class A, B, or C private IP address (default = allow).'
                choices:
                    - 'deny'
                    - 'allow'
            local-standalone:
                type: str
                description: 'Enable/disable AP local standalone (default = disable).'
                choices:
                    - 'disable'
                    - 'enable'
            local-standalone-nat:
                type: str
                description: 'Enable/disable AP local standalone NAT mode.'
                choices:
                    - 'disable'
                    - 'enable'
            local-switching:
                type: str
                description: 'Local-Switching.'
                choices:
                    - 'disable'
                    - 'enable'
            mac-auth-bypass:
                type: str
                description: 'Enable/disable MAC authentication bypass.'
                choices:
                    - 'disable'
                    - 'enable'
            mac-filter:
                type: str
                description: 'Enable/disable MAC filtering to block wireless clients by mac address.'
                choices:
                    - 'disable'
                    - 'enable'
            mac-filter-policy-other:
                type: str
                description: 'Allow or block clients with MAC addresses that are not in the filter list.'
                choices:
                    - 'deny'
                    - 'allow'
            max-clients:
                type: int
                description: 'Maximum number of clients that can connect simultaneously to the VAP (default = 0, meaning no limitation).'
            max-clients-ap:
                type: int
                description: 'Maximum number of clients that can connect simultaneously to the VAP per AP radio (default = 0, meaning no limitation).'
            me-disable-thresh:
                type: int
                description: 'Disable multicast enhancement when this many clients are receiving multicast traffic.'
            mesh-backhaul:
                type: str
                description: 'Enable/disable using this VAP as a WiFi mesh backhaul (default = disable). This entry is only available when security is set t...'
                choices:
                    - 'disable'
                    - 'enable'
            mpsk:
                type: str
                description: 'Enable/disable multiple PSK authentication.'
                choices:
                    - 'disable'
                    - 'enable'
            mpsk-concurrent-clients:
                type: int
                description: 'Maximum number of concurrent clients that connect using the same passphrase in multiple PSK authentication (0 - 65535, default...'
            multicast-enhance:
                type: str
                description: 'Enable/disable converting multicast to unicast to improve performance (default = disable).'
                choices:
                    - 'disable'
                    - 'enable'
            multicast-rate:
                type: str
                description: 'Multicast rate (0, 6000, 12000, or 24000 kbps, default = 0).'
                choices:
                    - '0'
                    - '6000'
                    - '12000'
                    - '24000'
            okc:
                type: str
                description: 'Enable/disable Opportunistic Key Caching (OKC) (default = enable).'
                choices:
                    - 'disable'
                    - 'enable'
            owe-groups:
                description: no description
                type: list
                choices:
                 - 19
                 - 20
                 - 21
            owe-transition:
                type: str
                description: 'Enable/disable OWE transition mode support.'
                choices:
                    - 'disable'
                    - 'enable'
            owe-transition-ssid:
                type: str
                description: 'OWE transition mode peer SSID.'
            passphrase:
                description: no description
                type: str
            pmf:
                type: str
                description: 'Protected Management Frames (PMF) support (default = disable).'
                choices:
                    - 'disable'
                    - 'enable'
                    - 'optional'
            pmf-assoc-comeback-timeout:
                type: int
                description: 'Protected Management Frames (PMF) comeback maximum timeout (1-20 sec).'
            pmf-sa-query-retry-timeout:
                type: int
                description: 'Protected Management Frames (PMF) SA query retry timeout interval (1 - 5 100s of msec).'
            portal-message-override-group:
                type: str
                description: 'Replacement message group for this VAP (only available when security is set to a captive portal type).'
            portal-type:
                type: str
                description: 'Captive portal functionality. Configure how the captive portal authenticates users and whether it includes a disclaimer.'
                choices:
                    - 'auth'
                    - 'auth+disclaimer'
                    - 'disclaimer'
                    - 'email-collect'
                    - 'cmcc'
                    - 'cmcc-macauth'
                    - 'auth-mac'
                    - 'external-auth'
                    - 'external-macauth'
            probe-resp-suppression:
                type: str
                description: 'Enable/disable probe response suppression (to ignore weak signals) (default = disable).'
                choices:
                    - 'disable'
                    - 'enable'
            probe-resp-threshold:
                type: str
                description: 'Minimum signal level/threshold in dBm required for the AP response to probe requests (-95 to -20, default = -80).'
            ptk-rekey:
                type: str
                description: 'Enable/disable PTK rekey for WPA-Enterprise security.'
                choices:
                    - 'disable'
                    - 'enable'
            ptk-rekey-intv:
                type: int
                description: 'PTK rekey interval (1800 - 864000 sec, default = 86400).'
            qos-profile:
                type: str
                description: 'Quality of service profile name.'
            quarantine:
                type: str
                description: 'Enable/disable station quarantine (default = enable).'
                choices:
                    - 'disable'
                    - 'enable'
            radio-2g-threshold:
                type: str
                description: 'Minimum signal level/threshold in dBm required for the AP response to receive a packet in 2.4G band (-95 to -20, default = -79).'
            radio-5g-threshold:
                type: str
                description: 'Minimum signal level/threshold in dBm required for the AP response to receive a packet in 5G band(-95 to -20, default = -76).'
            radio-sensitivity:
                type: str
                description: 'Enable/disable software radio sensitivity (to ignore weak signals) (default = disable).'
                choices:
                    - 'disable'
                    - 'enable'
            radius-mac-auth:
                type: str
                description: 'Enable/disable RADIUS-based MAC authentication of clients (default = disable).'
                choices:
                    - 'disable'
                    - 'enable'
            radius-mac-auth-server:
                type: str
                description: 'RADIUS-based MAC authentication server.'
            radius-mac-auth-usergroups:
                description: no description
                type: str
            radius-server:
                type: str
                description: 'RADIUS server to be used to authenticate WiFi users.'
            rates-11a:
                description: no description
                type: list
                choices:
                 - 1
                 - 1-basic
                 - 2
                 - 2-basic
                 - 5.5
                 - 5.5-basic
                 - 6
                 - 6-basic
                 - 9
                 - 9-basic
                 - 12
                 - 12-basic
                 - 18
                 - 18-basic
                 - 24
                 - 24-basic
                 - 36
                 - 36-basic
                 - 48
                 - 48-basic
                 - 54
                 - 54-basic
                 - 11
                 - 11-basic
            rates-11ac-ss12:
                description: no description
                type: list
                choices:
                 - mcs0/1
                 - mcs1/1
                 - mcs2/1
                 - mcs3/1
                 - mcs4/1
                 - mcs5/1
                 - mcs6/1
                 - mcs7/1
                 - mcs8/1
                 - mcs9/1
                 - mcs0/2
                 - mcs1/2
                 - mcs2/2
                 - mcs3/2
                 - mcs4/2
                 - mcs5/2
                 - mcs6/2
                 - mcs7/2
                 - mcs8/2
                 - mcs9/2
                 - mcs10/1
                 - mcs11/1
                 - mcs10/2
                 - mcs11/2
            rates-11ac-ss34:
                description: no description
                type: list
                choices:
                 - mcs0/3
                 - mcs1/3
                 - mcs2/3
                 - mcs3/3
                 - mcs4/3
                 - mcs5/3
                 - mcs6/3
                 - mcs7/3
                 - mcs8/3
                 - mcs9/3
                 - mcs0/4
                 - mcs1/4
                 - mcs2/4
                 - mcs3/4
                 - mcs4/4
                 - mcs5/4
                 - mcs6/4
                 - mcs7/4
                 - mcs8/4
                 - mcs9/4
                 - mcs10/3
                 - mcs11/3
                 - mcs10/4
                 - mcs11/4
            rates-11bg:
                description: no description
                type: list
                choices:
                 - 1
                 - 1-basic
                 - 2
                 - 2-basic
                 - 5.5
                 - 5.5-basic
                 - 6
                 - 6-basic
                 - 9
                 - 9-basic
                 - 12
                 - 12-basic
                 - 18
                 - 18-basic
                 - 24
                 - 24-basic
                 - 36
                 - 36-basic
                 - 48
                 - 48-basic
                 - 54
                 - 54-basic
                 - 11
                 - 11-basic
            rates-11n-ss12:
                description: no description
                type: list
                choices:
                 - mcs0/1
                 - mcs1/1
                 - mcs2/1
                 - mcs3/1
                 - mcs4/1
                 - mcs5/1
                 - mcs6/1
                 - mcs7/1
                 - mcs8/2
                 - mcs9/2
                 - mcs10/2
                 - mcs11/2
                 - mcs12/2
                 - mcs13/2
                 - mcs14/2
                 - mcs15/2
            rates-11n-ss34:
                description: no description
                type: list
                choices:
                 - mcs16/3
                 - mcs17/3
                 - mcs18/3
                 - mcs19/3
                 - mcs20/3
                 - mcs21/3
                 - mcs22/3
                 - mcs23/3
                 - mcs24/4
                 - mcs25/4
                 - mcs26/4
                 - mcs27/4
                 - mcs28/4
                 - mcs29/4
                 - mcs30/4
                 - mcs31/4
            sae-groups:
                description: no description
                type: list
                choices:
                 - 1
                 - 2
                 - 5
                 - 14
                 - 15
                 - 16
                 - 17
                 - 18
                 - 19
                 - 20
                 - 21
                 - 27
                 - 28
                 - 29
                 - 30
                 - 31
            sae-password:
                description: no description
                type: str
            schedule:
                type: str
                description: 'Firewall schedules for enabling this VAP on the FortiAP. This VAP will be enabled when at least one of the schedules is valid....'
            security:
                type: str
                description: 'Security mode for the wireless interface (default = wpa2-only-personal).'
                choices:
                    - 'None'
                    - 'WEP64'
                    - 'wep64'
                    - 'WEP128'
                    - 'wep128'
                    - 'WPA_PSK'
                    - 'WPA_RADIUS'
                    - 'WPA'
                    - 'WPA2'
                    - 'WPA2_AUTO'
                    - 'open'
                    - 'wpa-personal'
                    - 'wpa-enterprise'
                    - 'captive-portal'
                    - 'wpa-only-personal'
                    - 'wpa-only-enterprise'
                    - 'wpa2-only-personal'
                    - 'wpa2-only-enterprise'
                    - 'wpa-personal+captive-portal'
                    - 'wpa-only-personal+captive-portal'
                    - 'wpa2-only-personal+captive-portal'
                    - 'osen'
                    - 'wpa3-enterprise'
                    - 'sae'
                    - 'sae-transition'
                    - 'owe'
                    - 'wpa3-sae'
                    - 'wpa3-sae-transition'
                    - 'wpa3-only-enterprise'
                    - 'wpa3-enterprise-transition'
            security-exempt-list:
                type: str
                description: 'Optional security exempt list for captive portal authentication.'
            security-obsolete-option:
                type: str
                description: 'Enable/disable obsolete security options.'
                choices:
                    - 'disable'
                    - 'enable'
            security-redirect-url:
                type: str
                description: 'Optional URL for redirecting users after they pass captive portal authentication.'
            selected-usergroups:
                type: str
                description: 'Selective user groups that are permitted to authenticate.'
            split-tunneling:
                type: str
                description: 'Enable/disable split tunneling (default = disable).'
                choices:
                    - 'disable'
                    - 'enable'
            ssid:
                type: str
                description: 'IEEE 802.11 service set identifier (SSID) for the wireless interface. Users who wish to use the wireless network must configur...'
            tkip-counter-measure:
                type: str
                description: 'Enable/disable TKIP counter measure.'
                choices:
                    - 'disable'
                    - 'enable'
            usergroup:
                type: str
                description: 'Firewall user group to be used to authenticate WiFi users.'
            utm-profile:
                type: str
                description: 'UTM profile name.'
            vdom:
                type: str
                description: 'Vdom.'
            vlan-auto:
                type: str
                description: 'Enable/disable automatic management of SSID VLAN interface.'
                choices:
                    - 'disable'
                    - 'enable'
            vlan-pooling:
                type: str
                description: 'Enable/disable VLAN pooling, to allow grouping of multiple wireless controller VLANs into VLAN pools (default = disable). When...'
                choices:
                    - 'wtp-group'
                    - 'round-robin'
                    - 'hash'
                    - 'disable'
            vlanid:
                type: int
                description: 'Optional VLAN ID.'
            voice-enterprise:
                type: str
                description: 'Enable/disable 802.11k and 802.11v assisted Voice-Enterprise roaming (default = disable).'
                choices:
                    - 'disable'
                    - 'enable'
            mu-mimo:
                type: str
                description: 'Enable/disable Multi-user MIMO (default = enable).'
                choices:
                    - 'disable'
                    - 'enable'
            _intf_device-access-list:
                type: str
                description: '_Intf_Device-Access-List.'
            external-web-format:
                type: str
                description: 'URL query parameter detection (default = auto-detect).'
                choices:
                    - 'auto-detect'
                    - 'no-query-string'
                    - 'partial-query-string'
            high-efficiency:
                type: str
                description: 'Enable/disable 802.11ax high efficiency (default = enable).'
                choices:
                    - 'disable'
                    - 'enable'
            primary-wag-profile:
                type: str
                description: 'Primary wireless access gateway profile name.'
            secondary-wag-profile:
                type: str
                description: 'Secondary wireless access gateway profile name.'
            target-wake-time:
                type: str
                description: 'Enable/disable 802.11ax target wake time (default = enable).'
                choices:
                    - 'disable'
                    - 'enable'
            tunnel-echo-interval:
                type: int
                description: 'The time interval to send echo to both primary and secondary tunnel peers (1 - 65535 sec, default = 300).'
            tunnel-fallback-interval:
                type: int
                description: 'The time interval for secondary tunnel to fall back to primary tunnel (0 - 65535 sec, default = 7200).'
            access-control-list:
                type: str
                description: 'Access-Control-List.'
            captive-portal-auth-timeout:
                type: int
                description: 'Captive-Portal-Auth-Timeout.'
            ipv6-rules:
                description: no description
                type: list
                choices:
                 - drop-icmp6ra
                 - drop-icmp6rs
                 - drop-llmnr6
                 - drop-icmp6mld2
                 - drop-dhcp6s
                 - drop-dhcp6c
                 - ndp-proxy
                 - drop-ns-dad
                 - drop-ns-nondad
            sticky-client-remove:
                type: str
                description: 'Sticky-Client-Remove.'
                choices:
                    - 'disable'
                    - 'enable'
            sticky-client-threshold-2g:
                type: str
                description: 'Sticky-Client-Threshold-2G.'
            sticky-client-threshold-5g:
                type: str
                description: 'Sticky-Client-Threshold-5G.'
            bss-color-partial:
                type: str
                description: 'Bss-Color-Partial.'
                choices:
                    - 'disable'
                    - 'enable'
            dhcp-option43-insertion:
                type: str
                description: 'Dhcp-Option43-Insertion.'
                choices:
                    - 'disable'
                    - 'enable'
            mpsk-profile:
                type: str
                description: 'Mpsk-Profile.'
            igmp-snooping:
                type: str
                description: 'Enable/disable IGMP snooping.'
                choices:
                    - 'disable'
                    - 'enable'
            port-macauth:
                type: str
                description: 'Enable/disable LAN port MAC authentication (default = disable).'
                choices:
                    - 'disable'
                    - 'radius'
                    - 'address-group'
            port-macauth-reauth-timeout:
                type: int
                description: 'LAN port MAC authentication re-authentication timeout value (default = 7200 sec).'
            port-macauth-timeout:
                type: int
                description: 'LAN port MAC authentication idle timeout value (default = 600 sec).'
            additional-akms:
                description: no description
                type: list
                choices:
                 - akm6
            bstm-disassociation-imminent:
                type: str
                description: 'Enable/disable forcing of disassociation after the BSTM request timer has been reached (default = enable).'
                choices:
                    - 'disable'
                    - 'enable'
            bstm-load-balancing-disassoc-timer:
                type: int
                description: 'Time interval for client to voluntarily leave AP before forcing a disassociation due to AP load-balancing (0 to 30, default = ...'
            bstm-rssi-disassoc-timer:
                type: int
                description: 'Time interval for client to voluntarily leave AP before forcing a disassociation due to low RSSI (0 to 2000, default = 200).'
            dhcp-address-enforcement:
                type: str
                description: 'Enable/disable DHCP address enforcement (default = disable).'
                choices:
                    - 'disable'
                    - 'enable'
            gas-comeback-delay:
                type: int
                description: 'GAS comeback delay (0 or 100 - 10000 milliseconds, default = 500).'
            gas-fragmentation-limit:
                type: int
                description: 'GAS fragmentation limit (512 - 4096, default = 1024).'
            mac-called-station-delimiter:
                type: str
                description: 'MAC called station delimiter (default = hyphen).'
                choices:
                    - 'hyphen'
                    - 'single-hyphen'
                    - 'colon'
                    - 'none'
            mac-calling-station-delimiter:
                type: str
                description: 'MAC calling station delimiter (default = hyphen).'
                choices:
                    - 'hyphen'
                    - 'single-hyphen'
                    - 'colon'
                    - 'none'
            mac-case:
                type: str
                description: 'MAC case (default = uppercase).'
                choices:
                    - 'uppercase'
                    - 'lowercase'
            mac-password-delimiter:
                type: str
                description: 'MAC authentication password delimiter (default = hyphen).'
                choices:
                    - 'hyphen'
                    - 'single-hyphen'
                    - 'colon'
                    - 'none'
            mac-username-delimiter:
                type: str
                description: 'MAC authentication username delimiter (default = hyphen).'
                choices:
                    - 'hyphen'
                    - 'single-hyphen'
                    - 'colon'
                    - 'none'
            mbo:
                type: str
                description: 'Enable/disable Multiband Operation (default = disable).'
                choices:
                    - 'disable'
                    - 'enable'
            mbo-cell-data-conn-pref:
                type: str
                description: 'MBO cell data connection preference (0, 1, or 255, default = 1).'
                choices:
                    - 'excluded'
                    - 'prefer-not'
                    - 'prefer-use'
            nac:
                type: str
                description: 'Enable/disable network access control.'
                choices:
                    - 'disable'
                    - 'enable'
            nac-profile:
                type: str
                description: 'NAC profile name.'
            neighbor-report-dual-band:
                type: str
                description: 'Enable/disable dual-band neighbor report (default = disable).'
                choices:
                    - 'disable'
                    - 'enable'

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
    - name: Configure Virtual Access Points
      fmgr_vap_dynamicmapping:
         bypass_validation: False
         workspace_locking_adom: <value in [global, custom adom including root]>
         workspace_locking_timeout: 300
         rc_succeeded: [0, -2, -3, ...]
         rc_failed: [-2, -3, ...]
         adom: <your own value>
         vap: <your own value>
         state: <value in [present, absent]>
         vap_dynamicmapping:
            _centmgmt: <value in [disable, enable]>
            _dhcp_svr_id: <value of string>
            _intf_allowaccess:
              - https
              - ping
              - ssh
              - snmp
              - http
              - telnet
              - fgfm
              - auto-ipsec
              - radius-acct
              - probe-response
              - capwap
            _intf_device-identification: <value in [disable, enable]>
            _intf_device-netscan: <value in [disable, enable]>
            _intf_dhcp-relay-ip: <value of string>
            _intf_dhcp-relay-service: <value in [disable, enable]>
            _intf_dhcp-relay-type: <value in [regular, ipsec]>
            _intf_dhcp6-relay-ip: <value of string>
            _intf_dhcp6-relay-service: <value in [disable, enable]>
            _intf_dhcp6-relay-type: <value in [regular]>
            _intf_ip: <value of string>
            _intf_ip6-address: <value of string>
            _intf_ip6-allowaccess:
              - https
              - ping
              - ssh
              - snmp
              - http
              - telnet
              - any
              - fgfm
              - capwap
            _intf_listen-forticlient-connection: <value in [disable, enable]>
            _scope:
              -
                  name: <value of string>
                  vdom: <value of string>
            acct-interim-interval: <value of integer>
            address-group: <value of string>
            alias: <value of string>
            atf-weight: <value of integer>
            auth: <value in [PSK, psk, RADIUS, ...]>
            broadcast-ssid: <value in [disable, enable]>
            broadcast-suppression:
              - dhcp
              - arp
              - dhcp2
              - arp2
              - netbios-ns
              - netbios-ds
              - arp3
              - dhcp-up
              - dhcp-down
              - arp-known
              - arp-unknown
              - arp-reply
              - ipv6
              - dhcp-starvation
              - arp-poison
              - all-other-mc
              - all-other-bc
              - arp-proxy
              - dhcp-ucast
            captive-portal-ac-name: <value of string>
            captive-portal-macauth-radius-secret: <value of string>
            captive-portal-macauth-radius-server: <value of string>
            captive-portal-radius-secret: <value of string>
            captive-portal-radius-server: <value of string>
            captive-portal-session-timeout-interval: <value of integer>
            client-count: <value of integer>
            dhcp-lease-time: <value of integer>
            dhcp-option82-circuit-id-insertion: <value in [disable, style-1, style-2, ...]>
            dhcp-option82-insertion: <value in [disable, enable]>
            dhcp-option82-remote-id-insertion: <value in [disable, style-1]>
            dynamic-vlan: <value in [disable, enable]>
            eap-reauth: <value in [disable, enable]>
            eap-reauth-intv: <value of integer>
            eapol-key-retries: <value in [disable, enable]>
            encrypt: <value in [TKIP, AES, TKIP-AES]>
            external-fast-roaming: <value in [disable, enable]>
            external-logout: <value of string>
            external-web: <value of string>
            fast-bss-transition: <value in [disable, enable]>
            fast-roaming: <value in [disable, enable]>
            ft-mobility-domain: <value of integer>
            ft-over-ds: <value in [disable, enable]>
            ft-r0-key-lifetime: <value of integer>
            gtk-rekey: <value in [disable, enable]>
            gtk-rekey-intv: <value of integer>
            hotspot20-profile: <value of string>
            intra-vap-privacy: <value in [disable, enable]>
            ip: <value of string>
            key: <value of string>
            keyindex: <value of integer>
            ldpc: <value in [disable, tx, rx, ...]>
            local-authentication: <value in [disable, enable]>
            local-bridging: <value in [disable, enable]>
            local-lan: <value in [deny, allow]>
            local-standalone: <value in [disable, enable]>
            local-standalone-nat: <value in [disable, enable]>
            local-switching: <value in [disable, enable]>
            mac-auth-bypass: <value in [disable, enable]>
            mac-filter: <value in [disable, enable]>
            mac-filter-policy-other: <value in [deny, allow]>
            max-clients: <value of integer>
            max-clients-ap: <value of integer>
            me-disable-thresh: <value of integer>
            mesh-backhaul: <value in [disable, enable]>
            mpsk: <value in [disable, enable]>
            mpsk-concurrent-clients: <value of integer>
            multicast-enhance: <value in [disable, enable]>
            multicast-rate: <value in [0, 6000, 12000, ...]>
            okc: <value in [disable, enable]>
            owe-groups:
              - 19
              - 20
              - 21
            owe-transition: <value in [disable, enable]>
            owe-transition-ssid: <value of string>
            passphrase: <value of string>
            pmf: <value in [disable, enable, optional]>
            pmf-assoc-comeback-timeout: <value of integer>
            pmf-sa-query-retry-timeout: <value of integer>
            portal-message-override-group: <value of string>
            portal-type: <value in [auth, auth+disclaimer, disclaimer, ...]>
            probe-resp-suppression: <value in [disable, enable]>
            probe-resp-threshold: <value of string>
            ptk-rekey: <value in [disable, enable]>
            ptk-rekey-intv: <value of integer>
            qos-profile: <value of string>
            quarantine: <value in [disable, enable]>
            radio-2g-threshold: <value of string>
            radio-5g-threshold: <value of string>
            radio-sensitivity: <value in [disable, enable]>
            radius-mac-auth: <value in [disable, enable]>
            radius-mac-auth-server: <value of string>
            radius-mac-auth-usergroups: <value of string>
            radius-server: <value of string>
            rates-11a:
              - 1
              - 1-basic
              - 2
              - 2-basic
              - 5.5
              - 5.5-basic
              - 6
              - 6-basic
              - 9
              - 9-basic
              - 12
              - 12-basic
              - 18
              - 18-basic
              - 24
              - 24-basic
              - 36
              - 36-basic
              - 48
              - 48-basic
              - 54
              - 54-basic
              - 11
              - 11-basic
            rates-11ac-ss12:
              - mcs0/1
              - mcs1/1
              - mcs2/1
              - mcs3/1
              - mcs4/1
              - mcs5/1
              - mcs6/1
              - mcs7/1
              - mcs8/1
              - mcs9/1
              - mcs0/2
              - mcs1/2
              - mcs2/2
              - mcs3/2
              - mcs4/2
              - mcs5/2
              - mcs6/2
              - mcs7/2
              - mcs8/2
              - mcs9/2
              - mcs10/1
              - mcs11/1
              - mcs10/2
              - mcs11/2
            rates-11ac-ss34:
              - mcs0/3
              - mcs1/3
              - mcs2/3
              - mcs3/3
              - mcs4/3
              - mcs5/3
              - mcs6/3
              - mcs7/3
              - mcs8/3
              - mcs9/3
              - mcs0/4
              - mcs1/4
              - mcs2/4
              - mcs3/4
              - mcs4/4
              - mcs5/4
              - mcs6/4
              - mcs7/4
              - mcs8/4
              - mcs9/4
              - mcs10/3
              - mcs11/3
              - mcs10/4
              - mcs11/4
            rates-11bg:
              - 1
              - 1-basic
              - 2
              - 2-basic
              - 5.5
              - 5.5-basic
              - 6
              - 6-basic
              - 9
              - 9-basic
              - 12
              - 12-basic
              - 18
              - 18-basic
              - 24
              - 24-basic
              - 36
              - 36-basic
              - 48
              - 48-basic
              - 54
              - 54-basic
              - 11
              - 11-basic
            rates-11n-ss12:
              - mcs0/1
              - mcs1/1
              - mcs2/1
              - mcs3/1
              - mcs4/1
              - mcs5/1
              - mcs6/1
              - mcs7/1
              - mcs8/2
              - mcs9/2
              - mcs10/2
              - mcs11/2
              - mcs12/2
              - mcs13/2
              - mcs14/2
              - mcs15/2
            rates-11n-ss34:
              - mcs16/3
              - mcs17/3
              - mcs18/3
              - mcs19/3
              - mcs20/3
              - mcs21/3
              - mcs22/3
              - mcs23/3
              - mcs24/4
              - mcs25/4
              - mcs26/4
              - mcs27/4
              - mcs28/4
              - mcs29/4
              - mcs30/4
              - mcs31/4
            sae-groups:
              - 1
              - 2
              - 5
              - 14
              - 15
              - 16
              - 17
              - 18
              - 19
              - 20
              - 21
              - 27
              - 28
              - 29
              - 30
              - 31
            sae-password: <value of string>
            schedule: <value of string>
            security: <value in [None, WEP64, wep64, ...]>
            security-exempt-list: <value of string>
            security-obsolete-option: <value in [disable, enable]>
            security-redirect-url: <value of string>
            selected-usergroups: <value of string>
            split-tunneling: <value in [disable, enable]>
            ssid: <value of string>
            tkip-counter-measure: <value in [disable, enable]>
            usergroup: <value of string>
            utm-profile: <value of string>
            vdom: <value of string>
            vlan-auto: <value in [disable, enable]>
            vlan-pooling: <value in [wtp-group, round-robin, hash, ...]>
            vlanid: <value of integer>
            voice-enterprise: <value in [disable, enable]>
            mu-mimo: <value in [disable, enable]>
            _intf_device-access-list: <value of string>
            external-web-format: <value in [auto-detect, no-query-string, partial-query-string]>
            high-efficiency: <value in [disable, enable]>
            primary-wag-profile: <value of string>
            secondary-wag-profile: <value of string>
            target-wake-time: <value in [disable, enable]>
            tunnel-echo-interval: <value of integer>
            tunnel-fallback-interval: <value of integer>
            access-control-list: <value of string>
            captive-portal-auth-timeout: <value of integer>
            ipv6-rules:
              - drop-icmp6ra
              - drop-icmp6rs
              - drop-llmnr6
              - drop-icmp6mld2
              - drop-dhcp6s
              - drop-dhcp6c
              - ndp-proxy
              - drop-ns-dad
              - drop-ns-nondad
            sticky-client-remove: <value in [disable, enable]>
            sticky-client-threshold-2g: <value of string>
            sticky-client-threshold-5g: <value of string>
            bss-color-partial: <value in [disable, enable]>
            dhcp-option43-insertion: <value in [disable, enable]>
            mpsk-profile: <value of string>
            igmp-snooping: <value in [disable, enable]>
            port-macauth: <value in [disable, radius, address-group]>
            port-macauth-reauth-timeout: <value of integer>
            port-macauth-timeout: <value of integer>
            additional-akms:
              - akm6
            bstm-disassociation-imminent: <value in [disable, enable]>
            bstm-load-balancing-disassoc-timer: <value of integer>
            bstm-rssi-disassoc-timer: <value of integer>
            dhcp-address-enforcement: <value in [disable, enable]>
            gas-comeback-delay: <value of integer>
            gas-fragmentation-limit: <value of integer>
            mac-called-station-delimiter: <value in [hyphen, single-hyphen, colon, ...]>
            mac-calling-station-delimiter: <value in [hyphen, single-hyphen, colon, ...]>
            mac-case: <value in [uppercase, lowercase]>
            mac-password-delimiter: <value in [hyphen, single-hyphen, colon, ...]>
            mac-username-delimiter: <value in [hyphen, single-hyphen, colon, ...]>
            mbo: <value in [disable, enable]>
            mbo-cell-data-conn-pref: <value in [excluded, prefer-not, prefer-use]>
            nac: <value in [disable, enable]>
            nac-profile: <value of string>
            neighbor-report-dual-band: <value in [disable, enable]>

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
        '/pm/config/adom/{adom}/obj/wireless-controller/vap/{vap}/dynamic_mapping',
        '/pm/config/global/obj/wireless-controller/vap/{vap}/dynamic_mapping'
    ]

    perobject_jrpc_urls = [
        '/pm/config/adom/{adom}/obj/wireless-controller/vap/{vap}/dynamic_mapping/{dynamic_mapping}',
        '/pm/config/global/obj/wireless-controller/vap/{vap}/dynamic_mapping/{dynamic_mapping}'
    ]

    url_params = ['adom', 'vap']
    module_primary_key = 'complex:{{module}}["_scope"][0]["name"]+"/"+{{module}}["_scope"][0]["vdom"]'
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
        'state': {
            'type': 'str',
            'required': True,
            'choices': [
                'present',
                'absent'
            ]
        },
        'adom': {
            'required': True,
            'type': 'str'
        },
        'vap': {
            'required': True,
            'type': 'str'
        },
        'vap_dynamicmapping': {
            'required': False,
            'type': 'dict',
            'revision': {
                '6.0.0': True,
                '6.2.1': True,
                '6.2.3': True,
                '6.2.5': True,
                '6.4.0': True,
                '6.4.2': True,
                '6.4.5': True,
                '7.0.0': True
            },
            'options': {
                '_centmgmt': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                '_dhcp_svr_id': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                '_intf_allowaccess': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'choices': [
                        'https',
                        'ping',
                        'ssh',
                        'snmp',
                        'http',
                        'telnet',
                        'fgfm',
                        'auto-ipsec',
                        'radius-acct',
                        'probe-response',
                        'capwap'
                    ]
                },
                '_intf_device-identification': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                '_intf_device-netscan': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                '_intf_dhcp-relay-ip': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                '_intf_dhcp-relay-service': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                '_intf_dhcp-relay-type': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'regular',
                        'ipsec'
                    ],
                    'type': 'str'
                },
                '_intf_dhcp6-relay-ip': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                '_intf_dhcp6-relay-service': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                '_intf_dhcp6-relay-type': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'regular'
                    ],
                    'type': 'str'
                },
                '_intf_ip': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                '_intf_ip6-address': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                '_intf_ip6-allowaccess': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'choices': [
                        'https',
                        'ping',
                        'ssh',
                        'snmp',
                        'http',
                        'telnet',
                        'any',
                        'fgfm',
                        'capwap'
                    ]
                },
                '_intf_listen-forticlient-connection': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                '_scope': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'options': {
                        'name': {
                            'required': False,
                            'revision': {
                                '6.0.0': True,
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': True,
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'vdom': {
                            'required': False,
                            'revision': {
                                '6.0.0': True,
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': True,
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        }
                    }
                },
                'acct-interim-interval': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'address-group': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'alias': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'atf-weight': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'auth': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'PSK',
                        'psk',
                        'RADIUS',
                        'radius',
                        'usergroup'
                    ],
                    'type': 'str'
                },
                'broadcast-ssid': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'broadcast-suppression': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'choices': [
                        'dhcp',
                        'arp',
                        'dhcp2',
                        'arp2',
                        'netbios-ns',
                        'netbios-ds',
                        'arp3',
                        'dhcp-up',
                        'dhcp-down',
                        'arp-known',
                        'arp-unknown',
                        'arp-reply',
                        'ipv6',
                        'dhcp-starvation',
                        'arp-poison',
                        'all-other-mc',
                        'all-other-bc',
                        'arp-proxy',
                        'dhcp-ucast'
                    ]
                },
                'captive-portal-ac-name': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'captive-portal-macauth-radius-secret': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'captive-portal-macauth-radius-server': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'captive-portal-radius-secret': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'captive-portal-radius-server': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'captive-portal-session-timeout-interval': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'client-count': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'dhcp-lease-time': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'dhcp-option82-circuit-id-insertion': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'disable',
                        'style-1',
                        'style-2',
                        'style-3'
                    ],
                    'type': 'str'
                },
                'dhcp-option82-insertion': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'dhcp-option82-remote-id-insertion': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'disable',
                        'style-1'
                    ],
                    'type': 'str'
                },
                'dynamic-vlan': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'eap-reauth': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'eap-reauth-intv': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'eapol-key-retries': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'encrypt': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'TKIP',
                        'AES',
                        'TKIP-AES'
                    ],
                    'type': 'str'
                },
                'external-fast-roaming': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'external-logout': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'external-web': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'fast-bss-transition': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'fast-roaming': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'ft-mobility-domain': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'ft-over-ds': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'ft-r0-key-lifetime': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'gtk-rekey': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'gtk-rekey-intv': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'hotspot20-profile': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'intra-vap-privacy': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'ip': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'key': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'keyindex': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'ldpc': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'disable',
                        'tx',
                        'rx',
                        'rxtx'
                    ],
                    'type': 'str'
                },
                'local-authentication': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'local-bridging': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'local-lan': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'deny',
                        'allow'
                    ],
                    'type': 'str'
                },
                'local-standalone': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'local-standalone-nat': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'local-switching': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'mac-auth-bypass': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'mac-filter': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'mac-filter-policy-other': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'deny',
                        'allow'
                    ],
                    'type': 'str'
                },
                'max-clients': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'max-clients-ap': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'me-disable-thresh': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'mesh-backhaul': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'mpsk': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'mpsk-concurrent-clients': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'multicast-enhance': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'multicast-rate': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        '0',
                        '6000',
                        '12000',
                        '24000'
                    ],
                    'type': 'str'
                },
                'okc': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'owe-groups': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'choices': [
                        '19',
                        '20',
                        '21'
                    ]
                },
                'owe-transition': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'owe-transition-ssid': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'passphrase': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'pmf': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'disable',
                        'enable',
                        'optional'
                    ],
                    'type': 'str'
                },
                'pmf-assoc-comeback-timeout': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'pmf-sa-query-retry-timeout': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'portal-message-override-group': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'portal-type': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'auth',
                        'auth+disclaimer',
                        'disclaimer',
                        'email-collect',
                        'cmcc',
                        'cmcc-macauth',
                        'auth-mac',
                        'external-auth',
                        'external-macauth'
                    ],
                    'type': 'str'
                },
                'probe-resp-suppression': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'probe-resp-threshold': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'ptk-rekey': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'ptk-rekey-intv': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'qos-profile': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'quarantine': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'radio-2g-threshold': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'radio-5g-threshold': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'radio-sensitivity': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'radius-mac-auth': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'radius-mac-auth-server': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'radius-mac-auth-usergroups': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'radius-server': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'rates-11a': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'choices': [
                        '1',
                        '1-basic',
                        '2',
                        '2-basic',
                        '5.5',
                        '5.5-basic',
                        '6',
                        '6-basic',
                        '9',
                        '9-basic',
                        '12',
                        '12-basic',
                        '18',
                        '18-basic',
                        '24',
                        '24-basic',
                        '36',
                        '36-basic',
                        '48',
                        '48-basic',
                        '54',
                        '54-basic',
                        '11',
                        '11-basic'
                    ]
                },
                'rates-11ac-ss12': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'choices': [
                        'mcs0/1',
                        'mcs1/1',
                        'mcs2/1',
                        'mcs3/1',
                        'mcs4/1',
                        'mcs5/1',
                        'mcs6/1',
                        'mcs7/1',
                        'mcs8/1',
                        'mcs9/1',
                        'mcs0/2',
                        'mcs1/2',
                        'mcs2/2',
                        'mcs3/2',
                        'mcs4/2',
                        'mcs5/2',
                        'mcs6/2',
                        'mcs7/2',
                        'mcs8/2',
                        'mcs9/2',
                        'mcs10/1',
                        'mcs11/1',
                        'mcs10/2',
                        'mcs11/2'
                    ]
                },
                'rates-11ac-ss34': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'choices': [
                        'mcs0/3',
                        'mcs1/3',
                        'mcs2/3',
                        'mcs3/3',
                        'mcs4/3',
                        'mcs5/3',
                        'mcs6/3',
                        'mcs7/3',
                        'mcs8/3',
                        'mcs9/3',
                        'mcs0/4',
                        'mcs1/4',
                        'mcs2/4',
                        'mcs3/4',
                        'mcs4/4',
                        'mcs5/4',
                        'mcs6/4',
                        'mcs7/4',
                        'mcs8/4',
                        'mcs9/4',
                        'mcs10/3',
                        'mcs11/3',
                        'mcs10/4',
                        'mcs11/4'
                    ]
                },
                'rates-11bg': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'choices': [
                        '1',
                        '1-basic',
                        '2',
                        '2-basic',
                        '5.5',
                        '5.5-basic',
                        '6',
                        '6-basic',
                        '9',
                        '9-basic',
                        '12',
                        '12-basic',
                        '18',
                        '18-basic',
                        '24',
                        '24-basic',
                        '36',
                        '36-basic',
                        '48',
                        '48-basic',
                        '54',
                        '54-basic',
                        '11',
                        '11-basic'
                    ]
                },
                'rates-11n-ss12': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'choices': [
                        'mcs0/1',
                        'mcs1/1',
                        'mcs2/1',
                        'mcs3/1',
                        'mcs4/1',
                        'mcs5/1',
                        'mcs6/1',
                        'mcs7/1',
                        'mcs8/2',
                        'mcs9/2',
                        'mcs10/2',
                        'mcs11/2',
                        'mcs12/2',
                        'mcs13/2',
                        'mcs14/2',
                        'mcs15/2'
                    ]
                },
                'rates-11n-ss34': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'choices': [
                        'mcs16/3',
                        'mcs17/3',
                        'mcs18/3',
                        'mcs19/3',
                        'mcs20/3',
                        'mcs21/3',
                        'mcs22/3',
                        'mcs23/3',
                        'mcs24/4',
                        'mcs25/4',
                        'mcs26/4',
                        'mcs27/4',
                        'mcs28/4',
                        'mcs29/4',
                        'mcs30/4',
                        'mcs31/4'
                    ]
                },
                'sae-groups': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'choices': [
                        '1',
                        '2',
                        '5',
                        '14',
                        '15',
                        '16',
                        '17',
                        '18',
                        '19',
                        '20',
                        '21',
                        '27',
                        '28',
                        '29',
                        '30',
                        '31'
                    ]
                },
                'sae-password': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'schedule': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'security': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'None',
                        'WEP64',
                        'wep64',
                        'WEP128',
                        'wep128',
                        'WPA_PSK',
                        'WPA_RADIUS',
                        'WPA',
                        'WPA2',
                        'WPA2_AUTO',
                        'open',
                        'wpa-personal',
                        'wpa-enterprise',
                        'captive-portal',
                        'wpa-only-personal',
                        'wpa-only-enterprise',
                        'wpa2-only-personal',
                        'wpa2-only-enterprise',
                        'wpa-personal+captive-portal',
                        'wpa-only-personal+captive-portal',
                        'wpa2-only-personal+captive-portal',
                        'osen',
                        'wpa3-enterprise',
                        'sae',
                        'sae-transition',
                        'owe',
                        'wpa3-sae',
                        'wpa3-sae-transition',
                        'wpa3-only-enterprise',
                        'wpa3-enterprise-transition'
                    ],
                    'type': 'str'
                },
                'security-exempt-list': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'security-obsolete-option': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'security-redirect-url': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'selected-usergroups': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'split-tunneling': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'ssid': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'tkip-counter-measure': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'usergroup': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'utm-profile': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'vdom': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'vlan-auto': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'vlan-pooling': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'wtp-group',
                        'round-robin',
                        'hash',
                        'disable'
                    ],
                    'type': 'str'
                },
                'vlanid': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'voice-enterprise': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'mu-mimo': {
                    'required': False,
                    'revision': {
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                '_intf_device-access-list': {
                    'required': False,
                    'revision': {
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'external-web-format': {
                    'required': False,
                    'revision': {
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'auto-detect',
                        'no-query-string',
                        'partial-query-string'
                    ],
                    'type': 'str'
                },
                'high-efficiency': {
                    'required': False,
                    'revision': {
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'primary-wag-profile': {
                    'required': False,
                    'revision': {
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'secondary-wag-profile': {
                    'required': False,
                    'revision': {
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'target-wake-time': {
                    'required': False,
                    'revision': {
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
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
                'tunnel-echo-interval': {
                    'required': False,
                    'revision': {
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'tunnel-fallback-interval': {
                    'required': False,
                    'revision': {
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'access-control-list': {
                    'required': False,
                    'revision': {
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'captive-portal-auth-timeout': {
                    'required': False,
                    'revision': {
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'ipv6-rules': {
                    'required': False,
                    'revision': {
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'choices': [
                        'drop-icmp6ra',
                        'drop-icmp6rs',
                        'drop-llmnr6',
                        'drop-icmp6mld2',
                        'drop-dhcp6s',
                        'drop-dhcp6c',
                        'ndp-proxy',
                        'drop-ns-dad',
                        'drop-ns-nondad'
                    ]
                },
                'sticky-client-remove': {
                    'required': False,
                    'revision': {
                        '6.4.0': True,
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
                'sticky-client-threshold-2g': {
                    'required': False,
                    'revision': {
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'sticky-client-threshold-5g': {
                    'required': False,
                    'revision': {
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'bss-color-partial': {
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
                'dhcp-option43-insertion': {
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
                'mpsk-profile': {
                    'required': False,
                    'revision': {
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'igmp-snooping': {
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
                },
                'port-macauth': {
                    'required': False,
                    'revision': {
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'disable',
                        'radius',
                        'address-group'
                    ],
                    'type': 'str'
                },
                'port-macauth-reauth-timeout': {
                    'required': False,
                    'revision': {
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'port-macauth-timeout': {
                    'required': False,
                    'revision': {
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'additional-akms': {
                    'required': False,
                    'revision': {
                        '7.0.0': True
                    },
                    'type': 'list',
                    'choices': [
                        'akm6'
                    ]
                },
                'bstm-disassociation-imminent': {
                    'required': False,
                    'revision': {
                        '7.0.0': True
                    },
                    'choices': [
                        'disable',
                        'enable'
                    ],
                    'type': 'str'
                },
                'bstm-load-balancing-disassoc-timer': {
                    'required': False,
                    'revision': {
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'bstm-rssi-disassoc-timer': {
                    'required': False,
                    'revision': {
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'dhcp-address-enforcement': {
                    'required': False,
                    'revision': {
                        '7.0.0': True
                    },
                    'choices': [
                        'disable',
                        'enable'
                    ],
                    'type': 'str'
                },
                'gas-comeback-delay': {
                    'required': False,
                    'revision': {
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'gas-fragmentation-limit': {
                    'required': False,
                    'revision': {
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'mac-called-station-delimiter': {
                    'required': False,
                    'revision': {
                        '7.0.0': True
                    },
                    'choices': [
                        'hyphen',
                        'single-hyphen',
                        'colon',
                        'none'
                    ],
                    'type': 'str'
                },
                'mac-calling-station-delimiter': {
                    'required': False,
                    'revision': {
                        '7.0.0': True
                    },
                    'choices': [
                        'hyphen',
                        'single-hyphen',
                        'colon',
                        'none'
                    ],
                    'type': 'str'
                },
                'mac-case': {
                    'required': False,
                    'revision': {
                        '7.0.0': True
                    },
                    'choices': [
                        'uppercase',
                        'lowercase'
                    ],
                    'type': 'str'
                },
                'mac-password-delimiter': {
                    'required': False,
                    'revision': {
                        '7.0.0': True
                    },
                    'choices': [
                        'hyphen',
                        'single-hyphen',
                        'colon',
                        'none'
                    ],
                    'type': 'str'
                },
                'mac-username-delimiter': {
                    'required': False,
                    'revision': {
                        '7.0.0': True
                    },
                    'choices': [
                        'hyphen',
                        'single-hyphen',
                        'colon',
                        'none'
                    ],
                    'type': 'str'
                },
                'mbo': {
                    'required': False,
                    'revision': {
                        '7.0.0': True
                    },
                    'choices': [
                        'disable',
                        'enable'
                    ],
                    'type': 'str'
                },
                'mbo-cell-data-conn-pref': {
                    'required': False,
                    'revision': {
                        '7.0.0': True
                    },
                    'choices': [
                        'excluded',
                        'prefer-not',
                        'prefer-use'
                    ],
                    'type': 'str'
                },
                'nac': {
                    'required': False,
                    'revision': {
                        '7.0.0': True
                    },
                    'choices': [
                        'disable',
                        'enable'
                    ],
                    'type': 'str'
                },
                'nac-profile': {
                    'required': False,
                    'revision': {
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'neighbor-report-dual-band': {
                    'required': False,
                    'revision': {
                        '7.0.0': True
                    },
                    'choices': [
                        'disable',
                        'enable'
                    ],
                    'type': 'str'
                }
            }

        }
    }

    params_validation_blob = []
    check_galaxy_version(module_arg_spec)
    module = AnsibleModule(argument_spec=check_parameter_bypass(module_arg_spec, 'vap_dynamicmapping'),
                           supports_check_mode=False)

    fmgr = None
    if module._socket_path:
        connection = Connection(module._socket_path)
        connection.set_option('enable_log', module.params['enable_log'] if 'enable_log' in module.params else False)
        connection.set_option('forticloud_access_token',
                              module.params['forticloud_access_token'] if 'forticloud_access_token' in module.params else None)
        fmgr = NAPIManager(jrpc_urls, perobject_jrpc_urls, module_primary_key, url_params, module, connection, top_level_schema_name='data')
        fmgr.validate_parameters(params_validation_blob)
        fmgr.process_curd(argument_specs=module_arg_spec)
    else:
        module.fail_json(msg='MUST RUN IN HTTPAPI MODE')
    module.exit_json(meta=module.params)


if __name__ == '__main__':
    main()
