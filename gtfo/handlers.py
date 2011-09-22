from os.path import splitext, join
from sys import stderr

import web

from markdown2 import markdown

from gtfo import conf
from util import *
from comments import reply_form
from content import Content

# TODO: move this to a config option
PASSTHROUGH_EXTENSIONS = ['.txt', '.gpx', '.jpg', '.pdf', '.css']

# our URL structure
urls = (
  "/config", "config",
  "/blog", "Blog",
  "/tags/(.*)", "Tags",
  "/(.*)/comment", "Comment",
  "/(.*)", "GTFO",
)

# set up the DB; you can use the following command to do it:
# sqlite3 gtfo.db "create table comments (
#    id INTEGER PRIMARY KEY, slug TEXT,
#    name TEXT, url TEXT, email TEXT, payload TEXT,
#    time DATETIME DEFAULT(DATETIME('NOW')));"
db = web.database(dbn='sqlite', db=conf.system.db_location)

# set up some 'globals' for use inside of the templates
render = web.template.render('templates/')
web.template.Template.globals['render'] = render
web.template.Template.globals['navlist'] = build_root_nav_list()
web.template.Template.globals['conf'] = conf
web.template.Template.globals['get_front_page_posts'] = lambda: get_front_page_posts(db)
web.template.Template.globals['get_sidebar_posts'] = get_sidebar_posts
web.template.Template.globals['get_sidebar_calendar'] = get_sidebar_calendar
web.template.Template.globals['get_tags'] = get_tags
web.template.Template.globals['recent_comments'] = lambda: recent_comments(db)

# TODO: implement support for changing certain configuration options via an
# admin interface (maybe)
class config:
  def GET(self):
    return "no info yet"

class GTFO(object):
  """ This class handles the bulk of the GTFO requests. For backwards
  compatability (and/or users who like to have more control over certain pages)
  it will try to render raw .html documents matching the requested slug before
  it tries to render the corrosponding .gtf file. """
  def GET(self, path=None, reply=None):
    if not path: 
      path = conf.navigation.default_slug
      return PrettyRedirect('/'+path)
    (slug, ext) = splitext(path)
    ext = ext.lower()

    if not reply:
      reply = reply_form()

    if ext in PASSTHROUGH_EXTENSIONS:
      try:
        return open(join(conf.siteopts.root, path)).read()
      except IOError:
        return web.notfound()

    if os.path.isdir(join(conf.siteopts.root, slug)):
      return render.multiple_pages('Posts in '+slug, 
                                   get_gtf_in_slug(slug))

    comments = get_comments_for_slug(slug, db)
    
    try:
      content = Content(slug)
      return render.single_page(content, reply)
    except IOError:
      raise web.notfound()

class Tags(object):
  def GET(self, tag):
    return render.multiple_pages('Tag: '+tag, get_posts_by_tag(tag))

class Blog(object):
  def GET(self):
    return render.multiple_pages('Blog', get_front_page_posts(db))

class Comment(object):
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
      gtf = GTF(path)
      comment = reply.d

      # no point in putting the capcha in the db
      del comment['capcha']

      db.insert('comments', slug=path, **comment)
      return PrettyRedirect('/'+path)

app = web.application(urls, globals())
