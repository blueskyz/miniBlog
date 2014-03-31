#!/usr/bin/env python
# encoding: utf-8

import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

class Code2Html(object):
	def convert(self, content):
		result = re.subn(r'{{{.*?}}}', self.replace, content, flags=re.DOTALL)
		return result[0]

	def replace(self, content):
		result = re.search(r'^{{{!([^\n]*)(.*?)}}}', 
				content.group(), 
				flags=re.DOTALL)
		if result:
			lang = result.group(1)
			code = result.group(2)
			if lang and code:
				pyLexer = get_lexer_by_name(result.group(1), stripall=True)
				code = highlight(code, 
						PythonLexer(), 
						HtmlFormatter()).encode('utf-8')
				return code
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
	print Code2Html().convert(html0)
	print Code2Html().convert(html1)

if __name__ == '__main__':
	main()

