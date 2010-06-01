from __future__ import with_statement
from config import get_config
import os

CONFIG_FILE_PATH = 'www/gtfo.conf'
conf = None

with open(CONFIG_FILE_PATH, 'w+') as config_file:
  conf = get_config(config_file)
