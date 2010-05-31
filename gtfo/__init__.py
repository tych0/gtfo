from __future__ import with_statement
from config import get_config

conf = None

with open('../www/gtfo.conf', 'r+') as config_file:
  conf = get_config(config_file)
