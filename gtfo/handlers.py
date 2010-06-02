import web
from markdown2 import markdown
from os.path import splitext
from util import build_root_nav_list, GTF, Meta
from gtfo import conf

# TODO: move this to a config option
PASSTHROUGH_EXTENSIONS = ['.txt', '.gpx', '.jpg', '.pdf']

# our URL structure
urls = (
  "/config", "config",
  "/(.*)/comment", "Comment",
  "/(.*)", "GTFO",
)
       
# set up some 'globals' for use inside of the templates
from comments import reply_form
render = web.template.render('templates/')
web.template.Template.globals['render'] = render
web.template.Template.globals['navlist'] = build_root_nav_list('www')
web.template.Template.globals['conf'] = conf
web.template.Template.globals['reply_form'] = reply_form

# set up the DB
# sqlite3 gtfo.db "create table comments (
#    id INTEGER PRIMARY KEY, slug TEXT,
#    name TEXT, url TEXT, email TEXT, payload TEXT,
#    time DATETIME DEFAULT(DATETIME('NOW')));"
db = web.database(dbn='sqlite', db='gtfo.db')

# TODO: implement
class config:
  def GET(self):
    return "no info yet"

class GTFO:
  """ This class handles the bulk of the GTFO requests. For backwards
  compatability (and/or users who like to have more control over certain pages)
  it will try to render raw .html documents matching the requested slug before
  it tries to render the corrosponding .gtf file. """
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

    # TODO: this ({www/, rendering .html first}) should probably be
    # configurable
    basename = 'www/'+slug
    try:
      gtf = GTF(basename+'.gtf')
      comments = db.select('comments', {'slug' : slug}, where="slug = $slug", order="time DESC")
      return render.template(gtf.meta, markdown(gtf.markdown), comments)
    except IOError:
      pass

    try:
      print 'falling back to html'
      return render.template(Meta(slug), open('www/'+slug+'.html').read(), [])
    except IOError:
      return web.webapi.notfound()

class Comment:
  def GET(self, path):
    # If someone creates a slug ending in 'comment', we might end up here. In
    # that case, we should really just render that slug. If users are trying to
    # 'GET' to post a comment... well then they're not playing nice :(
    return GTFO().GET(path+'/comment')

  def POST(self, path):
    reply = reply_form(web.input())
    print reply.d
    db.insert('comments', slug=path, **reply.d)
    return web.redirect('/'+path)

app = web.application(urls, globals())
