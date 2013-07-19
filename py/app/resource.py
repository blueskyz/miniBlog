#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path as path
import time
import json
import md5

import web
import cgi

import config
import myutil

cgi.maxlen = 100 * 1024 * 1024 # 100MB

db = myutil.db
privilege = myutil.privilege


class reres:
	def GET(self): raise web.seeother('/')

class count:
	def GET(self, categoryid=None):
		try:
			query = ("select count(resource_id) as total from resources "
					"where privilege <= %d;") % (privilege())
			if int(categoryid) != 0:
				query = ("select count(res_category_link.category_id) as total "
						"from res_category_link left outer join resources "
						"on resources.resource_id = res_category_link.resource_id "
						"where resources.privilege <= %d and "
						"res_category_link.category_id = %d;") \
								%(privilege(), int(categoryid))
			curset = db.query(query)
			return json.dumps({'count': curset[0]["total"]}, ensure_ascii=False)
		except Exception, err:
			web.BadRequest()
			return '{"desc": "%s", "sql:" "%s"}' % (err, query)

class category:
	def GET(self):
		try:
			categorylist = []
			# all category
			curwhere = "privilege <= %d" % (privilege())
			curlist = db.select("resources", what="count(resource_id) as count", 
					where=curwhere).list()
			category = {"count": curlist[0]["count"], "category_id": 0, 
					"name": u"所有资源", "description": u"所有资源"}
			categorylist.append(category)

			# other category
			query = "select res_category.category_id as category_id, " \
					"res_category.name as name, " \
					"res_category.description as description, " \
					"count(res_category_link.category_id) as count " \
					"from (resources, res_category) left outer join res_category_link " \
					"on resources.resource_id = res_category_link.resource_id " \
					"and res_category.category_id= res_category_link.category_id " \
					"where resources.privilege <= %d " \
					"group by res_category.category_id;" % (privilege())
			curlist = db.query(query).list()
			for item in curlist:
				category = {}
				category["category_id"] = item["category_id"]
				category["name"] = item["name"]
				category["description"] = item["description"]
				category["count"] = item["count"]
				categorylist.append(category)
			return json.dumps(categorylist, ensure_ascii=False)
		except Exception, err:
			web.BadRequest()
			return '{"desc": "%s"}' % (err)

	def POST(self):
		try:
			pass
		except Exception, err:
			web.BadRequest()
			return '{"desc": "%s"}' % (err)

class resourceDownload:
	def GET(self, resourceid):
		try:
			curwhere = "resource_id=%d and privilege <= %d" \
					% (int(resourceid), privilege())
			curlist = db.select("resources", 
					what="resource_id, filename, path, description, " \
							"privilege, md5, filesize", 
					where=curwhere).list()
			if len(curlist) == 0:
				raise Exception("can't find file!")

			web.header('Content-Type','application/octet-stream')
			web.header('Content-disposition', 'attachment; filename=%s' \
					% (curlist[0]["filename"]))
			web.header("x-accel-redirect", 
					"/resdata/resources/other/%s" % (curlist[0]['path']))
			return
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

class resource:
	def GET(self, resourceid):
		try:
			# 获取资源
			curwhere = "resource_id=%d and privilege <= %d" \
					% (int(resourceid), privilege())
			curlist = db.select("resources", 
					what="resource_id, name, path, description, " \
							"privilege, md5, filesize", 
					where=curwhere).list()
			if len(curlist) == 0:
				raise Exception("can't find file!")
			buf = {}
			buf["resourceid"] = curlist[0]["resource_id"]
			buf["name"] = curlist[0]["name"]
			buf["desc"] = curlist[0]["description"]
			buf["resurl"] = "/rest/resource/download/%s" % (curlist[0]['resource_id'])
			buf["privilege"] = curlist[0]["privilege"]
			buf["md5"] = curlist[0]["md5"]
			buf["filesize"] = curlist[0]["filesize"]

			# 获取资源所属类目
			catwhere = "resource_id=%d" % (int(resourceid))
			catlist = db.select("res_category_link",
					what = "category_id",
					where = catwhere).list()
			if len(catlist) == 0:
				buf["category_id"] = 0
			else:
				buf["category_id"] = catlist[0]["category_id"]
			web.header('content-type', "application/json")
			return json.dumps(buf, ensure_ascii=False)
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

	def POST(self, resourceid=None):
		try:
			if privilege() < 1:
				raise Exception("privilege is error")
			if resourceid is None:
				resourceid = self.__insert__()
			else:
				curwhere = "resource_id=%d" % (int(resourceid))
				curlist = db.select("resources", what="resource_id", 
						where=curwhere).list()
				newId = resourceid
				if len(curlist) == 0:
					resourceid = self.__insert__()
				else:
					self.__update__(resourceid)

		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

	def __insert__(self):
		contentdata = web.input(content={})
		data = web.input()
		content = buffer(contentdata["content"].value)
		nowtime = time.time()
		md5str = md5.md5(content).hexdigest()
		filePath = "%d_%s" % (nowtime, md5str)
		db.insert("resources", 
				ctime=nowtime, 
				utime = nowtime,
				name = data["name"],
				filename = contentdata["content"].filename,
				description = data["description"], 
				path = filePath,
				md5 = md5str,
				filesize = len(content),
				privilege=data["privilege"])
		resultList = db.query("select last_insert_id() as resource_id").list();
		# save filedb
		orgresourcePath = config.filedb + 'resources/other/' + filePath
		if path.exists( path.dirname(orgresourcePath) ) is False:
			os.makedirs( path.dirname(orgresourcePath) )
		outOrgImg = file(orgresourcePath, 'w')
		outOrgImg.write(content)
		outOrgImg.flush()
		outOrgImg.close()

		resourceid = resultList[0]["resource_id"]
		# save category
		data = web.input()
		db.insert("res_category_link",
				category_id = data["categoryid"],
				resource_id = int(resourceid))
		return resourceid

	def __update__(self, resourceid):
		curwhere = "resource_id=%d" % (int(resourceid))
		data = web.input()
		db.update("resources", 
				where=curwhere, 
				name=data["name"], 
				description=data["description"], 
				utime=int(time.time()),
				privilege=data["privilege"])
		db.update("res_category_link",
				category_id = data["categoryid"],
				where="resource_id=%d" % (int(resourceid)))

class resourcedelete:
	def GET(self, resourceid):
		pass

	def POST(self, resourceid):
		try:
			if privilege() < 1:
				raise Exception("privilege is error")
			curwhere = "resource_id=%d" % (int(resourceid))
			curlist = db.select("resources", what="path", 
					where=curwhere).list()
			if len(curlist) != 0:
				self.__deleteFile__(curlist[0]["path"])
			db.delete("resources", where=curwhere)
			web.header("content-type", "application/json")
			return json.dumps({'desc': 'success'})
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

	def __deleteFile__(self, filePath):
		try:
			imagePath_Org = config.filedb + 'resources/other/' + filePath
			os.remove(imagePath_Org)
		except Exception, err:
			return '{"desc": "%s"}' % (err)

class resourcelist:
	def GET(self, categoryid=0, pageindex=1, count=8):
		web.header("content-type", "application/json")
		if int(categoryid) == 0:
			return self.__all__(categoryid, pageindex, count)
		else:
			return self.__gettype__(categoryid, pageindex, count)

	def __all__(self, categoryid, pageindex=1, count=8):
		try:
			offset = int(count)
			start = (int(pageindex) - 1) * offset
			query = "select resources.resource_id as resource_id, " \
					"resources.filename as name, " \
					"resources.description as description, " \
					"resources.ctime as ctime, " \
					"resources.utime as utime, " \
					"resources.md5 as md5, " \
					"resources.path as path, " \
					"resources.filesize as filesize, " \
					"res_category_link.category_id as category_id " \
					"from resources left outer join " \
					"res_category_link on res_category_link.resource_id = resources.resource_id " \
					"where resources.privilege <= %d order by utime desc " \
					"limit %d, %d;" % (privilege(), start, offset)
			curlist = db.query(query).list()
			resourcelist = []
			for item in curlist:
				resourceitem = {}
				resourceitem["resourceid"] = item["resource_id"]
				resourceitem["name"] = item["name"]
				resourceitem["desc"] = item["description"]
				resourceitem["ctime"] = time.strftime("%Y-%m-%d %H:%M:%S" , 
						time.localtime(item["ctime"]))
				resourceitem["utime"] = time.strftime("%Y-%m-%d %H:%M:%S" , 
						time.localtime(item["utime"]))
				resourceitem["md5"] = item["md5"]
				resourceitem["filesize"] = item["filesize"]
				resourceitem["resurl"] = "/rest/resource/download/%s" \
						% (item['resource_id'])
				if item["category_id"] is not None:
					resourceitem["category_id"] = item["category_id"]
				else:
					resourceitem["category_id"] = 0
				resourcelist.append(resourceitem)
			return json.dumps(resourcelist, ensure_ascii=False)
		except Exception, err:
			web.BadRequest()
			return '{"desc": "%s"}' % (err)

	def __gettype__(self, categoryid, pageindex=1, count=8):
		try:
			categoryid = int(categoryid)
			offset = int(count)
			start = (int(pageindex) - 1) * offset
			curwhere = "resources.privilege <= %d " \
					"and res_category_link.category_id=%d " \
					"and res_category_link.resource_id=resources.resource_id" \
					% (privilege(), categoryid)
			what="resources.resource_id as resource_id, " \
					"resources.filename as name, " \
					"resources.description as description, " \
					"resources.ctime as ctime, " \
					"resources.utime as utime, " \
					"resources.md5 as md5, " \
					"resources.path as path, " \
					"resources.filesize as filesize, " \
					"res_category_link.category_id as category_id "
			order = "utime desc"
			curlist = db.select("resources, res_category_link", 
					what=what, where=curwhere, order=order, 
					limit="%d, %d" % (start,offset)).list()
			resourcelist = []
			for item in curlist:
				resourceitem = {}
				resourceitem["resourceid"] = item["resource_id"]
				resourceitem["name"] = item["name"]
				resourceitem["desc"] = item["description"]
				resourceitem["ctime"] = time.strftime("%Y-%m-%d %H:%M:%S" , 
						time.localtime(item["ctime"]))
				resourceitem["utime"] = time.strftime("%Y-%m-%d %H:%M:%S" , 
						time.localtime(item["utime"]))
				resourceitem["md5"] = item["md5"]
				resourceitem["filesize"] = item["filesize"]
				resourceitem["resurl"] = "/rest/resource/download/%s" \
						% (item['resource_id'])
				resourceitem["category_id"] = categoryid
				resourcelist.append(resourceitem)
			return json.dumps(resourcelist, ensure_ascii=False)
		except Exception, err:
			web.BadRequest()
			return '{"desc": "%s"}' % (err)

class resourcelist_err:
	def GET(self, pageindex=1, count=8):
		try:
			offset = int(count)
			start = (int(pageindex) - 1) * offset
			curwhere = "privilege <= %d" % (privilege())
			order = "ctime desc"
			curlist = db.select("resources", 
					what="resource_id, ctime, utime, name, "\
							"description, path, md5, filesize",
					where=curwhere, order=order, 
					limit="%d, %d" % (start,offset)).list()

			resourcelist = []
			for resourceiter in curlist:
				resources = {}
				resources["resourceid"] = resourceiter["resource_id"]
				resources["name"] = resourceiter["name"]
				resources["desc"] = resourceiter["description"]
				resources["time"] = time.strftime("%Y-%m-%d", 
						time.localtime(resourceiter["ctime"]))
				resources["updated"] = time.strftime("%Y-%m-%d",
						time.localtime(resourceiter["utime"]))
				resources["resurl"] = "/mydb/resources/other/%d/" \
						% (resources["path"])
				resources["md5"] = resources["md5"]
				resources["filesize"] = resources["filesize"]
				resourcelist.append(resources)
			web.header("content-type", "application/json")
			return json.dumps(resourcelist, ensure_ascii=False)
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)


urls = (# rest router
		"/list/([1-9][0-9]{0,2})/([1-9][0-9]{0,1})/?", "resourcelist",
		"/([1-9][0-9]{0,9})/?", "resource",
		"/add/?", "resource",
		"/([1-9][0-9]{0,9})/delete/?", "resourcedelete",
		"/download/([0-9]+)/?", "resourceDownload",
		"", "reres",
		"/", "resourcecount")

app_resource = web.application(urls, globals(), autoreload=config.autoreload)

