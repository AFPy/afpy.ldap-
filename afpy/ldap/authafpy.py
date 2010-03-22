# -*- coding: utf-8 -*-
from zope.interface import implements
from repoze.who.interfaces import IAuthenticator
from repoze.who.interfaces import IMetadataProvider
from repoze.what.adapters import BaseSourceAdapter, SourceError
from repoze.who.plugins.basicauth import BasicAuthPlugin
from repoze.who.plugins.friendlyform import FriendlyFormPlugin
from repoze.who.plugins.cookie import InsecureCookiePlugin
from repoze.what.middleware import setup_auth
from afpy.ldap import custom as ldap
from afpy.ldap import auth

def make_auth(app, global_config, **local_config):

    conn = ldap.get_conn()

    cookie = InsecureCookiePlugin('__ac')

    loginform=FriendlyFormPlugin(login_form_url="/login",
                                 login_handler_path="/do_login",
                                 post_login_url="/login",
                                 logout_handler_path="/logout",
                                 post_logout_url="/login",
                                 rememberer_name="_ac")

    authenticators=[("accounts", auth.Authenticator(conn))]

    basicauth = BasicAuthPlugin('Private web site')
    if 'auth_basic' in local_config:
        identifiers=[("basicauth", basicauth)]
        challengers=[("basicauth", basicauth)]
    else:
        identifiers=[("loginform", loginform), ("_ac", cookie), ("basicauth", basicauth)]
        challengers=[("loginform", loginform)]

    groups = {'all_groups': auth.GroupAdapter(conn)}
    permissions = {'all_perms': auth.PermissionAdapter(conn, use_permissions=False)}
    mdproviders=[("accounts", auth.MDPlugin(conn))]

    return setup_auth(app,
                      groups,
                      permissions,
                      identifiers=identifiers,
                      authenticators=authenticators,
                      challengers=challengers,
                      mdproviders=mdproviders)

