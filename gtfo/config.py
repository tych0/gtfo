from ConfigParser import ConfigParser
def get_config(conf_file):
  """ Return the user's conf file (or create it if it doesn't exist) and make
  sure all the settings are present, or set them to their defaults. """

  # Read the user's file if it exists. 
  conf = ConfigParser()
  conf.read(conf_file)
  
  ### set default opts 
  ## meta section
  if not conf.has_section('meta'):
    conf.add_section('meta')

  # conf file version number
  if not conf.has_option('meta', 'version'):
    conf.set('meta', 'version', '1')

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

  conf.write(conf_file)
  return conf
