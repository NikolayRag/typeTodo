# coding= utf-8

'''
scratch of organizing smooth per-project id assigning for (un)registered users at HTTP

unregistered:
1. at .do creation it is assigned unique hash ID from SITE. So it being per-project.
2. any access to SITE using that ID is granted to anon

registered:
0. user can secure his ID's by applying his hash (username+pass) in config
1. same as unregistered.1
2. any access to SITE using that ID is specified by user


flow:

- each http request specifies projects/tasks repository by hash (public)
    OR by username (secured)
- each rep hold number of projects

public rep:
- rep is initialised by requesting name from server (at config)
- repository can be accessed anonymously, both reading and writing.
    *The ONLY protection from intrusion so far is hash complexity (xx-byte?)
- project accessed by specifying rep hash and project name within rep

secured rep:
- rep is initialised by creating on server/requesting while logged
- rep is accessed by owner only (by default)
- rep access can be expanded by owner

either:
- task editor name specified by rather an plain text (anon) or by logged user id

'''
#todo 96 (store) +0: add more 'context' using HTTP

import sys, json

if sys.version < '3':
    import urllib2, urllib
else:
    import urllib.request as urllib2
    import urllib.parse as urllib



class TodoDbHttp():
    todoA= None
    projectName= ''
    userName= ''

    httpAddr= ''
    httpRepository= ''
    httpUname= ''
    httpPass= ''


    def __init__(self, _todoA, _uname, _name, _httpAddr, _httpRepository, _httpUname, _httpPass):
        self.todoA= _todoA
        self.userName= _uname
        self.projectName= _name
        if self.projectName== '':
            self.projectName= '*'

        self.httpAddr= _httpAddr
        self.httpRepository= _httpRepository
        self.httpUname= _httpUname
        self.httpPass= _httpPass

    def flush(self):
        postData= {}
        postList= list()
        for iT in self.todoA:
            curTodo= self.todoA[iT]
            if curTodo.saved: continue

            postList.append(str(curTodo.id))
            postData['state' +str(curTodo.id)]= urllib2.quote(str(curTodo.state).encode('utf-8'))
            postData['file' +str(curTodo.id)]= urllib2.quote(curTodo.fileName.encode('utf-8'))
            postData['cat' +str(curTodo.id)]= urllib2.quote(curTodo.cat.encode('utf-8'))
            postData['lvl' +str(curTodo.id)]= curTodo.lvl
            postData['comm' +str(curTodo.id)]= urllib2.quote(curTodo.comment.encode('utf-8'))

        postData['ids']= ','.join(postList)
        postData['user']= urllib2.quote(self.userName.encode('utf-8'))
        postData['rep']= self.httpRepository
        postData['project']= urllib2.quote(self.projectName.encode('utf-8'))
        if self.httpUname!='' and self.httpPass!='':
            postData['logName']= urllib2.quote(self.httpUname)
            postData['logPass']= urllib2.quote(self.httpPass)

        req = urllib2.Request('http://' +self.httpAddr +'/?=flush', str.encode(urllib.urlencode(postData)))
        try:
            response = bytes.decode( urllib2.urlopen(req).read() )
            if response=='':
                print('TypeTodo: HTTP server flushing returns unexpected result. Repository: ' +self.httpRepository)
                return False

            allOk= True
            response= json.loads(response)
            for respId in response:
                if not self.todoA[int(respId)]:
                    print ('TypeTodo: Server responded task ' +respId +' that doesn\'t exists. Skipping')

                elif response[respId]==0:
                    self.todoA[int(respId)].setSaved()

                else:
                    print ('TypeTodo: Task ' +respId +' was not saved yet. Error returned: ' +response[respId])
                    allOk= False

            return allOk

        except:
            print('TypeTodo: HTTP server error while flushing. Repository: ' +self.httpRepository)
            return False

# reserve new db entry
# returned value:
#   int:    new id

    def newId(self):
        postData= {}
        postData['user']= urllib2.quote(self.userName.encode('utf-8'))
        postData['rep']= self.httpRepository
        postData['project']= urllib2.quote(self.projectName.encode('utf-8'))
        if self.httpUname!='' and self.httpPass!='':
            postData['logName']= urllib2.quote(self.httpUname)
            postData['logPass']= urllib2.quote(self.httpPass)
        req = urllib2.Request('http://' +self.httpAddr +'/?=newid', str.encode(urllib.urlencode(postData)))
        try:
            response= bytes.decode( urllib2.urlopen(req).read() )
            if str(int(response)) != response:
                response= False
                print('TypeTodo: HTTP server fails creating doplet. Repository: ' +self.httpRepository)

        except:
            response= False;
            print('TypeTodo: HTTP server error while creating doplet. Repository: ' +self.httpRepository)

        return response


#todo 105 (http) +0: make fetch()
    def fetch(self, _id=False):
        return False
