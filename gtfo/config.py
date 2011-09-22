from __future__ import with_statement

from os.path import exists, expanduser
from ConfigParser import ConfigParser

from tyconfig import TYConfig

def get_config(conf_file):
  """ Return the user's conf file (or create it if it doesn't exist) and make
  sure all the settings are present, or set them to their defaults. """
  ### set default opts 
  defaults = {
    ## siteopts
    "siteopts" : {
      # where is the root of the website on the filesystem?
      "root" : expanduser("~/www/"),

      # what should the separator be when interpreting gtf files?
      "gtf_separator" : "%%%%",

      # Site's title tag prefix, if any
      "title_prefix" : 'tycho.ws - ',
    },

    ## navigation (main menu)
    "navigation" : {
      # hide the 'index.{mkd,html}' file from the top menu?
      "remove_index" : True,

      # add a 'home' option to the top menu?
      "add_home" : True,
      
      # should we show a link to 'blog' on the top menu?
      "add_blog" : True,

      # where do we send the user by default?
      "default_slug" : "index",
    },
  
    ## default page information
    "page_defaults" : {
      # who is the default author?
      "author" : "tycho",

      # what is the default title?
      "title" : "",

      # should we allow comments by default?
      "comments" : True,

      # what are the default tags, if any?
      "tags" : "",
    },

    ## blog
    "blog" : {
      "posts_on_front_page" : 10,
    },

    ## sidebar
    "sidebar" : {
      "blog_posts_on_sidebar" : 5,
    },

    ## system
    "system" : {
      "db_location" : 'gtfo.db',
    },
  }

  # Read the user's file if it exists. 
  conf = TYConfig(defaults = defaults)
  conf.read([conf_file])

  if not exists(conf_file):
    with open(conf_file, 'w') as f:
      conf.write(f)
  return conf
