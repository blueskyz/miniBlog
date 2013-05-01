#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import time
import json
import web

import config
import myutil

db = myutil.db
privilege = myutil.privilege

class reblog:
	def GET(self): raise web.seeother('/')

class count:
	def GET(self, categoryid=None):
		try:
			query = ("select count(blog_id) as total from blog "
					"where privilege <= %d;") % (privilege())
			if int(categoryid) != 0:
				query = ("select count(category_link.category_id) as total "
						"from category_link left outer join blog "
						"on blog.blog_id = category_link.blog_id "
						"where blog.privilege <= %d and "
						"category_link.category_id = %d;") \
				%(privilege(), int(categoryid))
			curset = db.query(query)
			return json.dumps({'count': curset[0]["total"]}, ensure_ascii=False)
		except Exception, err:
			web.BadRequest()
			return '{"desc": "%s", "sql:" "%s"}' % (err, query)

class bloglist:
	def GET(self, categoryid=0, pageindex=1, count=8):
		if int(categoryid) == 0:
			return self.__all__(categoryid, pageindex, count)
		else:
			return self.__gettype__(categoryid, pageindex, count)

	def __all__(self, categoryid, pageindex=1, count=8):
		try:
			offset = int(count)
			start = (int(pageindex) - 1) * offset
			query = "select blog.blog_id as blog_id, blog.title as title, " \
					"blog.summary as summary, blog.published as published, " \
					"blog.updated as updated, " \
					"category_link.category_id as category_id " \
					"from blog left outer join " \
					"category_link on category_link.blog_id = blog.blog_id " \
					"where blog.privilege <= %d order by updated desc " \
					"limit %d, %d;" % (privilege(), start, offset)
			curlist = db.query(query).list()
			bloglist = []
			for item in curlist:
				blogitem = {}
				blogitem["blogid"] = item["blog_id"]
				blogitem["title"] = item["title"]
				blogitem["summary"] = item["summary"]
				blogitem["published"] = time.strftime("%Y-%m-%d %H:%M:%S" , 
						time.localtime(item["published"]))
				blogitem["updated"] = time.strftime("%Y-%m-%d %H:%M:%S" , 
						time.localtime(item["updated"]))
				blogitem["category_id"] = 0
				if item["category_id"] is not None:
					blogitem["category_id"] = item["category_id"]
				bloglist.append(blogitem)
			return json.dumps(bloglist, ensure_ascii=False)
		except Exception, err:
			web.BadRequest()
			return '{"desc": "%s"}' % (err)

	def __gettype__(self, categoryid, pageindex=1, count=8):
		try:
			offset = int(count)
			start = (int(pageindex) - 1) * offset
			curwhere = "blog.privilege <= %d and category_link.category_id=%s " \
					"and category_link.blog_id=blog.blog_id" % (privilege(), categoryid)
			what="blog.blog_id as blog_id, blog.title as title, " \
					"blog.summary as summary, blog.published as published, " \
					"blog.updated as updated"
			order = "updated desc"
			curlist = db.select("blog, category_link", 
					what=what, where=curwhere, order=order, 
					limit="%d, %d" % (start,offset)).list()
			bloglist = []
			categoryid = int(categoryid)
			for item in curlist:
				blogitem = {}
				blogitem["blogid"] = item["blog_id"]
				blogitem["title"] = item["title"]
				blogitem["summary"] = item["summary"]
				blogitem["published"] = time.strftime("%Y-%m-%d %H:%M:%S" , 
						time.localtime(item["published"]))
				blogitem["updated"] = time.strftime("%Y-%m-%d %H:%M:%S" , 
						time.localtime(item["updated"]))
				blogitem["category_id"] = categoryid
				bloglist.append(blogitem)
			return json.dumps(bloglist, ensure_ascii=False)
		except Exception, err:
			web.BadRequest()
			return '{"desc": "%s"}' % (err)


class category:
	def GET(self):
		try:
			categorylist = []
			# all category
			curwhere = "privilege <= %d" % (privilege())
			curlist = db.select("blog", what="count(blog_id) as count", 
					where=curwhere).list()
			category = {"count": curlist[0]["count"], "category_id": 0, 
					"name": u"所有日志", "description": u"所有日志"}
			categorylist.append(category)

			# other category
			query = "select category.category_id as category_id, " \
					"category.name as name, category.description as description, " \
					"count(category_link.category_id) as count " \
					"from (blog, category) left outer join category_link " \
					"on blog.blog_id = category_link.blog_id " \
					"and category.category_id=category_link.category_id " \
					"where blog.privilege <= %d " \
					"group by category.category_id;" % (privilege())
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


class blog:
	def GET(self, blogid=None):
		try:
			query = ("select blog.blog_id as blog_id, blog.title as title, " \
					"blog.summary as summary, blog.published as published, " \
					"blog.updated as updated, blog.content as content, " \
					"blog.privilege as privilege, " \
					"category_link.category_id as category_id " \
					"from blog left outer join category_link " \
					"on blog.blog_id = category_link.blog_id " \
					"where blog.blog_id='%s' and " \
					"blog.privilege <= %d;") % (blogid, privilege())
			curlist = db.query(query).list()
			if len(curlist) != 1:
				raise Exception("find blog is not one.[%d]" % (len(curlist)))
			item = curlist[0]
			bloglist = []
			blogitem = {}
			blogitem["blogid"] = item["blog_id"]
			blogitem["title"] = item["title"]
			blogitem["summary"] = item["summary"]
			blogitem["published"] = time.strftime("%Y-%m-%d %H:%M:%S" , 
					time.localtime(item["published"]))
			blogitem["updated"] = time.strftime("%Y-%m-%d %H:%M:%S" , 
					time.localtime(item["updated"]))
			blogitem["content"] = item["content"]
			blogitem["privilege"] = item["privilege"]
			blogitem["category_id"] = 0
			if item["category_id"] is not None:
				blogitem["category_id"] = item["category_id"]
			bloglist.append(blogitem)
			return json.dumps(bloglist, ensure_ascii=False)
		except Exception, err:
			web.BadRequest()
			return '{"desc": "%s"}' % (err)

	def POST(self, blogid):
		try:
			if privilege() < 1:
				raise Exception("privilege is error")
			selset = db.select("blog", where="blog_id=$blogid", 
					vars=locals(), what="blog_id").list()
			data = json.loads(web.data())
			if len(selset)==0:
				db.insert("blog", blog_id=int(blogid), title=data["title"], 
						summary=data["summary"], updated=int(blogid), 
						published=int(blogid), content=data["content"],
						privilege=data["privilege"])
				if data["category_id"] != 0:
					db.insert("category_link", blog_id=int(blogid), 
							category_id=data["category_id"])
			elif data["action"] == "update":
				db.update("blog", where="blog_id=$blogid", vars=locals(), 
						summary=data["summary"], title=data["title"], 
						updated=int(time.time()), content=data["content"],
						privilege=data["privilege"])
				if data["category_id"] == 0:
					db.delete("category_link", where="blog_id=" + blogid)
				else:
					result = db.select("category_link", what="blog_id", 
							where="blog_id=%s" % (blogid)).list()
					if len(result) == 0: # insert
						db.insert("category_link", blog_id=int(blogid), 
								category_id=data["category_id"])
					else: # update
						db.update("category_link", category_id=data["category_id"],
								where="blog_id=%s" % (blogid))
			elif data["action"] == "delete":
				db.delete("blog", where="blog_id=" + blogid)
				db.delete("category_link", where="blog_id=" + blogid)
			return json.dumps({'desc': 'success'})
		except Exception, err:
			web.BadRequest()
			return '{"desc": "%s"}' % (err)

urls = (# rest router
		"/category/?", "category",
		"/category/([0-9]{1,2})/count/?", "count",
		"/category/([0-9]{1,2})/([1-9][0-9]{0,2})/([1-9][0-9]{0,1})/?", "bloglist",
		"/([1-9][0-9]{9})/?", "blog",
		"", "reblog")

app_blog = web.application(urls, globals(), autoreload=config.autoreload)

