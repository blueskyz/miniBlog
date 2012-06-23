#!/usr/bin/env python
# -*- coding: utf-8 -*-


import web.contrib.template as template

render = template.render_mako(directories=['py/templates'], input_encoding='utf-8',
		output_encoding='utf-8')

