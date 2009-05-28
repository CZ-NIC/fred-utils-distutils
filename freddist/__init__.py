#!/usr/bin/python
# -*- coding: utf-8 -*-
# django
from django.conf.urls.defaults import patterns, include
from django.conf import settings


def module_urls():
    return patterns('',
        (r'^vip/', include('apps.vip.urls')),
    )
