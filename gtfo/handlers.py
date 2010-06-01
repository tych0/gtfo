import web
from markdown2 import markdown
from os.path import splitext
from util import build_root_nav_list, Meta
from gtfo import conf

PASSTHROUGH_EXTENSIONS = ['.txt', '.gpx', '.jpg', '.pdf']

urls = (
  "/config", "config",
  "/(.*)", "GTFO",
)
       
render = web.template.render('templates/')
web.template.Template.globals['render'] = render
web.template.Template.globals['navlist'] = build_root_nav_list('www')
web.template.Template.globals['conf'] = conf

class config:
  def GET(self):
    return "no info yet"

class GTFO:
  def GET(self, path=None):
    if not path: 
      path = conf.get('navigation', 'default_slug')
    (slug, ext) = splitext(path)
    ext = ext.lower()

    if ext in PASSTHROUGH_EXTENSIONS:
      try:
        return open('www/'+path).read()
      except IOError:
        return web.webapi.notfound()

    basename = 'www/'+slug
    meta = Meta(basename+'.meta')
    try:
      return render.template(meta, markdown(open(basename+'.mkd').read()))
    except IOError:
      pass

    try:
      return render.template(meta, open('www/'+slug+'.html').read())
    except IOError:
      return web.webapi.notfound()

app = web.application(urls, globals())
