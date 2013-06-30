#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path as path
import time
import json

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
			query = ("select count(resource_id) as total from resource"
					"where privilege <= %d;") % (privilege())
			if int(categoryid) != 0:
				query = ("select count(res_category_link.category_id) as total "
						"from res_category_link left outer join resource "
						"on resource.resource_id = res_category_link.resource_id "
						"where resource.privilege <= %d and "
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
			curlist = db.select("resource", what="count(resource_id) as count", 
					where=curwhere).list()
			category = {"count": curlist[0]["count"], "category_id": 0, 
					"name": u"所有日志", "description": u"所有日志"}
			categorylist.append(category)

			# other category
			query = "select res_category.category_id as category_id, " \
					"category.name as name, " \
					"res_category.description as description, " \
					"count(res_category_link.category_id) as count " \
					"from (resource, res_category) left outer join res_category_link " \
					"on resource.resource_id = res_category_link.resource_id " \
					"and res_category.category_id= res_category_link.category_id " \
					"where resource.privilege <= %d " \
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

class resourcecontent:
	def GET(self, resourceid):
		try:
			curwhere = "createtime='%s' and privilege <= %d" % (resourceid, privilege())
			curlist = db.select("resource", what="name, description, privilege, image", 
					where=curwhere).list()
			if len(curlist) is None:
				raise Exception("can't find image")
			buf = {}
			buf["name"] = curlist[0]["name"]
			buf["description"] = curlist[0]["description"]
			timepath = time.localtime(int(resourceid))
			buf["imgresource"] = "/resource/600/%s" % (curlist[0]['image'])
			buf["privilege"] = curlist[0]["privilege"]
			web.header('content-type', "application/json")
			return json.dumps(buf, ensure_ascii=False)
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

	def POST(self, resourceid):
		try:
			if privilege() < 1:
				raise Exception("privilege is error")
			curwhere = "createtime='%s'" % (resourceid)
			curlist = db.select("resource", what="createtime", where=curwhere).list()
			newId = resourceid
			if len(curlist) == 0:
				newId = self.__insert__(resourceid)
			else:
				self.__update__(resourceid)
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

	def __insert__(self, resourceid):
		itype = {"jpeg": 0, "png": 1}
		data = web.input()
		content = buffer(data["content"])
		fstr = StringIO.StringIO(content)
		(newresourceid, imgtypeStr) = self.__imgid__(resourceid, fstr)
		timeInfo = time.localtime(int(resourceid))
		imgExt = "jpg"
		if imgtypeStr == "png":
			imgExt = ".png"
		imagePath = "%d/%d/%d.%s" % (timeInfo.tm_year, timeInfo.tm_mon, newresourceid, imgExt)
		db.insert("resource", createtime=newresourceid, name=data["name"],
				description=data["description"], updated=int(time.time()),
				imagetype=itype[imgtypeStr], image=imagePath,
				privilege=data["privilege"])
		fstr.close()
		# save filedb
		orgresourcePath = config.filedb + 'resource/org/' + imagePath
		if path.exists( path.dirname(orgresourcePath) ) is False:
			os.makedirs( path.dirname(orgresourcePath) )
		outOrgImg = file(orgresourcePath, 'w')
		outOrgImg.write(content)
		outOrgImg.flush()
		outOrgImg.close()
		# 600 scale
		resourcePath_600 = config.filedb + 'resource/600/' + imagePath
		self.__createScalcresourceFile__(imgtypeStr, content, 600, resourcePath_600)

		# 80 scale
		resourcePath_80 = config.filedb + 'resource/80/' + imagePath
		self.__createScalcresourceFile__(imgtypeStr, content, 80, resourcePath_80)

	def __update__(self, resourceid):
		curwhere = "createtime='%s'" % (resourceid)
		data = web.input()
		db.update("resource", where=curwhere, name=data["name"], 
				description=data["description"], updated=int(time.time()),
				privilege=data["privilege"])

	def __imgid__(self, resourceid, fstr):
		im = Image.open(fstr)
		try:
			resourcetimestr = im._getexif()[36867]
			resourcetime = time.strptime(resourcetimestr, "%Y:%m:%d %H:%M:%S") 
			return (int(time.mktime(resourcetime)), im.format.lower())
		except Exception, err:
			return (int(resourceid), im.format.lower())

	def __createScalcresourceFile__(self, imagetype, buf, scale, filePath):
		content = self.__getScaleresource__(imagetype, buf, scale)
		if path.exists( path.dirname(filePath) ) is False:
			os.makedirs( path.dirname(filePath) )
		outOrgImg = file(filePath, 'w')
		outOrgImg.write(content)
		outOrgImg.flush()
		outOrgImg.close()

	def __getScaleresource__(self, imagetype, buf, scale):
		try:
			fstr = StringIO.StringIO(buf)
			im = Image.open(fstr)
			outstr = StringIO.StringIO()
			rate = float(scale)/float(im.size[1])
			size = (im.size[0] * rate, im.size[1] * rate)
			im = self.__fix_orientation__(im)
			im.thumbnail(size, Image.ANTIALIAS)
			im.save(outstr, imagetype)
			retdata = outstr.getvalue()
			fstr.close()
			outstr.close()
			return retdata
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

	def __fix_orientation__(self, im):
		try:
			orientation = im._getexif()[EXIF_ORIENTATION_TAG]
			if orientation in [3, 6, 8]:
				degrees = ORIENTATIONS[orientation][1]
				im = im.rotate(degrees)
			return im
		except Exception, err:
			return im


class resourcedelete:
	def GET(self, resourceid):
		pass

	def POST(self, resourceid):
		try:
			if privilege() < 1:
				raise Exception("privilege is error")
			curwhere = "createtime='%s'" % (resourceid)
			curlist = db.select("resource", what="image", 
					where=curwhere).list()
			if len(curlist) != 0:
				self.__deleteFile__(curlist[0]["image"])
			db.delete("resource", where=curwhere)
			web.header("content-type", "application/json")
			return json.dumps({'desc': 'success'})
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

	def __deleteFile__(self, filePath):
		try:
			imagePath_Org = config.filedb + 'resource/org/' + filePath
			os.remove(imagePath_Org)
			imagePath_600 = config.filedb + 'resource/600/' + filePath
			os.remove(imagePath_600)
			imagePath_80 = config.filedb + 'resource/80/' + filePath
			os.remove(imagePath_80)
		except Exception, err:
			return '{"desc": "%s"}' % (err)

class resource:
	def GET(self, resourceid, scale):
		itype = {0:"image/jpeg", 1:"image/png"}
		itypename = {0: "jpeg", 1:"png"}
		try:
			curwhere = "createtime='%s' and privilege <= %d" % (resourceid, privilege())
			curlist = db.select("resource", what="image, imagetype", 
					where=curwhere).list()
			if len(curlist) == 0:
				raise Exception("can't find image")
			scale= int(scale)
			if (scale== 80 or scale== 600):
				#web.header('content-type', itype[imagetype])
				web.header("x-accel-redirect", 
						"/filedb/resource/%d/%s" % (scale, curlist[0]["image"]))
				return
			if scale!= 1:
				imageFile = config.filedb + 'resource/org/' + curlist[0]["image"]
				imagetype = curlist[0]["imagetype"]
				buf = self.__getscaleresource__(itypename[imagetype], imageFile, scale)
				#web.header('content-type', itype[imagetype])
				return buf
			web.header('content-type', "application/json")
			buf = '{"desc": "failure", "image", "%s can\'t find"}' % (curlist[0]["image"])
			return buf
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

	def __getscaleresource__(self, imagetype, imageFile, scale):
		try:
			outstr = StringIO.StringIO()
			im = Image.open(imageFile)
			rate = float(scale)/float(im.size[1])
			size = (int(im.size[0] * rate), int(im.size[1] * rate))
			im = self.__fix_orientation__(im)
			im.thumbnail(size, Image.ANTIALIAS)
			im.save(outstr, imagetype)
			retdata = outstr.getvalue()
			outstr.close()
			return retdata
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

	def __fix_orientation__(self, im):
		try:
			orientation = im._getexif()[EXIF_ORIENTATION_TAG]
			if orientation in [3, 6, 8]:
				degrees = ORIENTATIONS[orientation][1]
				im = im.rotate(degrees)
			return im
		except Exception, err:
			return im

class resourcelist:
	def GET(self, pageindex=1, count=8):
		try:
			offset = int(count)
			start = (int(pageindex) - 1) * offset
			curwhere = "privilege <= %d" % (privilege())
			order = "createtime desc"
			curlist = db.select("resource", 
					what="createtime, name, description, updated, image",
					where=curwhere, order=order, 
					limit="%d, %d" % (start,offset)).list()

			resourcelist = []
			for resourceiter in curlist:
				resource = {}
				resource["resourceid"] = resourceiter["createtime"]
				resource["name"] = resourceiter["name"]
				resource["desc"] = resourceiter["description"]
				resource["time"] = time.strftime("%Y-%m-%d", 
						time.localtime(resourceiter["createtime"]))
				resource["updated"] = time.strftime("%Y-%m-%d",
						time.localtime(resourceiter["updated"]))
				resource["small-resource"] = "/rest/resource/%d/80/" % (resource["resourceid"])
				resource["big-resource"] = "/rest/resource/%d/600/" % (resource["resourceid"])
				resourcelist.append(resource)
			web.header("content-type", "application/json")
			return json.dumps(resourcelist, ensure_ascii=False)
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)


urls = (# rest router
		"/list/([1-9][0-9]{0,2})/([1-9][0-9]{0,1})/?", "resourcelist",
		"/([1-9][0-9]{9})/([0-9]{1,4})/?", "resource",
		"/([1-9][0-9]{9})/?", "resourcecontent",
		"/([1-9][0-9]{9})/delete/?", "resourcedelete",
		"", "repres",
		"/", "resourcecount")

app_resource = web.application(urls, globals(), autoreload=config.autoreload)

