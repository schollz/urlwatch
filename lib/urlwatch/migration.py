# -*- coding: utf-8 -*-
#
# This file is part of urlwatch (https://thp.io/2008/urlwatch/).
# Copyright (c) 2008-2016 Thomas Perl <thp.io/about>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The name of the author may not be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import logging
import os.path
import sys

from .util import atomic_rename
from .storage import UrlsYaml, UrlsTxt, CacheDirStorage

logger = logging.getLogger(__name__)


def migrate_urls(urlwatcher):
    # Migrate urlwatch 1.x URLs to urlwatch 2.x

    urlwatch_config = urlwatcher.urlwatch_config
    pkgname = urlwatch_config.pkgname
    urls = urlwatch_config.urls
    urls_txt = os.path.join(urlwatch_config.urlwatch_dir, 'urls.txt')
    edit = urlwatch_config.edit
    add = urlwatch_config.add

    if os.path.isfile(urls_txt) and not os.path.isfile(urls):
        print("""
    Migrating URLs: {urls_txt} -> {urls_yaml}
    Use "{pkgname} --edit" to customize it.
    """.format(urls_txt=urls_txt, urls_yaml=urls, pkgname=pkgname))
        UrlsYaml(urls).save(UrlsTxt(urls_txt).load_secure())
        atomic_rename(urls_txt, urls_txt + '.migrated')

    if not os.path.isfile(urls) and not edit and not add:
        print("""
    You need to create {urls_yaml} in order to use {pkgname}.
    Use "{pkgname} --edit" to open the file with your editor.
    """.format(urls_yaml=urls, pkgname=pkgname))
        sys.exit(1)


def migrate_cache(urlwatcher):
    # Migrate urlwatch 1.x cache to urlwatch 2.x

    urlwatch_config = urlwatcher.urlwatch_config
    cache = urlwatch_config.cache
    cache_dir = os.path.join(urlwatch_config.urlwatch_dir, 'cache')

    if not os.path.isfile(cache) and os.path.isdir(cache_dir):
        print("""
    Migrating cache: {cache_dir} -> {cache_db}
    """.format(cache_dir=cache_dir, cache_db=cache))

        old_cache_storage = CacheDirStorage(cache_dir)
        urlwatcher.cache_storage.restore(old_cache_storage.backup())
        urlwatcher.cache_storage.gc([job.get_guid() for job in urlwatcher.jobs])
        atomic_rename(cache_dir, cache_dir + '.migrated')
