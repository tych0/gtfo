import web
from markdown2 import markdown
from os.path import splitext
from util import build_root_nav_list

PASSTHROUGH_EXTENSIONS = ['.txt', '.gpx', '.jpg', '.pdf']

urls = (
  "/(.*)", "GTFO",
)
       
render = web.template.render('templates/')
web.template.Template.globals['render'] = render
web.template.Template.globals['navlist'] = build_root_nav_list('www')

class GTFO:
  def GET(self, path=None):
    if not path: path='index'
    (slug, ext) = splitext(path)
    ext = ext.lower()

    if ext in PASSTHROUGH_EXTENSIONS:
      try:
        return open('www/'+path).read()
      except IOError:
        return web.webapi.notfound()

    try:
      return render.template('hi there', markdown(open('www/'+slug+'.mkd').read()))
    except IOError:
      pass

    try:
      return render.template('', open('www/'+slug+'.html').read())
    except IOError:
      return web.webapi.notfound()

app = web.application(urls, globals())
