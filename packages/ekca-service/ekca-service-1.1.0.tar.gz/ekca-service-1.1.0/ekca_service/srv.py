# -*- coding: utf-8 -*-
"""
The EKCA service package
"""

# from Python's standard library
import socket
import os
import re
import uuid
import logging
import logging.config

# from setuptools
import pkg_resources

# from PyNaCl package
import nacl.utils
import nacl.public

# from Werkzeug package
import werkzeug.exceptions
from werkzeug.exceptions import HTTPException

from werkzeug.middleware.proxy_fix import ProxyFix

import flask.logging
from flask import Flask, request, g, jsonify

from .__about__ import OTP_PLUGIN_NAMESPACE, PASSWORD_PLUGIN_NAMESPACE
from .plugins.otp.base import OTPCheckFailed
from .plugins.password.base import PasswordCheckFailed
from .sshca import SSHCertAuthority, SSHCAException

# initialize app
app = Flask(__name__, instance_relative_config=True)

# initialize config
app.config.from_object('ekca_service.settings')
app.config.from_envvar('EKCA_CFG', silent=False)

# initialize logging
if os.path.isfile(app.config['LOG_CONFIG']):
    logging.config.fileConfig(app.config['LOG_CONFIG'], disable_existing_loggers=True)
    app.logger.removeHandler(flask.logging.default_handler)
    app.logger.debug('Loaded logging config from %s', app.config['LOG_CONFIG'])
else:
    app.logger.warning('No valid logging config at %s', app.config['LOG_CONFIG'])
app.logger.name = app.config['LOG_NAME']

if app.config['PROXY_LEVEL'] > 0:
    # see https://werkzeug.palletsprojects.com/en/1.0.x/middleware/proxy_fix/
    app.logger.info('Using ProxyFix wrapper with %d proxy layers', app.config['PROXY_LEVEL'])
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=app.config['PROXY_LEVEL'],
        x_proto=app.config['PROXY_LEVEL'],
        x_host=app.config['PROXY_LEVEL'],
    )

# set default socket timeout, especially for urllib.request.urlopen()
socket.setdefaulttimeout(app.config['SOCKET_TIMEOUT'])


class RequestError(werkzeug.exceptions.BadRequest):
    """
    generic error class
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        werkzeug.exceptions.BadRequest.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """
        return a dict to be returned to client as JSON
        """
        res = dict(self.payload or ())
        res['message'] = self.message
        return res


def user_regex():
    """
    initialize global regex object for validating usernames
    """
    if not hasattr(g, 'VALID_USERNAME_REGEX'):
        g.VALID_USERNAME_REGEX = re.compile(app.config['VALID_USERNAME_REGEX'])
    return g.VALID_USERNAME_REGEX


def otp_regex():
    """
    initialize global regex object for validating usernames
    """
    if not hasattr(g, 'VALID_OTP_REGEX'):
        g.VALID_OTP_REGEX = re.compile(app.config['VALID_OTP_REGEX'])
    return g.VALID_OTP_REGEX


def password_checker():
    """
    Return PasswordChecker instance defined with config parameter PASSWORD_CHECK_MOD
    """
    if hasattr(g, 'PASSWORD_CHECKER'):
        return g.PASSWORD_CHECKER
    g.PASSWORD_CHECKER = None
    if app.config['PASSWORD_CHECK_MOD']:
        password_plugins = {
            entry_point.name: entry_point.load()
            for entry_point in pkg_resources.iter_entry_points(PASSWORD_PLUGIN_NAMESPACE)
        }
        if app.config['PASSWORD_CHECK_MOD'] not in password_plugins:
            raise KeyError(
                'Plugin module {0!r} not found in {1}!'.format(
                    app.config['PASSWORD_CHECK_MOD'],
                    OTP_PLUGIN_NAMESPACE,
                )
            )
        # init OTP check plugin
        g.PASSWORD_CHECKER = password_plugins[app.config['PASSWORD_CHECK_MOD']](
            app.config,
            app.logger,
        )
        app.logger.debug('Initialized password check plugin %s', g.PASSWORD_CHECKER.__class__.__name__)
    return g.PASSWORD_CHECKER


def otp_checker():
    """
    Return OTPChecker instance defined with config parameter OTP_CHECK_MOD
    """
    if hasattr(g, 'OTP_CHECKER'):
        return g.OTP_CHECKER
    g.OTP_CHECKER = None
    if app.config['OTP_CHECK_MOD']:
        otp_plugins = {
            entry_point.name: entry_point.load()
            for entry_point in pkg_resources.iter_entry_points(OTP_PLUGIN_NAMESPACE)
        }
        if app.config['OTP_CHECK_MOD'] not in otp_plugins:
            raise KeyError(
                'Plugin module {0!r} not found in {1}!'.format(
                    app.config['OTP_CHECK_MOD'],
                    OTP_PLUGIN_NAMESPACE,
                )
            )
        # init OTP check plugin
        g.OTP_CHECKER = otp_plugins[app.config['OTP_CHECK_MOD']](
            app.config,
            app.logger,
        )
        app.logger.debug('Initialized OTP check plugin %s', g.OTP_CHECKER.__class__.__name__)
    return g.OTP_CHECKER

with app.app_context():
    # enforce loading password checker plugin
    password_checker()
    # enforce loading OTP checker plugin
    otp_checker()


def check_user_authc(user_name, password, otp):
    """
    generic wrapper function to be overridden by plugins later
    """
    # check whether username has valid format
    if not user_regex().match(user_name):
        app.logger.warning('Invalid user name %r', user_name)
        raise RequestError('invalid user name', status_code=405)
    # check whether OTP has valid format
    if not otp_regex().match(otp):
        app.logger.warning('Invalid OTP format %r', otp)
        raise RequestError('invalid OTP', status_code=405)
    if otp_checker():
        # first check OTP to consume it in every case
        otp_checker().check(user_name, otp)
        app.logger.info('OTP check successful for user name %r', user_name)
        return password_checker().check(user_name, password, request.remote_addr)
    return password_checker().check(user_name, password+otp, request.remote_addr)


@app.errorhandler(OTPCheckFailed)
def handle_otp_check_failed(error):
    """
    in case of unhandled OTPCheckFailed it returns 401 response
    """
    app.logger.error('OTP check failed: %r', error)
    response = jsonify(message='authentication failed')
    response.status_code = 401
    return response


@app.errorhandler(PasswordCheckFailed)
def handle_password_check_failed(error):
    """
    in case of unhandled PasswordCheckFailed it returns 401 response
    """
    app.logger.error('Password check failed: %r', error)
    response = jsonify(message='authentication failed')
    response.status_code = 401
    return response


@app.errorhandler(Exception)
def handle_internal_error(error):
    """
    returns response based on InternalServerError exception instance
    """
    app.logger.error('Unhandled error: %r', error, exc_info=True)
    response = jsonify(message='internal error')
    response.status_code = 500
    return response


@app.errorhandler(HTTPException)
def handle_http_error(error):
    """
    returns response based on RequestError exception instance
    """
    response = jsonify(message=str(error))
    response.status_code = error.code
    return response


@app.errorhandler(RequestError)
def handle_request_error(error):
    """
    returns response based on RequestError exception instance
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/get', methods=['GET'])
def get_capubkey():
    """
    return the public key of a CA
    """
    ca_name = app.config['SSH_CA_NAME']
    ca_dir = os.path.join(app.config['SSH_CA_DIR'], ca_name)
    try:
        ssh_ca = SSHCertAuthority(app.config, ca_name, ca_dir, logger=app.logger)
    except SSHCAException as err:
        app.logger.warning('Error initializing CA %r: %r', ca_name, err)
        raise RequestError('invalid CA', status_code=404)
    return jsonify(ca=ca_name, pubkey=ssh_ca.get_pubkey())


@app.route('/check', methods=['GET'])
def check_signing():
    """
    sign a dummy key to check whether SSH-CA key is loaded
    """
    ca_name = app.config['SSH_CA_NAME']
    ca_dir = os.path.join(app.config['SSH_CA_DIR'], ca_name)
    try:
        ssh_ca = SSHCertAuthority(app.config, ca_name, ca_dir, logger=app.logger)
    except SSHCAException as err:
        app.logger.warning('Error initializing CA %r: %r', ca_name, err)
        raise RequestError('invalid CA', status_code=404)
    pass_phrase, user_key, user_cert = ssh_ca.user_cert(
        '__dummy__',
        ['127.0.0.1'],
        'test-request-id',
        (()),
        '+0s',
        remove_files=True,
    )
    return jsonify(ca=ca_name, cert=user_cert.decode('utf-8'))


@app.route('/usercert', methods=['POST'])
def gen_user_cert():
    """
    generate user key pair and cert
    """
    ca_name = app.config['SSH_CA_NAME']
    # load the CA if existing
    ca_dir = os.path.join(app.config['SSH_CA_DIR'], ca_name)
    try:
        ssh_ca = SSHCertAuthority(app.config, ca_name, ca_dir, logger=app.logger)
    except SSHCAException as err:
        app.logger.warning('Error initializing CA %r: %r', ca_name, err)
        raise RequestError('invalid CA', status_code=404)
    # check input
    if not request.get_json():
        app.logger.warning('No request data')
        raise RequestError('invalid request', status_code=405)
    # check whether all required input parameters are there
    for param in ('username', 'reqid', 'password', 'otp', 'epubkey'):
        if param not in request.get_json() or not request.get_json()[param]:
            app.logger.warning('Parameter %r missing or empty in request', param)
            raise RequestError('%s missing or empty' % (param), status_code=405)
    try:
        req_id = str(uuid.UUID(request.get_json()['reqid']))
    except ValueError:
        app.logger.warning('Invalid reqid in request for %r', request.get_json()['username'])
        raise RequestError('invalid reqid', status_code=405)
    # whether to get from IP address from user entry returned by password plugin
    user_entry = check_user_authc(
        request.get_json()['username'],
        request.get_json()['password'],
        request.get_json()['otp'],
    )
    # determine the IP address to be signed
    from_ip = None
    if app.config['SSH_FROMIP_METHOD'].lower() == 'request.remote_addr':
        from_ip = [request.remote_addr]
    elif app.config['SSH_FROMIP_METHOD'].lower().startswith('user:'):
        user_ipaddr_attr = app.config['SSH_FROMIP_METHOD'][5:].strip()
        if user_ipaddr_attr in user_entry:
            from_ip = user_entry[user_ipaddr_attr]
    # determine the SSH permissions to be signed
    if 'SSH_CERT_PERMISSIONS_ATTR' in app.config and app.config['SSH_CERT_PERMISSIONS_ATTR']:
        ssh_cert_perms = (
            user_entry.get(app.config['SSH_CERT_PERMISSIONS_ATTR'])
            or app.config['SSH_CERT_PERMISSIONS']
        )
    else:
        ssh_cert_perms = app.config['SSH_CERT_PERMISSIONS']
    pass_phrase, user_key, user_cert = ssh_ca.user_cert(
        request.get_json()['username'],
        from_ip,
        req_id,
        ssh_cert_perms,
        app.config['SSH_CERT_VALIDITY'],
    )
    ekey_box = nacl.public.SealedBox(
        nacl.public.PublicKey(
            request.get_json()['epubkey'].encode('ascii'),
            nacl.encoding.URLSafeBase64Encoder,
        ),
    )
    crypted_pass_phrase = ekey_box.encrypt(pass_phrase, nacl.encoding.URLSafeBase64Encoder)
    return jsonify(
        message='SSH cert issued for %s' % (request.get_json()['username']),
        reqid=req_id,
        passphrase=crypted_pass_phrase.decode('ascii'),
        key=user_key,
        cert=user_cert.decode('utf-8'),
        validity=app.config['SSH_CERT_VALIDITY'],
    )
