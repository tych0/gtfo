from __future__ import with_statement
import os
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

class Meta(object):
  def __init__(self, slug, metadata=[]):
    self.slug = slug
    print metadata
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
  def __init__(self, fname):
    """ This splits a .gtf file into it's metadata and markdown pieces,
    for use in their respective parsers. """
    meta = []
    markd = []
    in_meta = True
    slug = os.path.splitext(fname)[0][len('www/'):]
  
    with open(fname) as f:
      for line in f:
        if conf.get('misc', 'gtf_separator') in line:
          in_meta = False
        elif in_meta:
          meta.append(line)
        else:
          markd.append(line)
    self.meta = Meta(slug, meta)
    self.markdown = ''.join(markd)
