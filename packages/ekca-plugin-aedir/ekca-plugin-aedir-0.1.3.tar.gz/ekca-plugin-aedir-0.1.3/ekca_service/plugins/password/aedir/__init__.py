# -*- coding: utf-8 -*-
"""
ekca_service.plugins.password.ldap3 - Module package for LDAP password checker plugins
"""

from ldap0 import LDAPError
from ldap0.filter import escape_str as escape_filter_str
from ldap0.controls.ppolicy import PasswordPolicyControl
from ldap0.controls.simple import AuthorizationIdentityRequestControl
from ldap0.controls.sessiontrack import SessionTrackingControl, SESSION_TRACKING_FORMAT_OID_USERNAME

from aedir import AEDirObject, AEDirUrl, aedir_aeuser_dn

from ekca_service.plugins.password.base import PasswordChecker, PasswordCheckFailed


class AEDirPasswordChecker(PasswordChecker):
    """
    Password check done by sending a simple bind request to the server
    """

    def __init__(self, cfg, logger):
        PasswordChecker.__init__(self, cfg, logger)
        self.user_attrs = [self._cfg.get('SSH_CERT_PERMISSIONS_ATTR', 'aeSSHPermissions')]
        if self._cfg.get('SSH_FROMIP_METHOD', '').lower().startswith('user:'):
            ipaddr_attr = self._cfg['SSH_FROMIP_METHOD'][5:].strip()
            self.user_attrs.append(ipaddr_attr)

    @staticmethod
    def _session_tracking_control(user_name, remote_addr):
        """
        return SessionTrackingControl instance based on params
        """
        return SessionTrackingControl(
            remote_addr,
            'ekca-service',
            SESSION_TRACKING_FORMAT_OID_USERNAME,
            user_name,
        )

    def check(self, user_name, password, remote_addr):
        """
        Check password of user
        """
        # accepting empty passwords is a security issue on most LDAP servers
        # => always error out in case of empty password
        if not password:
            raise PasswordCheckFailed('Empty password for user name {!r}'.format(user_name))
        # open new LDAP connection
        ldap_conn = AEDirObject(
            self._cfg['LDAP_URI'],
            cacert_filename=self._cfg['LDAP_CA_CERT'],
            timeout=self._cfg['SOCKET_TIMEOUT'],
        )
        bind_dn = None
        stc = self._session_tracking_control(user_name, remote_addr)
        try:
            # determine the bind DN (DN of user's entry)
            bind_dn = aedir_aeuser_dn(user_name, aeroot_dn=ldap_conn.search_base)
            ldap_conn.simple_bind_s(
                bind_dn,
                password.encode(ldap_conn.encoding),
                req_ctrls=[
                    PasswordPolicyControl(),
                    AuthorizationIdentityRequestControl(),
                    stc,
                ],
            )
            self._log.debug(
                'Bound to %r as %r',
                ldap_conn.uri,
                ldap_conn.get_whoami_dn(),
            )
            ldap_res = ldap_conn.read_s(
                ldap_conn.get_whoami_dn(),
                filterstr=self._cfg['LDAP_READ_FILTER'].format(
                    raddr=escape_filter_str(remote_addr),
                ),
                attrlist=self.user_attrs,
                req_ctrls=[stc],
            )
            if ldap_res is None:
                raise PasswordCheckFailed('No result reading user entry {!r}'.format(ldap_conn.get_whoami_dn()))
            self._log.debug(
                'Read user entry %r: %r',
                ldap_conn.get_whoami_dn(),
                ldap_res.entry_s
            )
        except LDAPError as ldap_err:
            raise PasswordCheckFailed(
                'Bind as {} / {} failed: {!r}'.format(
                    user_name,
                    bind_dn,
                    ldap_err,
                )
            )
        return ldap_res.entry_s
