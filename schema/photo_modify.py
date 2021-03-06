#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json
import cStringIO as StringIO
import Image
import MySQLdb
import os
import os.path as path


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

class photo:
	def SaveImageToScale(self, photoid, scale, srcdir, dstdir):
		itype = {0:"image/jpeg", 1:"image/png"}
		itypename = {0: "jpeg", 1:"png"}
		try:
			conn = MySQLdb.connect(user='webadmin', passwd='webadmin791127', db='myblog')
			cur = conn.cursor()
			sql= "select image, imagetype from photo where createtime>'%d'" % (photoid)
			cur.execute(sql)
			print sql
			record = cur.fetchone()
			count = 0
			while record is not None:
				(image, imagetype) = record
				imageFile = open( srcdir + '/' + image, 'r+b' )
				buf = imageFile.read()
				imageFile.close()
				buf = self.__getscalephoto__(itypename[imagetype], buf, scale)
				filePath = '%s/%d/%s' % ( dstdir, scale, image )
				if path.exists( path.dirname(filePath) ) is False:
					os.makedirs( path.dirname(filePath) )
				print 'write image:', filePath, " count: ", count
				imageFile = open( filePath, 'w+b' )
				imageFile.write( buf )
				imageFile.close( )
				record = cur.fetchone()
				count += 1
		except Exception, err:
			return '{"desc": "%s"}' % (err)

	def __getscalephoto__(self, imagetype, buf, scale):
		try:
			fstr = StringIO.StringIO(buf)
			outstr = StringIO.StringIO()
			im = Image.open(fstr)
			rate = float(scale)/float(im.size[1])
			size = (int(im.size[0] * rate), int(im.size[1] * rate))
			im = self.__fix_orientation__(im)
			print size
			im.thumbnail(size, Image.ANTIALIAS)
			im.save(outstr, imagetype)
			retdata = outstr.getvalue()
			outstr.close()
			fstr.close()
			return retdata
		except Exception, err:
			raise Exception("__getscalephoto__: " + err.message)

	def __fix_orientation__(self, im):
		try:
			orientation = im._getexif()[EXIF_ORIENTATION_TAG]
			if orientation in [3, 6, 8]:
				degrees = ORIENTATIONS[orientation][1]
				im = im.rotate(degrees)
			return im
		except Exception, err:
			return im

if __name__ == '__main__':
	obj = photo()
	ret = obj.SaveImageToScale(1277020143, 600, './preimport/org', './preimport')
	ret = obj.SaveImageToScale(1277020143, 80, './preimport/org', './preimport')
	print ret
