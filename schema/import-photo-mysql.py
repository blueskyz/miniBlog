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
	def __init__( self, dir = None, sqliteFilePath = None, fileFilterExt = ['.jpg', '.png'] ):
		if dir is None:
			raise Exception( r'dir or sqliteFilePath is empty!' )
		self.__dir = dir
		self.__sqliteFilePath = sqliteFilePath
		self.__fileFilterExt = fileFilterExt
		print self.__dir, self.__sqliteFilePath

	def ImportPhoto( self ):
		""" Get photo list from dir. """
		timeline = 0
		try:
			#conn = sqlite.connect( self.__sqliteFilePath )
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

		if not path.isdir( self.__dir ) or not path.isfile( self.__sqliteFilePath ):
			raise Exception( r'dir is not directory or sqliteFilePath is not file!' )
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

	def SaveAllPhotoToFile( self, imageFilePath ):
		try:
			conn_mysql = mysql.connect( host='127.0.0.1', 
					user='webadmin', passwd='webadmin791127', db='myblog', charset='utf8')
			cur_mysql = conn_mysql.cursor()
			conn = sqlite.connect( self.__sqliteFilePath )
			cur = conn.cursor()
			cur.execute( "select createtime, year, month, name, description, imagetype, privilege, updated, image from photo" )
			record = cur.fetchone( )
			typeMap = { 0:'.jpg', 1:'.png' }
			while record is not None:
				( createtime, year, month, name, description, imagetype, privilege, updated, image ) = record
				print "----------------------------------------"
				print "CreateTime:  ", createtime, type(createtime)
				print "Year:  ", year
				print "Month:  ", month
				print "Name:  ", name
				print "Description:  ", description
				print "ImageType:  ", imagetype
				filePath = '%s/%s/%s/' % ( imageFilePath, year, month )

				# save mysql
				urlFilePath = '%d/%d/%d%s' % ( year, month, createtime, typeMap[imagetype] )
				print urlFilePath
				values = ( createtime, year, month, name, description, imagetype, urlFilePath, privilege, updated)
				cur_mysql.execute("insert into photo( createtime, year, month, name, description, imagetype, image, privilege, updated) values( %s,%s,%s,%s,%s,%s,%s,%s,%s )", values )

				# save file
				if path.exists( filePath ) is False:
					os.makedirs( filePath )
				imageFile = open( filePath + str( createtime ) + typeMap[imagetype], 'w+b' )
				imageFile.write( image )
				imageFile.close( )
				record = cur.fetchone( )
			cur.close()
			conn.close()
			cur_mysql.close()
			conn_mysql.close()
		except Exception, err:
			print err

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
			#conn = sqlite.connect( self.__sqliteFilePath )
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
				imageFilePath = '%s/%s/%d%s' % ( year, month, modifyTimeStat, type )
				print "image path: ", imageFilePath
				imageFile = open( filePath, 'r+b' )
				values = ( modifyTimeStat, year, month, name, description, typeMap[type], imageFilePath, modifyTimeStat)
				cur.execute("insert into photo( createtime, year, month, name, description, imagetype, image, updated) values( %s,%s,%s,%s,%s,%s,%s,%s )", values )
				imageFile.close( )
			conn.commit( )
			cur.close( )
			conn.close( )
		except Exception, err:
			print err


if __name__ == r'__main__':
	try:
		#photoObject = PhotoMgr( r'/resource/downloads/tmpphoto', r'./myphoto.dat' )
		photoObject = PhotoMgr( r'/resource/photo', r'./photo.dat' )
		#photoObject.ImportPhoto( )
		photoObject.SaveAllPhotoToFile( "/resource/photo/" )
	except Exception, err:
		print err

