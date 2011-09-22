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

def get_posts_as_dicts(gtf_files, db):
  posts = []
  for post in gtf_files:
    d = {}
    d['title'] = post.title
    d['author'] = post.author
    d['date'] = post.date
    d['content'] = post.html
    d['slug'] = post.slug
    d['tags'] = post.tags
    d['comment_count'] = db.select('comments', 
                                   vars={'slug':post.slug},
                                   what='COUNT(*) as count',
                                   where='slug=$slug',
                                  )[0].count
    posts.append(d)
  return posts

def get_gtf_in_slug(slug):
  for root, dirs, files in os.walk(join(conf.siteopts.root, slug)):

    # Don't go into . directories
    filter(lambda d: not d.startswith('.'), dirs)
    
    for f in files:
      if f.lower().endswith('.gtf'):
        yield Content(slug_from_path(join(root, f)))

def _get_blog_posts():
  return get_gtf_in_slug('blog')

def get_sidebar_calendar():
  months = defaultdict(lambda: 0)
  for post in _get_blog_posts():
    post_month = post.date[:-3].replace('-', '/') # dates are in YYYY-MM-DD format
    months[post_month] = months[post_month] + 1
  return sorted(months.items(), key=lambda (k, v): k, reverse=True)

def _last_n_blog_posts(n):
  return islice(_get_blog_posts(), n)

def get_front_page_posts(db):
  gtf_files = _last_n_blog_posts(conf.blog.posts_on_front_page)
  return gtf_files

def get_tags():
  tags = defaultdict(lambda: 0)
  for post in _get_blog_posts():
    if hasattr(post, 'tags') and post.tags:
      for tag in post.tags:
        tags[tag.strip()] = tags[tag.strip()] + 1
  return tags.items()
    
def get_posts_by_tag(tag):
  posts = []
  for post in _get_blog_posts():
    if hasattr(post, 'tags') and post.tags:
      if tag in [ t.strip() for t in post.tags ]:
        posts.append(post)
  return sorted(posts, cmp=lambda x,y: cmp(y,x), key=lambda p: p.date)

def get_sidebar_posts():
  return _last_n_blog_posts(conf.sidebar.blog_posts_on_sidebar)

def get_comments_for_slug(slug, db):
  return list(db.select('comments', {'slug' : slug}, where="slug = $slug", order="time DESC"))
  
def recent_comments(db):
  comments = list(db.select('comments', limit=conf.sidebar.recent_comments, order="time DESC"))
  meta = []
  for comment in comments:
    try:
      meta.append(GTF(comment.slug).meta)
    except IOError:
      meta.append(Meta(comment.slug))
  return zip(comments, meta)

class Meta(object):
  def __init__(self, slug, metadata=[]):
    self.slug = slug
    self.date = None

    try:
      for line in metadata:
        # make the information an attribute of this object
        key = line.split('=')[0].strip()
        value = line.split('=')[1].strip()
        self.__dict__[key] = value
    except (IOError, IndexError):
      pass

  def __getattr__(self, name):
    # if we couldn't find the attribute, get the default
    return getattr(conf.page_defaults, name)

class GTF(object):
  """ constructor for automatically parsing a .gtf file """
  def __init__(self, slug=None, path=None):
    """ This splits a .gtf file into it's metadata and markdown pieces,
    for use in their respective parsers. """
    meta = []
    markd = []
    in_meta = True

    if slug:
      assert not path, "Exactly one of slug or path should be true"
      localpath = join(conf.siteopts.root, slug + '.gtf')
    else:
      assert path, "Exactly one of slug or path should be true"
      localpath = path
  
    with open(localpath) as f:
      for line in f:
        if conf.siteopts.gtf_separator in line:
          in_meta = False
        elif in_meta:
          meta.append(line)
        else:
          markd.append(line)
    self.meta = Meta(slug, meta)
    self.markdown = ''.join(markd)
  
  def raw_content_html(self):
    return markdown(self.markdown)

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
