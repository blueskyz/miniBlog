#!/usr/bin/python
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

class BlogMgr:
	def __init__( self, sqliteFilePath = None ):
		self.__sqliteFilePath = sqliteFilePath
		print self.__sqliteFilePath

	def ImportTable( self ):
		""" Save photo to database. """
		try:
			srcConn = sqlite.connect( self.__sqliteFilePath )
			dstConn = mysql.connect( host='127.0.0.1', user='webadmin', passwd='webadmin791127', db='myblog', charset='utf8')
			self.__ImportUsers(srcConn, dstConn)
			self.__ImportCategory(srcConn, dstConn)
			self.__ImportBlog(srcConn, dstConn)
			self.__ImportCategoryLink(srcConn, dstConn)

			srcConn.close()
			dstConn.close()
		except Exception, err:
			print err

	def __ImportUsers(self, srcConn, dstConn):
		field = "user_id, name, passwd, localname, email, description, mobile_phone, privilege"
		srcSql="select %s from users" % (field)
		dstSql="insert into users(%s) values(%s)" % (field, "%s,%s,%s,%s,%s,%s,%s,%s")
		self.__ImportTable(srcSql, dstSql, srcConn, dstConn)

	def __ImportCategory(self, srcConn, dstConn):
		field = "category_id, name, description"
		srcSql="select %s from category" % (field)
		dstSql="insert into category(%s) values(%s)" % (field, "%s,%s,%s")
		self.__ImportTable(srcSql, dstSql, srcConn, dstConn)

	def __ImportBlog(self, srcConn, dstConn):
		field =
		"blog_id,title,summary,permalink,link,status,published,updated,authors,privilege,config,content"
		srcSql="select %s from blog" % (field)
		dstSql="insert into blog(%s) values(%s)" % (field, "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s")
		self.__ImportTable(srcSql, dstSql, srcConn, dstConn)

	def __ImportCategoryLink(self, srcConn, dstConn):
		field = "category_link_id, category_id, blog_id"
		srcSql="select %s from category_link" % (field)
		dstSql="insert into category_link(%s) values(%s)" % (field, "%s,%s,%s")
		self.__ImportTable(srcSql, dstSql, srcConn, dstConn)

	def __ImportTable( self, srcSql, dstSql, srcConn, dstConn ):
		srcCur = srcConn.cursor()
		dstCur = dstConn.cursor()
		srcCur.execute(srcSql)
		record = srcCur.fetchone()
		while record is not None:
			print record
			dstCur.execute(dstSql, record);
			record = srcCur.fetchone()
		srcCur.close()
		dstCur.close()


if __name__ == r'__main__':
	try:
		print "aaaa"
		blogObject = BlogMgr( r'../blog.dat' )
		blogObject.ImportTable( )
	except Exception, err:
		print err

