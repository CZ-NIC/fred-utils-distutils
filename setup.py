#!/usr/bin/python
# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
        name='fred-distutils',
        version='1.0',
        description = 'Fred Distutils',
        author = 'Aleš Doležal, CZ.NIC',
        author_email = 'ales.dolezal@nic.cz',
        url = 'http://www.nic.cz/',
        license = 'GNU GPL',
        platforms = ['posix'],
        long_description = 'Fred Distutils, utilities for easier way to build packages.',

        packages=['freddist', 'freddist.command', 'freddist.nicms'],
        package_data={'freddist': ['freddist/README']},

      )

