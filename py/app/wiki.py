#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import time
import json
import web
import urlparse
import mediawiki as wikiparser

import config
import myutil

db = myutil.db
privilege = myutil.privilege

class reblog:
	def GET(self): raise web.seeother('/')


class wiki:
	def GET(self):
		return "why?"
	def POST(self, content=""):
		try:
			if privilege() < 1:
				raise Exception("privilege is error")
			datadict = dict(urlparse.parse_qsl(web.data()))
			data = datadict["data"]
			if len(data)==0:
				raise Exception("content is empty!")
			return wikiparser.wiki2html(data, False)
		except Exception, err:
			web.BadRequest()
			return '{"desc": "%s"}' % (err)

urls = (# rest router
		"/?", "wiki",
		"", "reblog")

app_wiki = web.application(urls, globals(), autoreload=config.autoreload)

