import web
from markdown2 import markdown
from os.path import splitext
from util import build_root_nav_list

urls = (
  "/(.*)", "GTFO",
)
       
render = web.template.render('templates/')
web.template.Template.globals['render'] = render
web.template.Template.globals['navlist'] = build_root_nav_list('www')

class GTFO:
  def GET(self, path=None):
    if not path: path='index'
    path = splitext(path)[0]

    try:
      return render.template('hi there', markdown(open('www/'+path+'.mkd').read()))
    except IOError:
      pass

    try:
      return render.template('', open('www/'+path+'.html').read())
    except IOError:
      return web.webapi.notfound()

app = web.application(urls, globals())
