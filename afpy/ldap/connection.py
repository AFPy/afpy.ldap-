# -*- coding: utf-8 -*-
from dataflake.ldapconnection.connection import LDAPConnection
from dataflake.ldapconnection.utils import to_utf8
from ConfigObject import ConfigObject
from ConfigParser import NoOptionError
from node import Node
import ldap
import os

class LDAP(object):
    node_class = Node
    def __init__(self, section='ldap', prefix='ldap.', filename=os.path.expanduser('~/.ldap.cfg')):
        self.config = ConfigObject()
        self.config.read([filename])
        self.prefix = prefix
        self.section = self.config[section]
        self._conn = self.connection_factory()
        try:
            self.bind_dn = self.get('bind_dn')
            self.bind_pw = self.get('bind_pw')
            self.base_dn = self.get('base_dn', self.bind_dn.split(',', 1)[1])
        except Exception, e:
            raise e.__class__('Invalid configuration %s - %s' % (section, self.section))


    def get(self, key, default=None):
        try:
            return self.section[self.prefix+key]
        except (NoOptionError, KeyError):
            return default

    def connection_factory(self, user=None, passwd=None):
        config = dict(self.section.items())
        conn = ldapconnection_from_config(config, prefix=self.prefix)
        if conn.server.get('protocol') == 'ldaps':
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            ldap.set_option(ldap.OPT_REFERRALS, 0)
        return conn

    def check(self, uid, password):
        dn = self.uid2dn(uid)
        try:
            self.connection_factory().connect(dn, password)
        except ldap.INVALID_CREDENTIALS, e:
            return False
        return True

    def search(self, **kwargs):
        """search"""
        options = dict(base_dn=self.base_dn,
                       scope=ldap.SCOPE_SUBTREE,
                       bind_dn=self.bind_dn,
                       bind_pwd=self.bind_pw)
        options.update(kwargs)
        return self._conn.search(options.pop('base_dn'), options.pop('scope'), **options)['results']

    def search_nodes(self, **kwargs):
        return [self.node_class(r['dn'], attrs=r, conn=self) for r in self.search(**kwargs)]

    def get_dn(self, dn):
        """return search result for dn"""
        try:
            return self._conn.search(dn,
                                 ldap.SCOPE_BASE,
                                 bind_dn=self.bind_dn,
                                 bind_pwd=self.bind_pw)
        except:
            raise ValueError(dn)

    def uid2dn(self, uid):
        """apply `config:ldap.user_mask` to uid"""
        user_mask = self.get('user_mask', 'uid={uid},%s' % self.base_dn)
        return '=' in uid and uid or user_mask.replace('{uid}', uid)

    def group2dn(self, uid):
        """apply `config:ldap.group_mask` to uid"""
        group_mask = self.get('group_mask', 'cn={uid},%s' % self.section[self.prefix+'group_dn'])
        return '=' in uid and uid or group_mask.replace('{uid}', uid)

    def get_user(self, uid):
        """return user as node object"""
        dn = self.uid2dn(uid)
        return self.node_class(dn=dn, conn=self)

    def get_group(self, uid):
        """return group as node object"""
        dn = self.group2dn(uid)
        return self.node_class(dn=dn, conn=self)

    def get_node(self, dn=None):
        """return node for dn"""
        return self.node_class(dn=dn, conn=self)

    def get_groups(self, dn, base_dn=None):
        """return groups for dn"""
        if base_dn is None:
            base_dn = self.section[self.prefix+'group_dn']
        filter = '(&(objectClass=groupOfNames)(member=%s))' % dn
        return self.search_nodes(base_dn=base_dn,
                                 scope=ldap.SCOPE_SUBTREE,
                                 filter=filter,
                                 bind_dn=self.bind_dn,
                                 bind_pwd=self.bind_pw)



def ldapconnection_from_config(config, prefix='ldap.', **kwargs):
    """This is useful to get an LDAPConnection from a ConfigParser section
    items.
    """
    options = dict(
            host='localhost',
            port = 389,
            protocol = 'ldap',
            c_factory = ldap.initialize,
            login_attr='',
            rdn_attr='',
            bind_dn='',
            bind_pwd='',
            read_only=0,
            conn_timeout=-1,
            op_timeout=-1)

    options.update(kwargs)
    for key, value in config.items():
        if prefix in key:
            k = key.replace(prefix, '')
            if k in options:
                if isinstance(options[k], int):
                    try:
                        value = int(value)
                    except (TypeError, ValueError):
                        raise TypeError(
                           '%s must be an integer. Got %s' % (key, value))
                options[k] = value

    if not callable(options['c_factory']):
        raise TypeError(
           'c_factory must be callable. Got %(c_factory)s' % options)

    return LDAPConnection(**options)
