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

