#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web

import config


# disable debug
web.config.debug=config.debug

# model control
import app.photo as appphoto
import app.blog as appblog
import app.user as appuser

from myutil import render
import app.authpicture as pic

# url map
urls = (# rest
		# photo app
		"/rest/photo", appphoto.app_photo,
		"/rest/blog", appblog.app_blog,
		"/rest/user", appuser.app_user,
		# page
		"/photo/?", "photo",
		"/login/?", "login",
		"/blog/?([0-9]{1,2}){0,1}/?([1-9][0-9]{9}){0,1}/?", "blog",
		# mgr page
		"/manage/blog/?([1-9][0-9]{9}){0,1}/?", "mgrblog",
		"/manage/photo/?([1-9][0-9]{9}){0,1}/?", "mgrphoto",
		"/manage/user/?([0-9]{1,3}){0,1}/?", "mgruser",
		"/(.*)", "myweb")

app = web.application(urls, globals(), autoreload=config.autoreload)

web.config.session_parameters['timeout'] = 3600 
web.config.session_parameters['ignore_expiry'] = False

import myutil

def createsession():
	if web.config.get('_session'):
		return web.config._session
	sqlitedb = web.database(dbn='mysql', 
			user='webadmin', 
			pw='webadmin791127', 
			host='localhost', 
			db='myblog')

	sessiondb = web.session.DBStore(sqlitedb, 'sessions')
	session = web.session.Session(app, sessiondb,
			initializer={"privilege": -1, 
				"authcode": pic.picChecker().getPicString()})
	web.config["_session"] = session

createsession()

#sqlitedb = web.database(dbn="sqlite", db="sessions/sessions.dat")
#sessiondb = web.session.DBStore(sqlitedb, 'sessions')
#session = web.session.Session(app, sessiondb,
#		initializer={"privilege": -1, 
#			"authcode": pic.picChecker().getPicString()})
#web.config["_session"] = session

def islogin():
	return web.config["_session"].privilege >= 0

def mgrprivilege():
	return web.config["_session"].privilege >= 1

# main page
class myweb:
	def GET(self, cururl):
		return render.index(login=islogin(), mgrprivilege=mgrprivilege(), 
				photocount=8, blogcount=15)

# login page
class login:
	def GET(self):
		return render.loginview(login=islogin(), mgrprivilege=mgrprivilege())

# photo page
class photo:
	def GET(self):
		return render.photoview(login=islogin(), mgrprivilege=mgrprivilege(), 
				photocount=40)

# blog page
class blog:
	def GET(self, categoryid=None, blogid=None):
		return render.blogview(login=islogin(), mgrprivilege=mgrprivilege(),
				blogcount=30, categoryid=categoryid, blogid=blogid)

# manage blog page
class mgrblog:
	def GET(self, blogid=None):
		return render.mgrblogview(login=islogin(), mgrprivilege=mgrprivilege(), 
				blogid=blogid)

# manage photo page
class mgrphoto:
	def GET(self, photoid=None):
		return render.mgrphotoview(login=islogin(), mgrprivilege=mgrprivilege(), 
				photoid=photoid)

# manage user page
class mgruser:
	def GET(self, userid=None):
		return render.mgruserview(login=islogin(), mgrprivilege=mgrprivilege(),
				userid=userid)


if __name__ == "__main__":
	web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
	app.run()

