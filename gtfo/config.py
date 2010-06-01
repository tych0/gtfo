from __future__ import with_statement
from ConfigParser import ConfigParser
def get_config(conf_file):
  """ Return the user's conf file (or create it if it doesn't exist) and make
  sure all the settings are present, or set them to their defaults. """

  # Read the user's file if it exists. 
  conf = ConfigParser()
  conf.read([conf_file])

  ### set default opts 
  ## navigation
  if not conf.has_section('navigation'):
    conf.add_section('navigation')

  # hide the 'index.{mkd,html}' file from the left menu?
  if not conf.has_option('navigation', 'remove_index'):
    conf.set('navigation', 'remove_index', 'True')

  # add a 'home' option to the left menu?
  if not conf.has_option('navigation', 'add_home'):
    conf.set('navigation', 'add_home', 'True')
  
  if not conf.has_option('navigation', 'default_slug'):
    conf.set('navigation', 'default_slug', 'index')

  ## default page information
  if not conf.has_section('page_defaults'):
    conf.add_section('page_defaults')

  # who is the default author?
  if not conf.has_option('page_defaults', 'author'):
    conf.set('page_defaults', 'author', 'tycho')

  # what is the default title?
  if not conf.has_option('page_defaults', 'title'):
    conf.set('page_defaults', 'title', '')

  # should we allow comments by default?
  if not conf.has_option('page_defaults', 'comments'):
    conf.set('page_defaults', 'comments', True)

  ## misc
  if not conf.has_section('misc'):
    conf.add_section('misc')

  if not conf.has_option('misc', 'gtf_separator'):
    conf.set('misc', 'gtf_separator', '%%%%')

  with open(conf_file, 'w') as f:
    conf.write(f)
  return conf
