from os.path import join

import web

from markdown2 import markdown

from gtfo import conf

class Content(object):
  """ This object represents a single piece of "content" represented by a slug.
  This can be either a raw html document or a gtf file, and may or may not have
  comments and other things associated with it. """
  def __init__(self, slug):

    db = web.database(dbn='sqlite', db=conf.system.db_location)
    metadata = []
    markd = []

    self.slug = slug

    try:
      path = join(conf.siteopts.root, slug+'.gtf')
      with open(path) as f:
        in_meta = True
        for line in f:
          if conf.siteopts.gtf_separator in line:
            in_meta = False
          elif in_meta:
            metadata.append(line)
          else:
            markd.append(line)

      for line in metadata:
        try:
          # make the information an attribute of this
          # object
          key = line.split('=')[0].strip()
          value = line.split('=')[1].strip()
          setattr(self, key, value)
        except IndexError:
          # someone screwed up their metadata... oh well,
          # do the best we can
          pass
      print metadata, markd
      self.html = markdown(''.join(markd))
      # TODO: Do we really need to do this for everything? We could get the
      # comments on demand if this turns out to slow things down.
      self.comments = list(db.select('comments', 
                                     {'slug' : slug}, 
                                     where="slug = $slug", 
                                     order="time DESC"))
    except IOError:

      try: # if not .gtf, try .html
        path = join(conf.siteopts.root, slug+'.html')
        with open(path) as f:
          self.html = f.read()
      except IOError:
        raise IOError("No such slug :-(")

    # set up default attributes if necessary
    if not hasattr(self, "author"):
      self.author = conf.page_defaults.author
    if not hasattr(self, "title"):
      self.title = conf.page_defaults.title
    if not hasattr(self, "date"):
      self.date = None
    if not hasattr(self, "comments"):
      kelf.comments = None
    if not hasattr(self, "tags"):
      self.tags = conf.page_defaults.tags.split(',')
    else:
      self.tags = self.tags.split(',')
    
