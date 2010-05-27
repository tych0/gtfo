import web
import sys

urls = ("/(.*)", "GTFO")

class GTFO:
  def GET(self, path=None):
    return 'Hello world! ' + sys.version

app = web.application(urls, globals())
