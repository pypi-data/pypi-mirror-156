# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r'''
options:
    name_encoding:
        description:
            - How to encode names (DNS names, URIs, email addresses) in return values.
            - C(ignore) will use the encoding returned by the backend.
            - C(idna) will convert all labels of domain names to IDNA encoding.
              IDNA2008 will be preferred, and IDNA2003 will be used if IDNA2008 encoding fails.
            - C(unicode) will convert all labels of domain names to Unicode.
              IDNA2008 will be preferred, and IDNA2003 will be used if IDNA2008 decoding fails.
            - B(Note) that C(idna) and C(unicode) require the L(idna Python library,https://pypi.org/project/idna/) to be installed.
        type: str
        default: ignore
        choices:
            - ignore
            - idna
            - unicode
requirements:
    - If I(name_encoding) is set to another value than C(ignore), the L(idna Python library,https://pypi.org/project/idna/) needs to be installed.
'''
