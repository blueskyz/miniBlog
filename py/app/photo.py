#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path as path
import time
import json
import cStringIO as StringIO
import Image

import web
import cgi

import config

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
			curlist = db.select("photo", what="name, description, privilege, image", 
					where=curwhere).list()
			if len(curlist) is None:
				raise Exception("can't find image")
			buf = {}
			buf["name"] = curlist[0]["name"]
			buf["description"] = curlist[0]["description"]
			timepath = time.localtime(int(photoid))
			buf["imgphoto"] = "/photo/600/%s" % (curlist[0]['image'])
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
			newId = photoid
			if len(curlist) == 0:
				newId = self.__insert__(photoid)
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
		(newphotoid, imgtypeStr) = self.__imgid__(photoid, fstr)
		timeInfo = time.localtime(int(photoid))
		imgExt = "jpg"
		if imgtypeStr == "png":
			imgExt = ".png"
		imagePath = "%d/%d/%d.%s" % (timeInfo.tm_year, timeInfo.tm_mon, newphotoid, imgExt)
		db.insert("photo", createtime=newphotoid, name=data["name"],
				description=data["description"], updated=int(time.time()),
				imagetype=itype[imgtypeStr], image=imagePath,
				privilege=data["privilege"])
		fstr.close()
		# save filedb
		orgphotoPath = config.filedb + 'photo/org/' + imagePath
		if path.exists( path.dirname(orgphotoPath) ) is False:
			os.makedirs( path.dirname(orgphotoPath) )
		outOrgImg = file(orgphotoPath, 'w')
		outOrgImg.write(content)
		outOrgImg.flush()
		outOrgImg.close()
		# 600 scale
		photoPath_600 = config.filedb + 'photo/600/' + imagePath
		self.__createScalcPhotoFile__(imgtypeStr, content, 600, photoPath_600)

		# 80 scale
		photoPath_80 = config.filedb + 'photo/80/' + imagePath
		self.__createScalcPhotoFile__(imgtypeStr, content, 80, photoPath_80)

	def __update__(self, photoid):
		curwhere = "createtime='%s'" % (photoid)
		data = web.input()
		db.update("photo", where=curwhere, name=data["name"], 
				description=data["description"], updated=int(time.time()),
				privilege=data["privilege"])

	def __imgid__(self, photoid, fstr):
		im = Image.open(fstr)
		try:
			phototimestr = im._getexif()[36867]
			phototime = time.strptime(phototimestr, "%Y:%m:%d %H:%M:%S") 
			return (int(time.mktime(phototime)), im.format.lower())
		except Exception, err:
			return (int(photoid), im.format.lower())

	def __createScalcPhotoFile__(self, imagetype, buf, scale, filePath):
		content = self.__getScalePhoto__(imagetype, buf, scale)
		if path.exists( path.dirname(filePath) ) is False:
			os.makedirs( path.dirname(filePath) )
		outOrgImg = file(filePath, 'w')
		outOrgImg.write(content)
		outOrgImg.flush()
		outOrgImg.close()

	def __getScalePhoto__(self, imagetype, buf, scale):
		try:
			fstr = StringIO.StringIO(buf)
			im = Image.open(fstr)
			outstr = StringIO.StringIO()
			rate = float(scale)/float(im.size[1])
			size = (int(im.size[0] * rate), int(im.size[1] * rate))
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


class photodelete:
	def GET(self, photoid):
		pass

	def POST(self, photoid):
		try:
			if privilege() < 1:
				raise Exception("privilege is error")
			curwhere = "createtime='%s'" % (photoid)
			curlist = db.select("photo", what="image", 
					where=curwhere).list()
			if len(curlist) != 0:
				self.__deleteFile__(curlist[0]["image"])
			db.delete("photo", where=curwhere)
			web.header("content-type", "application/json")
			return json.dumps({'desc': 'success'})
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

	def __deleteFile__(self, filePath):
		try:
			imagePath_Org = config.filedb + 'photo/org/' + filePath
			os.remove(imagePath_Org)
			imagePath_600 = config.filedb + 'photo/600/' + filePath
			os.remove(imagePath_600)
			imagePath_80 = config.filedb + 'photo/80/' + filePath
			os.remove(imagePath_80)
		except Exception, err:
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
			imagetype = curlist[0]["imagetype"]
			scale= int(scale)
			if (scale== 80 or scale== 600):
				web.header('content-type', itype[imagetype])
				web.header("x-accel-redirect", 
						"/filedb/photo/%d/%s" % (scale, curlist[0]["image"]))
				return
			if scale!= 1:
				imageFile = config.filedb + 'photo/org/' + curlist[0]["image"]
				buf = self.__getscalephoto__(itypename[imagetype], imageFile, scale)
				#web.header('content-type', itype[imagetype])
				return buf
			web.header('content-type', "application/json")
			buf = '{"desc": "failure", "image", "%s can\'t find"}' % (curlist[0]["image"])
			return buf
		except Exception, err:
			web.BadRequest()
			web.header("content-type", "application/json")
			return '{"desc": "%s"}' % (err)

	def __getscalephoto__(self, imagetype, imageFile, scale):
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
				#photo["small-photo"] = "/rest/photo/%d/80" % (photo["photoid"])
				#photo["big-photo"] = "/rest/photo/%d/600" % (photo["photoid"])
				photo["small-photo"] = "/mydb/photo/80/%s" % (photoiter["image"])
				photo["big-photo"] = "/mydb/photo/600/%s" % (photoiter["image"])
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

app_photo = web.application(urls, globals(), autoreload=config.autoreload)

