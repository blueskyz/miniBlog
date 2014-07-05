#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import web
import logging
import ConfigParser

# format char
fmt_c = '********'

debug = False
autoreload = False

# database
cfBase = ConfigParser.ConfigParser()
cfBase.read('py/config/base.ini')
dbn = cfBase.get('dbs', 'dbn')
user = cfBase.get('dbs', 'user')
password = cfBase.get('dbs', 'password')
host = cfBase.get('dbs', 'host')
dbname = cfBase.get('dbs', 'dbname')
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
filedb = "/data/station/filedb/"
print fmt_c, 'other set', fmt_c
print 'filedb', filedb

# station name
title = cfBase.get('station', 'title')
station_desc = cfBase.get('station', 'station_desc')

# guest reader
guest_reader = cfBase.get('login', 'guest_reader')


# widget
def loadWidgets(widgetCfg):
	widgets = {}
	cfWidget = ConfigParser.ConfigParser()
	cfWidget.read(widgetCfg)
	sections = cfWidget.sections()
	for section in sections:
		options = cfWidget.options(section)
		item = {}
		widgets[section] = item
		for option in options:
			item[option] = cfWidget.get(section, option)
	return widgets

widgets = loadWidgets('py/config/widgets.ini')

