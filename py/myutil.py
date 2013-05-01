#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import web.utils
import StringIO
from BaseHTTPServer import BaseHTTPRequestHandler

from wsgilog import WsgiLog
import web.contrib.template as template

import config

# template
render = template.render_mako(directories=['py/templates'], 
		input_encoding='utf-8',
		output_encoding='utf-8')


# log
class mylog(WsgiLog):
	def __init__(self, application):
		WsgiLog.__init__(
				self,
				application,
				logformat = config.log_format,
				tofile = True,
				tostream = True,
				toprint = False,
				debug = config.log_debug,
				loglevel = config.log_level,
				file = config.log_file,
				interval = config.log_interval,
				backups = config.log_backups
				)

	@staticmethod
	def _createmsg(msg = None):
		class FakeSocket:
			def makefile(self, *a):
				return StringIO.StringIO()

		fmtmsg = '[%s] - %s "%s %s %s" - %s. msg:%s'
		fmt = '[%s] - %s "%s %s %s" - %s.'
		environ = web.ctx.environ
		status = web.ctx.status

		req = environ.get('PATH_INFO', '_')
		protocol = environ.get('ACTUAL_SERVER_PROTOCOL', '-')
		method = environ.get('REQUEST_METHOD', '-')
		host = "%s:%s" % (environ.get('REMOTE_ADDR','-'), 
				environ.get('REMOTE_PORT','-'))
		time = BaseHTTPRequestHandler(FakeSocket(), None, None).log_date_time_string()
		if msg is not None:
			msg = fmtmsg % (time, host, protocol, method, req, status, msg)
		else:
			msg = fmt % (time, host, protocol, method, req, status)
		return web.utils.safestr(msg)

	@classmethod
	def logdebug(cls, msg = None):
		web.ctx.environ['wsgilog.logger'].debug(cls._createmsg(msg))

	@classmethod
	def loginfo(cls, msg = None):
		web.ctx.environ['wsgilog.logger'].info(cls._createmsg(msg))

	@classmethod
	def logerr(cls, msg = None):
		web.ctx.environ['wsgilog.logger'].error(cls._createmsg(msg))

# database
def dbconnect():
	try:
		db = web.database(dbn=config.dbn, 
				user=config.user, 
				pw=config.password, 
				host=config.host, 
				db=config.dbname)
		return db
	except Exception, error:
		print error

def session():
	return web.ctx.session

def privilege():
	return web.ctx.session.privilege

db = dbconnect()

