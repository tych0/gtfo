import web
from markdown2 import markdown
from os.path import splitext

urls = (
  "/(.*)", "GTFO",
)
       
render = web.template.render('templates/')
web.template.Template.globals['render'] = render

class GTFO:
  def GET(self, path=None):
    if not path: path='index'
    path = splitext(path)[0]

    try:
      return render.template('hi there', markdown(open('www/'+path+'.mkd').read()))
    except IOError:
      pass

    return open('www/'+path+'.html').read()

app = web.application(urls, globals())
