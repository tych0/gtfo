import os

def _length_then_lex(f, s):
	if len(f) == len(s):
		return cmp(f, s)
	else:
		return len(f) - len(s)

def build_root_nav_list(path):
	files = os.listdir(path)
	navlist = [('/', 'home')]
	for f in files:
		(slug, ext) = os.path.splitext(f)
		ext = ext.lower()
		if( not os.path.isdir(path+'/'+f) and
			  not slug.startswith('.') and
				ext == '.html' or ext == '.mkd'
			):
			navlist.append( ('/'+slug, slug) )
	navlist = filter(lambda (x,y): x!='/index', navlist)
	return sorted(navlist, _length_then_lex, lambda (a, b): a)
