from os.path import splitext

import web

from markdown2 import markdown

from gtfo import conf
from util import *
from comments import reply_form

# TODO: move this to a config option
PASSTHROUGH_EXTENSIONS = ['.txt', '.gpx', '.jpg', '.pdf']

# our URL structure
urls = (
  "/config", "config",
  "/(.*)/comment", "Comment",
  "/(.*)", "GTFO",
)

# set up the DB
# sqlite3 gtfo.db "create table comments (
#    id INTEGER PRIMARY KEY, slug TEXT,
#    name TEXT, url TEXT, email TEXT, payload TEXT,
#    time DATETIME DEFAULT(DATETIME('NOW')));"
db = web.database(dbn='sqlite', db='gtfo.db')

# set up some 'globals' for use inside of the templates
render = web.template.render('templates/')
web.template.Template.globals['render'] = render
web.template.Template.globals['navlist'] = build_root_nav_list('www')
web.template.Template.globals['conf'] = conf
web.template.Template.globals['get_front_page_posts'] = lambda: get_front_page_posts(db)
web.template.Template.globals['get_sidebar_posts'] = lambda: get_sidebar_posts(db)
web.template.Template.globals['recent_comments'] = lambda: recent_comments(db)

# TODO: implement
class config:
  def GET(self):
    return "no info yet"

class GTFO:
  """ This class handles the bulk of the GTFO requests. For backwards
  compatability (and/or users who like to have more control over certain pages)
  it will try to render raw .html documents matching the requested slug before
  it tries to render the corrosponding .gtf file. """
  def GET(self, path=None, reply=reply_form()):
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
    comments = db.select('comments', {'slug' : slug}, where="slug = $slug", order="time DESC")
    try:
      gtf = GTF(basename+'.gtf')
      return render.single_page(gtf.meta, markdown(gtf.markdown), list(comments), reply)
    except IOError:
      pass

    try:
      return render.single_page(Meta(slug), 
                                open('www/'+slug+'.html').read(), 
                                list(comments), 
                                reply
                               )
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
    if not reply.validates():
      return GTFO().GET(path, reply)
    else:
      db.insert('comments', slug=path, **reply.d)
      return web.redirect('/'+path)

app = web.application(urls, globals())
