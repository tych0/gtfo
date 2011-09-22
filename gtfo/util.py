from __future__ import with_statement

import os, urlparse, web
from os.path import join, splitext
from datetime import date
from itertools import islice
from collections import defaultdict
from web import HTTPError, ctx

from markdown2 import markdown

from gtfo import conf
from content import Content

def slug_from_path(path):
  (name, _) = splitext(path)
  return name[ len(conf.siteopts.root) :]

def _length_then_lex(f, s):
  """ Sorts strings on length. If two strings are the same length,
  then it sorts them based on lexicographic order. """
  if len(f) == len(s):
    return cmp(f, s)
  else:
    return len(f) - len(s)

def build_root_nav_list():
  """ Build the root nav list. This includes all files ending in .html or .gtf
  which are in the root web directory."""
  files = os.listdir(conf.siteopts.root)
  navlist = []

  if conf.navigation.add_home:
    navlist.append(('/', 'home'))
  if conf.navigation.add_blog:
    navlist.append(('/blog', 'blog'))

  for f in files:
    (slug, ext) = os.path.splitext(f)
    ext = ext.lower()
    if( not slug.startswith('.') and
        ext == '.html' or ext == '.gtf'
      ):
      navlist.append( ('/'+slug, slug) )
  if conf.navigation.remove_index:
    navlist = filter(lambda (x,y): x!='/index', navlist)
  return sorted(navlist, _length_then_lex, lambda (a, b): a)

def get_gtf_in_slug(slug):
  for root, dirs, files in os.walk(join(conf.siteopts.root, slug)):

    # Don't go into . directories
    filter(lambda d: not d.startswith('.'), dirs)
    
    for f in files:
      if f.lower().endswith('.gtf'):
        yield Content(slug_from_path(join(root, f)))

def get_sidebar_calendar():
  months = defaultdict(lambda: 0)
  for post in get_gtf_in_slug('blog'):
    post_month = post.date[:-3].replace('-', '/') # dates are in YYYY-MM-DD format
    months[post_month] = months[post_month] + 1
  return sorted(months.items(), key=lambda (k, v): k, reverse=True)

def last_n_blog_posts(n):
  return islice(get_gtf_in_slug('blog'), n)

def get_tags():
  tags = defaultdict(lambda: 0)
  for post in get_gtf_in_slug('blog'):
    if hasattr(post, 'tags') and post.tags:
      for tag in post.tags:
        tags[tag.strip()] = tags[tag.strip()] + 1
  return tags.items()
    
def get_posts_by_tag(tag):
  posts = []
  for post in get_gtf_in_slug('blog'):
    if hasattr(post, 'tags') and post.tags:
      if tag in [ t.strip() for t in post.tags ]:
        posts.append(post)
  return sorted(posts, cmp=lambda x,y: cmp(y,x), key=lambda p: p.date)

def recent_comments(db):
  comments = list(db.select('comments', limit=conf.sidebar.recent_comments, order="time DESC"))
  meta = []
  for comment in comments:
    try:
      meta.append(GTF(comment.slug).meta)
    except IOError:
      meta.append(Meta(comment.slug))
  return zip(comments, meta)

class PrettyRedirect(HTTPError):
  """A `304 See Other` redirect which ignores the ctx.homepath (mod_rewrite
  mucks with this, which yields ugly (but working) URLS.). GTFO uses this
  redirect to avoid this problem."""
  def __init__(self, url, status='303 See Other'):
    """
    Returns a `status` redirect to the new URL. 
    `url` is joined with the base URL so that things like 
    `redirect("about") will work properly.
    """
    newloc = urlparse.urljoin(web.ctx.path, url)

    newloc = ctx.homedomain + newloc

    headers = {
      'Content-Type': 'text/html',
      'Location': newloc
    }
    HTTPError.__init__(self, status, headers, "")
