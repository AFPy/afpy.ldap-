# -*- coding: utf-8 -*-
# Copyright (c) 2009 Gael Pasgrimaud
"""
afpy.ldap
"""
import os
from setuptools import setup, find_packages

version = '0.7'

long_description = """%s

News
=====

%s
""" % (
        open(os.path.join('README.txt')).read(),
        open(os.path.join('CHANGES.txt')).read()
      )

setup(name='afpy.ldap',
      version=version,
      description="This module provide an easy way to deal with ldap stuff in python.",
      long_description='''
afpy.ldap
=========

%s
''' % long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='ldap',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='https://hg.afpy.org/gawel/afpy.ldap/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['afpy'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'ConfigObject',
          'dataflake.ldapconnection>0.9',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      ldapsh = afpy.ldap.scripts:main

      [paste.filter_app_factory]
      main = afpy.ldap.authbasic:make_auth_basic
      """,
      )

