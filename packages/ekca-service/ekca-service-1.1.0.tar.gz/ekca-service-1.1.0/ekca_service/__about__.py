# -*- coding: utf-8 -*-
"""
Meta information about module package ekca_service
"""

import collections

VersionInfo = collections.namedtuple('VersionInfo', ('major', 'minor', 'micro'))
__version_info__ = VersionInfo(
    major=1,
    minor=1,
    micro=0,
)
__version__ = '.'.join(str(val) for val in __version_info__)
__author__ = u'Michael Stroeder'
__mail__ = u'michael@stroeder.com'
__copyright__ = u'(C) 2018-2021 by Michael Ströder <michael@stroeder.com>'
__license__ = 'Apache-2.0'

__all__ = [
    '__version_info__',
    '__version__',
    '__author__',
    '__mail__',
    '__license__',
    '__copyright__',
    'OTP_PLUGIN_NAMESPACE',
    'PASSWORD_PLUGIN_NAMESPACE',
]

# Constants for the names of the plugin name space packages
PLUGIN_NAMESPACE = 'ekca_service.plugins'
OTP_PLUGIN_NAMESPACE = PLUGIN_NAMESPACE + '.otp'
PASSWORD_PLUGIN_NAMESPACE = PLUGIN_NAMESPACE + '.password'
