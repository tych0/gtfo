from __future__ import with_statement

import os
from datetime import date

from markdown2 import markdown

from gtfo import conf

def _length_then_lex(f, s):
  """ Sorts strings on length. If two strings are the same length,
  then it sorts them based on lexicographic order. """
  if len(f) == len(s):
    return cmp(f, s)
  else:
    return len(f) - len(s)

def build_root_nav_list(path):
  """ Build the root nav list. This includes all files ending in .html or .mkd
  which are in the root web directory."""
  files = os.listdir(path)
  navlist = []

  if conf.getboolean('navigation', 'add_home'):
    navlist.append(('/', 'home'))

  for f in files:
    (slug, ext) = os.path.splitext(f)
    ext = ext.lower()
    if( not slug.startswith('.') and
        ext == '.html' or ext == '.mkd'
      ):
      navlist.append( ('/'+slug, slug) )
  if conf.getboolean('navigation', 'remove_index'):
    navlist = filter(lambda (x,y): x!='/index', navlist)
  return sorted(navlist, _length_then_lex, lambda (a, b): a)

def _last_n_blog_posts(n):
  year = date.today().year
  posts = []
  while year > 1990: # nobody used the internet for 1990, right? ;-)
    month = 12
    while month > 0:
      try:
        month_str = '%02d' % month
        slug = 'blog/'+str(year)+'/'+month_str
        entries = os.listdir('www/'+slug)
        entries = filter(lambda e: not os.path.isdir(e) and
                                   not e.startswith('.') and
                                   e.lower().endswith('.gtf'),
                         entries)
        entries = map(lambda e: GTF(slug+'/'+os.path.splitext(e)[0]), entries)
        entries = sorted(entries, cmp, lambda g: g.meta.date)
        posts += entries
        if len(posts) >= n:
          posts = posts[n:]
          return posts
      except (IOError, OSError) as e:
        pass
      month = month - 1
    year = year - 1
  return posts

def get_front_page_posts(db):
  gtf_files = _last_n_blog_posts(conf.getint('blog', 'posts_on_front_page'))
  posts = []
  for post in gtf_files:
    d = {}
    d['title'] = post.meta.title
    d['author'] = post.meta.author
    d['date'] = post.meta.date
    d['content'] = post.raw_content_html()
    d['slug'] = post.meta.slug
    d['comment_count'] = db.select('comments', 
                                   vars={'slug':post.meta.slug},
                                   what='COUNT(*) as count',
                                   where='slug=$slug',
                                  )[0].count
    posts.append(d)
  return posts

def get_sidebar_posts():
  return _last_n_blog_posts(conf.getint('sidebar', 'blog_posts_on_sidebar'))

def get_comments_for_slug(slug, db):
  return list(db.select('comments', {'slug' : slug}, where="slug = $slug", order="time DESC"))
  
def recent_comments(db):
  comments = list(db.select('comments', limit=10, order="time DESC"))
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
    # if we couldn't find the attribute, get the default (or fail)
    if conf.has_option('page_defaults', name):
      return conf.get('page_defaults', name)
    else:
      raise AttributeError(name)

class GTF(object):
  """ constructor for automatically parsing a .gtf file """
  def __init__(self, slug):
    """ This splits a .gtf file into it's metadata and markdown pieces,
    for use in their respective parsers. """
    meta = []
    markd = []
    in_meta = True
  
    with open('www/'+slug+'.gtf') as f:
      for line in f:
        if conf.get('misc', 'gtf_separator') in line:
          in_meta = False
        elif in_meta:
          meta.append(line)
        else:
          markd.append(line)
    self.meta = Meta(slug, meta)
    self.markdown = ''.join(markd)
  
  def raw_content_html(self):
    return markdown(self.markdown)
