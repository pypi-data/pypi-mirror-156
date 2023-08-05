# -*- coding: utf-8 -*-
"""
Default settings for ekca_service
"""

import logging
import os

from .srv import app

LOG_CONFIG = os.path.join(app.instance_path, 'ekca-stderr-logging.conf')

LOG_NAME = 'ekca_service'

# maximum byte size of incoming requests
MAX_CONTENT_LENGTH = 500

# number of proxy levels
# see https://werkzeug.palletsprojects.com/en/1.0.x/middleware/proxy_fix/
PROXY_LEVEL = 0

#---------------------------------------------------------------------------
# Validation parameters
#---------------------------------------------------------------------------

# regex pattern for restricting user names
VALID_USERNAME_REGEX = '^[a-z0-9_-]+$'

#---------------------------------------------------------------------------
# SSH-CA parameters
#---------------------------------------------------------------------------

# passphrase of CA's private key
SSH_CA_PASSPHRASE = ''

# full pathname of root directory where to store all CA data
SSH_CA_DIR = '/var/lib/ekca-ssh-ca'

# where to find the ssh-keygen executable
SSH_KEYGEN_CMD = '/usr/bin/ssh-keygen'

# cert validity period
SSH_CERT_VALIDITY = '+1h'

# minimum args used for ssh-keygen when generating a new keypair
SSH_GENCA_ARGS = [
    # generate RSA-4096 key pairs
    '-t', 'rsa',
    '-b', '4096',
    # no passphrase
    '-N', SSH_CA_PASSPHRASE,
    # no console output
    '-q',
]

# character length of generated SSH key passphrase
SSH_PASSPHRASE_LENGTH = 40

# alphabet used to generate SSH key passphrase
SSH_PASSPHRASE_ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

# additional args used when signing a user key
# see CLI arg -O in man-page ssh-keygen(1)
SSH_CERT_PERMISSIONS = [
    'pty',
#    'x11-forwarding',
#    'agent-forwarding',
#    'port-forwarding',
#    'user-rc',
]

# LDAP attribute from where to read the SSH key permissions for ssh-keygen -O
#SSH_CERT_PERMISSIONS_ATTR = None

# Where to get the user's client IP to be added as cert option
# from the HTTP request's remote address attribute
#SSH_FROMIP_METHOD = 'request.remote_addr'
# from LDAP attribute 'remoteAddr' in user's LDAP entry
#SSH_FROMIP_METHOD = 'user:remoteAddr'
SSH_FROMIP_METHOD = ''

# Plugin module for checking OTP
OTP_CHECK_MOD = None
VALID_OTP_REGEX = '^[0-9]+$'

# Plugin module for checking password
PASSWORD_CHECK_MOD = None
