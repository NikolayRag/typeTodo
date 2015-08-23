import sys, urllib2, base64, json

if sys.version < '3':
    import urllib2, urllib
else:
    import urllib.request as urllib2
    import urllib.parse as urllib

if sys.version < '3':
    from task import *
    from c import *
else:
    from .task import *
    from .c import *


class TodoDbRedmine():
    name= 'Redmine'

    lastId= None

    settings= None
    parentDB= False


    def __init__(self, _parentDB, _settings):
        self.settings= _settings
        self.parentDB= _parentDB




	def flush(self, _dbN):
		None




    def releaseId(self):
    	None



    def newId(self, _wantedId=0):
        if _wantedId==self.lastId:
            return self.lastId




	def fetch(self):
		return False
        request= urllib2.Request("http://demo.redmine.org/projects/right start.json")
        request= urllib2.Request("http://demo.redmine.org/issues.json?project_id=84387")
        base64string= base64.encodestring('%s:%s' % (log, passw)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        result= urllib2.urlopen(request)

