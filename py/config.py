#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import web
import logging

# format char
fmt_c = '********'

debug = False
autoreload = False

# database
dbn = 'mysql'
user = 'webadmin'
password = 'webadmin791127'
host = 'localhost'
dbname = 'myblog'
print fmt_c, 'database set', fmt_c
print 'dbn=', dbn
print 'user=', user
print 'password=', password
print 'host=', host
print 'dbname=', dbname
print ''

# log
log_file= '/var/log/myblog/myblog.%d.log' % (os.getpid())
log_interval = 10
log_backups = 10
log_format = '%(levelname)s %(process)d %(message)s'
#log_format = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
#log_format = '%(levelname)s %(process)d %(asctime)-15s %(clientip)s %(message)s'
log_debug = True
log_level = logging.DEBUG
print fmt_c, 'log set', fmt_c
print 'log_file', log_file
print 'log_interval', log_interval
print 'log_backups', log_backups
print 'log_format', log_format
print ''

# file db path
filedb = "/opt/data/station/filedb/"
print fmt_c, 'other set', fmt_c
print 'filedb', filedb


# guest reader
guest_reader="张士卓"

