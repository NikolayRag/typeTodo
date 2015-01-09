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

if sys.version < '3':
    from task import *
else:
    from .task import *


class TodoDbHttp():
    name= 'Http'

    httpAddr= ''
    httpRepository= ''
    httpUname= ''
    httpPass= ''

    parentDB= False


    def __init__(self, _cfg, _parentDB):
        self.httpAddr= _cfg['addr']
        self.httpRepository= _cfg['base']
        self.httpUname= _cfg['login']
        self.httpPass= _cfg['passw']

        self.parentDB= _parentDB


    def flush(self, _dbN):
        postData= {}
        postList= list()
        postTodoA= {}

        for iT in self.parentDB.todoA:
            curTodo= self.parentDB.todoA[iT]
            if curTodo.savedA[_dbN]: continue

            postList.append(str(curTodo.id))
            postTodoA['state' +str(curTodo.id)]= urllib2.quote(str(curTodo.state).encode('utf-8'))
            postTodoA['file' +str(curTodo.id)]= urllib2.quote(curTodo.fileName.encode('utf-8'))
            postTodoA['cat' +str(curTodo.id)]= urllib2.quote(curTodo.cat.encode('utf-8'))
            postTodoA['lvl' +str(curTodo.id)]= curTodo.lvl
            postTodoA['comm' +str(curTodo.id)]= urllib2.quote(curTodo.comment.encode('utf-8'))
            postTodoA['stamp' +str(curTodo.id)]= curTodo.stamp

        if not len(postList):
            return True

        postTodoA['ids']= ','.join(postList)
        postData['user']= urllib2.quote(self.parentDB.projUser.encode('utf-8'))
        postData['rep']= self.httpRepository
        postData['project']= urllib2.quote(self.parentDB.projectName.encode('utf-8'))
        postData['todoa']= json.dumps(postTodoA)
        if self.httpUname!='' and self.httpPass!='':
            postData['logName']= urllib2.quote(self.httpUname)
            postData['logPass']= urllib2.quote(self.httpPass)

        req = urllib2.Request('http://' +self.httpAddr +'/?=flush', str.encode(urllib.urlencode(postData)))
        try:
            response = bytes.decode( urllib2.urlopen(req).read() )
        except:
            print('TypeTodo: HTTP server error while flushing. Repository: ' +self.httpRepository)
            return False
        if response=='':
            print('TypeTodo: HTTP server flushing returns unexpected result. Repository: ' +self.httpRepository)
            return False

        allOk= True
        response= json.loads(response)
        for respId in response:
            if not self.parentDB.todoA[int(respId)]:
                print ('TypeTodo: Server responded task ' +respId +' that doesn\'t exists. Skipping')

            elif response[respId]!=0:
                print ('TypeTodo: Task ' +respId +' was not saved yet. Error returned: ' +response[respId])
                allOk= False

            else:
                self.parentDB.todoA[int(respId)].setSaved(True, _dbN)
            
        return allOk

# reserve new db entry
# returned value:
#   int:    new id

    def newId(self):
        postData= {}
        postData['user']= urllib2.quote(self.parentDB.projUser.encode('utf-8'))
        postData['rep']= self.httpRepository
        postData['project']= urllib2.quote(self.parentDB.projectName.encode('utf-8'))
        if self.httpUname!='' and self.httpPass!='':
            postData['logName']= urllib2.quote(self.httpUname)
            postData['logPass']= urllib2.quote(self.httpPass)
        req = urllib2.Request('http://' +self.httpAddr +'/?=newid', str.encode(urllib.urlencode(postData)))
        try:
            response= bytes.decode( urllib2.urlopen(req).read() )
        except:
            response= False;
            print('TypeTodo: HTTP server error while creating doplet. Repository: ' +self.httpRepository)
        if str(int(response)) != response:
            response= False
            print('TypeTodo: HTTP server fails creating doplet. Repository: ' +self.httpRepository)

        return int(response)


    def fetch(self, _id=False):
        postData= {}
        postData['rep']= self.httpRepository
        postData['project']= urllib2.quote(self.parentDB.projectName.encode('utf-8'))
        if self.httpUname!='' and self.httpPass!='':
            postData['logName']= urllib2.quote(self.httpUname)
            postData['logPass']= urllib2.quote(self.httpPass)
        req = urllib2.Request('http://' +self.httpAddr +'/?=fetchtasks', str.encode(urllib.urlencode(postData)))
        try:
            response= bytes.decode( urllib2.urlopen(req).read() )
        except:
            print('Cant fetch http')
            return False

        todoA= {}
        for task in json.loads(response):
            __id= int(task['id'])

#todo 143 (multidb) -1: http; handle cStamp on fetch
            if __id not in todoA:
                todoA[__id]= TodoTask(__id, task['nameproject'], task['nameuser'], int(task['ustamp']), self.parentDB)

                __state= True
                if task['namestate']=='False':
                    __state= False
                todoA[__id].set(__state, task['nametag'], task['priority'], task['namefile'], task['comment'], task['nameuser'], int(task['ustamp']))

        return todoA
