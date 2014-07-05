#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import json
import web

import config

# disable debug
web.config.debug=config.debug

# model control
import app.photo as appphoto
import app.blog as appblog
import app.resource as appres
import app.user as appuser
import app.wiki as appwiki

import myutil
from myutil import render, mylog
import app.authpicture as pic

# url map
urls = (# rest
		# photo app
		"/rest/photo", appphoto.app_photo,
		"/rest/blog", appblog.app_blog,
		"/rest/resource", appres.app_resource,
		"/rest/user", appuser.app_user,
		"/rest/wiki", appwiki.app_wiki,

		# page
		"/login/?", "login",
		"/photo/?([0-9]{0,4})/?", "photo",
		"/blog/([0-9]{1,2}){1}/([1-9][0-9]{9}){1}/?", "blog",
		"/blog/?([0-9]{1,2}){0,1}/?([1-9][0-9]{0,1}){0,1}/?([1-9][0-9]{0,1}){0,1}/?", "bloglist",
		"/resource/?([0-9]{1,2}){0,1}/?([1-9][0-9]{0,1}){0,1}/?([1-9][0-9]{0,1}){0,1}/?", "resource",

		# mgr page
		"/manage/blog/?([1-9][0-9]{9}){0,1}/?", "mgrblog",
		"/manage/photo/?([1-9][0-9]{9}){0,1}/?", "mgrphoto",
		"/manage/resource/?([1-9][0-9]{0,9}){0,1}/?", "mgrres",
		"/manage/user/?([0-9]{1,3}){0,1}/?", "mgruser",
		"/(.*)", "myweb")

app = web.application(urls, globals(), autoreload=config.autoreload)

web.config.session_parameters['cookie_path'] = '/'
web.config.session_parameters['timeout'] = 3600 
web.config.session_parameters['ignore_expiry'] = True

def createsession():
	print 'createsession'
	db = myutil.db
	if db is None:
		print 'db error'

	sessiondb = web.session.DBStore(db, 'sessions')
	session = web.session.Session(app, sessiondb,
			initializer={"privilege": -1, 
				"authcode": pic.picChecker().getPicString()})
	def session_hook():
		web.ctx.session = session
	app.add_processor(web.loadhook(session_hook))

def createprocessor():
	createsession()
	def pre_hook():
		mylog.loginfo()
	app.add_processor(web.loadhook(pre_hook))
	def post_hook():
		if web.ctx.fullpath[0:6] == "/rest/": 
				if web.ctx.fullpath[6:14] != "resource" \
						and web.ctx.fullpath[6:11] != "photo":
							web.header("content-type", "application/json")
				else:
					return
		else:
			web.header("content-type", "text/html; charset=utf-8")
	app.add_processor(web.unloadhook(post_hook))

createprocessor()

def islogin():
	#mylog.loginfo(web.ctx.session.authcode)
	return web.ctx.session.privilege >= 0

def mgrprivilege():
	return web.ctx.session.privilege >= 1


# main page
class myweb_old:
	def GET(self, cururl):
		categorys = json.loads(appblog.category().GET())
		blogs = json.loads(appblog.bloglist().GET(0, 1, 40))
		return render.index(menuname = '/', 
				login=islogin(), 
				mgrprivilege=mgrprivilege(), 
				photocount=8, 
				categorys=categorys,
				blogs=blogs)

# index page
class myweb:
	def GET(self, cururl):
		return bloglist().GET(0, pageidx=1, pagesize=40)


# login page
class login:
	def GET(self):
		if islogin() : raise web.seeother('/')
		return render.loginview(
				config=config,
				menuname='/login',
				login=islogin(), 
				mgrprivilege=mgrprivilege())


# photo page
class photo:
	def GET(self, categoryid = '0'):
		if len(categoryid) == 0 : categoryid = '0'
		categorys = json.loads(appphoto.category().GET())
		return render.photoview(
				config=config,
				menuname='/photo',
				login=islogin(), 
				mgrprivilege=mgrprivilege(), 
				categoryid=categoryid,
				categorys=categorys, 
				photocount=40)

# blog page
class blog:
	def GET(self, categoryid=None, blogid=None):
		categorys = json.loads(appblog.category().GET())
		blogs = json.loads(appblog.blog().GET(blogid, True))
		#mylog.loginfo(appblog.blog())
		return render.blogview(
				config=config,
				menuname='/blog',
				login=islogin(), 
				mgrprivilege=mgrprivilege(),
				blogid=blogid, 
				categoryid=categoryid,
				categorys=categorys, 
				blogs=blogs)

# blog list
class bloglist:
	def GET(self, categoryid=0, pageidx=1, pagesize=8):
		if categoryid is None:
			categoryid = 0
		if pageidx is None: pageidx = 1
		else: pageidx = int(pageidx)
		if pagesize is None: pagesize = 40
		else: pagesize = int(pagesize)
		if pagesize > 100: pagesize = 40
		categorys = json.loads(appblog.category().GET())
		count = json.loads(appblog.count().GET(categoryid))['count']
		pagecount = count / pagesize + 1
		if count % pagesize == 0:
			pagecount = pagecount - 1
		if pagecount < pageidx:
			pageidx = 1
		blogs = json.loads(appblog.bloglist().GET(categoryid, pageidx, pagesize))
		#mylog.loginfo(appblog.bloglist().GET(categoryid,pageidx,pagesize))
		return render.blogview(
				config=config,
				menuname='/blog',
				login=islogin(), 
				mgrprivilege=mgrprivilege(),
				blogid=None, 
				categoryid=categoryid, 
				categorys=categorys, 
				blogs=blogs,
				pagecount=pagecount,
				pageidx=pageidx,
				pagesize=pagesize)

# resource page
class resource:
	def GET(self, categoryid=0, pageidx=1, pagesize=8):
		if categoryid is None:
			categoryid = 0
		if pageidx is None: pageidx = 1
		else: pageidx = int(pageidx)
		if pagesize is None: pagesize = 40
		else: pagesize = int(pagesize)
		if pagesize > 100: pagesize = 40
		categorys = json.loads(appres.category().GET())
		count = json.loads(appres.count().GET(categoryid))['count']
		pagecount = count / pagesize + 1
		if count % pagesize == 0:
			pagecount = pagecount - 1
		if pagecount < pageidx:
			pageidx = 1
		resources = json.loads(appres.resourcelist().GET(categoryid, \
				pageidx, pagesize))
		return render.resourceview(
				config=config,
				menuname='/resource',
				login=islogin(), 
				mgrprivilege=mgrprivilege(),
				resourceid=None, 
				categoryid=categoryid, 
				categorys=categorys, 
				resources=resources,
				pagecount=pagecount,
				pageidx=pageidx,
				pagesize=pagesize)

# manage blog page
class mgrblog:
	def GET(self, blogid=None):
		return render.mgrblogview(
				config=config,
				menuname='/manage',
				curmgrtype='/blog',
				login=islogin(), 
				mgrprivilege=mgrprivilege(), 
				blogid=blogid)

# manage photo page
class mgrphoto:
	def GET(self, photoid=None):
		return render.mgrphotoview(
				config=config,
				menuname='/manage',
				curmgrtype='/photo',
				login=islogin(), 
				mgrprivilege=mgrprivilege(), 
				photoid=photoid)

# manage photo page
class mgrres:
	def GET(self, resourceid = None):
		categorys = json.loads(appres.category().GET())
		resource = None
		if resourceid:
			resource = json.loads(appres.resource().GET(resourceid))
			mylog.loginfo(resource)
		mylog.loginfo(categorys)
		return render.mgrresview(
				config=config,
				menuname = '/manage',
				curmgrtype = '/resource',
				login = islogin(), 
				mgrprivilege = mgrprivilege(), 
				categorys = categorys,
				resourceid = resourceid,
				resource = resource)

# manage user page
class mgruser:
	def GET(self, userid=None):
		return render.mgruserview(
				config=config,
				menuname='/manage',
				curmgrtype='/user',
				login=islogin(), 
				mgrprivilege=mgrprivilege(),
				userid=userid)

application = app.wsgifunc(mylog)

if __name__ == "__main__":
	web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
	print 'start run web server'
	app.run(mylog)

