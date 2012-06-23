#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import web
import json
import hashlib
import authpicture as pic 

db = web.database(dbn='mysql', 
		user='webadmin', 
		pw='webadmin791127', 
		host='localhost', 
		db='myblog')

def privilege():
	return web.config["_session"].privilege

class login:
	def GET(self):
		pass

	def POST(self):
		try:
			session = web.config["_session"]
			data = json.loads(web.data())
			if session.authcode != data["authstr"]:
				raise Exception("验证码错误:" + session.authcode)
			query = "name='%s'" % (data["name"])
			lsuser = db.select("users", where=query, 
					what="name, passwd, privilege").list()
			web.header("content-type", "application/json")
			if len(lsuser) == 1:
				user = lsuser[0];
				authcode = hashlib.md5(user["passwd"] + session.authcode)
				if authcode.hexdigest() == data["authcode"]:
					session.privilege = user["privilege"]
					web.setcookie("id", data["authcode"], expires=3600)
					return '{"desc": "success"}'
				else:
					raise Exception("密码错误")
			else:
				raise Exception("用户名错误")
			return '{"desc": "error"}'
		except Exception, err:
			authcode = pic.picChecker().getPicString()
			web.config["_session"].authcode = authcode
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

class logout:
	def GET(self):
		web.config["_session"].privilege = -1
		web.config["_session"].kill()
		web.setcookie("id", "")
		web.header("content-type", "application/json")
		return '{"desc": "success"}'

	def POST(self):
		web.config["_session"].privilege = -1
		web.config["_session"].kill()
		web.setcookie("id", "")
		web.header("content-type", "application/json")
		return '{"desc": "success"}'

class user:
	def GET(self, userid=None):
		try:
			if privilege() < 1:
				raise Exception("privilege is error")
			squery = ("select user_id, name, localname, email, "
					"mobile_phone, description, privilege from users "
					"where user_id='%s'") % (userid)
			curlist = db.query(squery).list()
			if len(curlist) != 1:
				raise Exception("find user is not one.[%d]" % (len(curlist)))
			item = curlist[0]
			useritem = {}
			useritem["userid"] = item["user_id"]
			useritem["name"] = item["name"]
			useritem["localname"] = item["localname"]
			useritem["email"] = item["email"]
			useritem["mobilephone"] = item["mobile_phone"]
			useritem["description"] = item["description"]
			useritem["privilege"] = item["privilege"]
			web.header("content-type", "application/json")
			return json.dumps(useritem, ensure_ascii=False)
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return json.dumps({'desc': err.message}, ensure_ascii=False)

	def POST(self, userid=None):
		try:
			if privilege() != 2:
				raise Exception("privilege is error")
			if len(userid) == 0:
				self.__insert__()
			else:
				self.__update__(userid)
			web.header("content-type", "application/json")
			return json.dumps({'desc': 'success'})
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return json.dumps({'desc': str(err)}, ensure_ascii=False)

	def __update__(self, userid):
		data = json.loads(web.data())
		if (data["action"] == "delete"):
			db.delete("users", where="user_id='%s'" % (userid))
		else:
			db.update("users", name=data["name"], 
					localname=data["localname"], passwd=data["passwd"], 
					email=data["email"], mobile_phone=data["mobilephone"], 
					description=data["description"], privilege=int(data["privilege"]),
					where="user_id='%s'" % (userid))

	def __insert__(self):
		data = json.loads(web.data())
		db.insert("users", name=data["name"], 
				localname=data["localname"], passwd=data["passwd"], 
				email=data["email"], mobile_phone=data["mobilephone"], 
				description=data["description"], privilege=int(data["privilege"]))

class authpicture:
	def GET(self, seconds):
		picture = pic.picChecker() 
		data = picture.createChecker()   
		web.config["_session"].authcode = data["str"] 
		web.header('content-type', "image/png")
		return data["image"].getvalue()


urls = ("/login", "login",
		"/logout", "logout",
		"/([0-9]{0,3}){0,1}/?", "user",
		"/authpicture/([1-9][0-9]{9})/?", "authpicture",
		"", "error")

app_user = web.application(urls, globals(), autoreload=False)

