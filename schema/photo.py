#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json
import cStringIO as StringIO
import Image

import web
import cgi

cgi.maxlen = 10 * 1024 * 1024 # 10MB

db = web.database(dbn='mysql', 
		user='webadmin', 
		pw='webadmin791127', 
		host='localhost', 
		db='myblog')

# The EXIF tag that holds orientation data.
EXIF_ORIENTATION_TAG = 274

# Obviously the only ones to process are 3, 6 and 8.
# All are documented here for thoroughness.
ORIENTATIONS = {
		1: ("Normal", 0),
		2: ("Mirrored left-to-right", 0),
		3: ("Rotated 180 degrees", 180),
		4: ("Mirrored top-to-bottom", 0),
		5: ("Mirrored along top-left diagonal", 0),
		6: ("Rotated 90 degrees", -90),
		7: ("Mirrored along top-right diagonal", 0),
		8: ("Rotated 270 degrees", -270)
		}

def privilege():
	return web.config["_session"].privilege

class rephoto:
	def GET(self): raise web.seeother('/')

class photocount:
	def GET(self):
		try:
			curwhere = "privilege <= %d" % (privilege())
			curset = db.select("photo", what="count(createtime) as total", 
					where=curwhere).list()
			#query = ("select count(createtime) as total from photo "
			#		"where privilege <= %d") % (privilege())
			#curset = db.query(query)
			web.header("content-type", "application/json")
			return json.dumps({'count': curset[0]["total"]}, ensure_ascii=False)
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

class photocontent:
	def GET(self, photoid):
		try:
			curwhere = "createtime='%s' and privilege <= %d" % (photoid, privilege())
			curlist = db.select("photo", what="name, description, privilege", 
					where=curwhere).list()
			if len(curlist) is None:
				raise Exception("can't find image")
			buf = {}
			buf["name"] = curlist[0]["name"]
			buf["description"] = curlist[0]["description"]
			buf["imgphoto"] = "/rest/photo/%s/600" % (photoid)
			buf["privilege"] = curlist[0]["privilege"]
			web.header('content-type', "application/json")
			return json.dumps(buf, ensure_ascii=False)
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

	def POST(self, photoid):
		try:
			if privilege() < 1:
				raise Exception("privilege is error")
			curwhere = "createtime='%s'" % (photoid)
			curlist = db.select("photo", what="createtime", where=curwhere).list()
			if len(curlist) == 0:
				self.__insert__(photoid)
			else:
				self.__update__(photoid)
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

	def __insert__(self, photoid):
		itype = {"jpeg": 0, "png": 1}
		data = web.input()
		content = buffer(data["content"])
		fstr = StringIO.StringIO(content)
		im = Image.open(fstr);
		db.insert("photo", createtime=photoid, name=data["name"],
				description=data["description"], updated=int(time.time()),
				imagetype=itype[im.format.lower()], image=content,
				privilege=data["privilege"])
		fstr.close()

	def __update__(self, photoid):
		curwhere = "createtime='%s'" % (photoid)
		data = web.input()
		db.update("photo", where=curwhere, name=data["name"], 
				description=data["description"], updated=int(time.time()),
				privilege=data["privilege"])

class photodelete:
	def GET(self, photoid):
		pass

	def POST(self, photoid):
		try:
			if privilege() < 1:
				raise Exception("privilege is error")
			curwhere = "createtime='%s'" % (photoid)
			db.delete("photo", where=curwhere)
			web.header("content-type", "application/json")
			return json.dumps({'desc': 'success'})
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

class photo:
	def GET(self, photoid, scale):
		itype = {0:"image/jpeg", 1:"image/png"}
		itypename = {0: "jpeg", 1:"png"}
		try:
			curwhere = "createtime='%s' and privilege <= %d" % (photoid, privilege())
			curlist = db.select("photo", what="image, imagetype", 
					where=curwhere).list()
			if len(curlist) == 0:
				raise Exception("can't find image")
			buf = curlist[0]["image"]
			imagetype = curlist[0]["imagetype"]
			scale = int(scale)
			if scale != 1:
				buf = self.__getscalephoto__(itypename[imagetype], buf, scale)
			web.header('content-type', itype[imagetype])
			return buf
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

	def __getscalephoto__(self, imagetype, buf, scale):
		try:
			fstr = StringIO.StringIO(buf)
			outstr = StringIO.StringIO()
			im = Image.open(fstr)
			rate = float(scale)/float(im.size[1])
			size = (im.size[0] * rate, im.size[1] * rate)
			im = self.__fix_orientation__(im)
			im.thumbnail(size, Image.ANTIALIAS)
			im.save(outstr, imagetype)
			retdata = outstr.getvalue()
			outstr.close()
			fstr.close()
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

class photolist:
	def GET(self, pageindex=1, count=8):
		try:
			offset = int(count)
			start = (int(pageindex) - 1) * offset
			curwhere = "privilege <= %d" % (privilege())
			order = "createtime desc"
			curlist = db.select("photo", 
					what="createtime, name, description, updated, image",
					where=curwhere, order=order, 
					limit="%d, %d" % (start,offset)).list()

			photolist = []
			for photoiter in curlist:
				photo = {}
				photo["photoid"] = photoiter["createtime"]
				photo["name"] = photoiter["name"]
				photo["desc"] = photoiter["description"]
				photo["time"] = time.strftime("%Y-%m-%d", 
						time.localtime(photoiter["createtime"]))
				photo["updated"] = time.strftime("%Y-%m-%d",
						time.localtime(photoiter["updated"]))
				photo["small-photo"] = "/filedb/photo/80/%s" % (photoiter["image"])
				photo["big-photo"] = "/filedb/photo/600/%s" % (photoiter["image"])
				photolist.append(photo)
			web.header("content-type", "application/json")
			return json.dumps(photolist, ensure_ascii=False)
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)


urls = (# rest router
		"/list/([1-9][0-9]{0,2})/([1-9][0-9]{0,1})/?", "photolist",
		"/([1-9][0-9]{9})/([0-9]{1,4})/?", "photo",
		"/([1-9][0-9]{9})/?", "photocontent",
		"/([1-9][0-9]{9})/delete/?", "photodelete",
		"", "rephoto",
		"/", "photocount")

app_photo = web.application(urls, locals())

