#!/usr/bin/env python
# encoding: utf-8

import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

class Code2Html(object):
	def __init__(self):
		self._holders = []

	def convertBeforeWiki(self, content):
		result = re.subn(r'{{{.*?}}}', self._createHolder, content, flags=re.DOTALL)
		return result[0]

	def convertAfterWiki(self, content):
		result = re.subn(r'{{{\d+}}}', self._replaceHolder, content, flags=re.DOTALL)
		return result[0]

	def _createHolder(self, content):
		result = re.search(r'^{{{!([^\n]*)(.*?)}}}', 
				content.group(), 
				flags=re.DOTALL)
		if result:
			lang = result.group(1)
			code = result.group(2)
			if lang and code:
				lexer = get_lexer_by_name(result.group(1), stripall=True)
				code = highlight(code, 
						lexer, 
						HtmlFormatter()).encode('utf-8')
				self._holders.append(code)
				return '{{{%d}}}' % len(self._holders)
		return None	

	def _replaceHolder(self, content):
		print self._holders
		if self._holders:
			result = re.search(r'{{{(\d+)}}}', content.group(), flags=re.DOTALL)
			if result:
				idx = int(result.group(1))
				return self._holders[idx - 1]
		return None


def main():
	html0 = '''没有代码'''
	html1 = '''先测试下 python 代码

	{{{!python

	import socket

	def hello():
		print 'hello world'

	class ThisTest():
		def __init(self):
			pass

		def work(self):
			print socket.gethostname()

	}}}

	貌似能用

	在测试下 c++
	{{{!c++
	#include <iostream>
	int main(int argc, char* argv[])
	{
		std::cout << "hello world!" << std::end;
	}
	}}}

	结束
	'''
	first = Code2Html()
	result = first.convertBeforeWiki(html0)
	print first.convertAfterWiki(result)

	second = Code2Html()
	result = second.convertBeforeWiki(html1)
	print second.convertAfterWiki(result)

if __name__ == '__main__':
	main()

