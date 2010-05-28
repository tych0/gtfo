import web
import sys
import os

urls = [("/(.*)html", "ident"),
        ("/(.*)md", "markdown")
			 ]
render = web.template.render('templates/')
web.template.Template.globals['render'] = render

class ident:
	def GET(self, path):
		return open(path+'.html').read()

class markdown:
	def GET(self, path):
		return 'markdown not supported yet :('

class GTFO:
  def GET(self, path=None):
    if not path: path='index'
    return render.template('hi there', open('www/'+path).read())

app = web.application(urls, globals())
