#!/usr/bin/env python
# -*- encoding: utf-8 -*-

#
# photo table info
# create time ( main id index )
# name
# description
# create year
# create month
# type { jpg: 0, png: 1 }
#

import sys
import os
import os.path as path
import MySQLdb as mysql 
import sqlite3 as sqlite
import time
import Image

class PhotoMgr:
	def __init__( self, dir = None, destPath = None, fileFilterExt = ['.jpg', '.png'] ):
		print "dir: ", dir, " destPath: ", destPath
		if dir is None or destPath is None:
			raise Exception( r'dir or destPath is empty!' )
		self.__dir = dir
		self.__destPath = destPath
		self.__fileFilterExt = fileFilterExt
		print self.__dir, self.__destPath

	def ImportPhoto( self ):
		""" Get photo list from dir. """
		timeline = 0
		try:
			conn = mysql.connect( user='webadmin', passwd='webadmin791127', db='myblog', charset='utf8')
			cur = conn.cursor();
			cur.execute("select createtime from photo "
					"order by createtime desc limit 0,1")
			curset = cur.fetchone()
			if curset is not None:
				timeline = curset[0]
			print "timeline:", timeline
			cur.close()
			conn.close()
		except Exception, err:
			print err
			return

		if not path.isdir( self.__dir ) or not path.isdir( self.__destPath):
			raise Exception( r'dir is not directory or destPath is not directory!' )
		photoFileMap = {}
		dirList = [ self.__dir ]
		nFileCount = 0
		while True:
			if len( dirList ) == 0:
				break;
			curFiles = os.listdir( dirList[0] )
			tmpDirs = []
			for curStep in curFiles:
				curStepPath = dirList[0] + r'/' + curStep
				if path.isdir( curStepPath ):
					tmpDirs.append( curStepPath )
				elif path.isfile( curStepPath ) and path.splitext( curStepPath )[1].lower( ) in self.__fileFilterExt:
					modifyTimeStat = self.__phototime(curStepPath)
					if modifyTimeStat is None:
						print "Can't get timestamp", curStepPath
						break
					if modifyTimeStat > timeline:
						photoFileMap[modifyTimeStat]=curStepPath
					nFileCount = nFileCount + 1
			dirList = dirList[ 1: ]
			dirList = dirList + tmpDirs

		self.__SavePhotoToDB( photoFileMap )

		print timeline
		print r'total:  ', nFileCount
		print r'available:  ', len( photoFileMap )


	def __phototime( self, filepath ):
		#fileStat = os.stat( filepath )
		#modifyTimeStat = fileStat[-2]
		try:
			im = Image.open(filepath)
			phototimestr = im._getexif()[36867]
			phototime = time.strptime(phototimestr, "%Y:%m:%d %H:%M:%S") 
			return int(time.mktime(phototime))
		except Exception, err:
			print err, filepath, 'can not find time from file'
			timevalue = path.splitext(path.basename(filepath))[0]
			print 'get time from file name'
			return int(timevalue)

	def __SavePhotoToDB( self, photoFileMap ):
		""" Save photo to database. """
		try:
			conn = mysql.connect( host='127.0.0.1', user='webadmin', passwd='webadmin791127', db='myblog', charset='utf8')
			cur = conn.cursor( )

			for modifyTimeStat in photoFileMap:
				filePath = photoFileMap[modifyTimeStat]
				print filePath
				typeMap = {'.jpg':0, '.png':1 }
				modifyTime = time.localtime( modifyTimeStat )
				year = modifyTime[0]
				month = modifyTime[1]
				name = str( modifyTimeStat )
				description = ""
				type = path.splitext( filePath )[1].lower( )
				print "CreateTime id:  ", modifyTimeStat
				#print "Year:  ", year
				#print "Month:  ", month
				#print "Name:  ", name
				#print "Description:  ", description
				#print "ImageType:  ", type, typeMap[type]

				print "image src path: ", filePath
				# read src image file
				imageFile = open( filePath, 'r+b' )
				imageContent = imageFile.read(-1)
				imageFile.close()

				# save file
				imageFilePath = '%s/%s/%d%s' %(year, month, modifyTimeStat, type)
				destFilePath = '%s/%s/%s/' % ( self.__destPath, year, month )
				if path.exists( destFilePath ) is False:
					os.makedirs( destFilePath )
				destFilePath = destFilePath + str(modifyTimeStat) + type
				print "image dest Path: ", destFilePath 
				imageDestFile = open( destFilePath, 'w+b' )
				imageDestFile.write( imageContent )
				imageDestFile.close( )
				
				# save db
				values = ( modifyTimeStat, year, month, name, description, typeMap[type], imageFilePath, modifyTimeStat)
				cur.execute("insert into photo( createtime, year, month, name, description, imagetype, image, updated) values( %s,%s,%s,%s,%s,%s,%s,%s )", values )
			conn.commit( )
			cur.close( )
			conn.close( )
		except Exception, err:
			print err


if __name__ == r'__main__':
	try:
		#photoObject = PhotoMgr( r'/resource/downloads/tmpphoto', r'./myphoto.dat' )
		photoObject = PhotoMgr( r'/resource/photo', r'./preimport/org' )
		photoObject.ImportPhoto( )
	except Exception, err:
		print err

