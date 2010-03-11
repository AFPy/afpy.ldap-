# -*- coding: utf-8 -*-
try:
    from repoze.what.middleware import setup_auth
except ImportError:
    raise ImportError('repoze.what is required')
from repoze.who.plugins.basicauth import BasicAuthPlugin
from afpy.ldap.connection import Connection
from afpy.ldap import auth
import os

__doc__ = """
This module contain a paste entry point example with basic auth.

You can use it in you app. Once you have read :doc:`../install` you can use this
in your paste config file:

.. sourcecode:: ini

    [filter:auth]
    use = egg:afpy.ldap
    section = afpy

    # and if you dont want to use ~/.ldap.cfg
    #file = %(here)s/ldap.cfg

You can also adapt this code and use your own identifiers/challengers:

.. literalinclude:: ../../afpy/ldap/authbasic.py
   :language: py

"""

def make_auth_basic(app, global_config, conn=None, **local_conf):
    """Paste entry point for auth basic middleware using repoze.what"""

    if not conn:
        section = local_conf.get('section', 'ldap')
        config_file = local_conf.get('config', os.path.expanduser('~/.ldap.cfg'))
        conn = Connection(section, filename=config_file)

    authenticator=auth.Authenticator(conn)

    groups = auth.GroupAdapter(conn)
    groups = {'all_groups': groups}

    basicauth = BasicAuthPlugin('Private web site')
    identifiers=[("basicauth", basicauth)]
    challengers=[("basicauth", basicauth)]

    authenticators=[("accounts", authenticator)]
    mdproviders=[("accounts", auth.MDPlugin(conn))]

    permissions = {'all_perms': auth.PermissionAdapter(conn)}

    return setup_auth(app,
                      groups,
                      permissions,
                      identifiers=identifiers,
                      authenticators=authenticators,
                      challengers=challengers,
                      mdproviders=mdproviders)

