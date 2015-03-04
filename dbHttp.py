# coding= utf-8

'''
unregistered setup:
1. at .do creation, unique hash ID from SITE is used. So it being per-project.
2. any access to SITE using that ID is granted to anon

registered setup:
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

import sys, json, threading, encodings.idna
from threading import Timer

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


class TodoDbHttp():
    name= 'Http'

    httpAddr= ''
    httpRepository= ''
    httpUname= ''
    httpPass= ''

    parentDB= False
    migrate= False

    reservedId= 0
    reserveEvent= None
    timerReserveId= None

    def __init__(self, _cfg, _parentDB):
        self.httpAddr= _cfg['addr']
        self.httpRepository= _cfg['base']
        self.httpUname= _cfg['login']
        self.httpPass= _cfg['passw']

        self.parentDB= _parentDB

        self.reservedId= 0
        self.reserveEvent= threading.Event()
        self.reserveEvent.set()
        self.timerReserveId = Timer(0, None) #dummy

        self.newId()

#todo 270 (http) +0: implement http timeout

    def flush(self, _dbN):
        postData= {}
        postList= list()
        postTodoA= {}

        if self.migrate:
            print('TypeTodo Http: migrating')

        for iT in self.parentDB.todoA:
            curTodo= self.parentDB.todoA[iT]
            if not self.migrate: 
                if curTodo.savedA[_dbN]!=SAVE_STATES.READY: continue
            curTodo.setSaved(SAVE_STATES.HOLD, _dbN) #poke out from saving elsewhere

            postList.append(str(curTodo.id))
            postTodoA['state' +str(curTodo.id)]= urllib2.quote(STATE_LIST[curTodo.state].encode('utf-8'))
            postTodoA['file' +str(curTodo.id)]= urllib2.quote(curTodo.fileName.encode('utf-8'))
            postTodoA['tags' +str(curTodo.id)]= urllib2.quote(','.join(curTodo.tagsA).encode('utf-8'))
            postTodoA['lvl' +str(curTodo.id)]= curTodo.lvl
            postTodoA['comm' +str(curTodo.id)]= urllib2.quote(curTodo.comment.encode('utf-8'))
            postTodoA['stamp' +str(curTodo.id)]= curTodo.stamp

        if not len(postList):
            return True

        postTodoA['ids']= ','.join(postList)
        postData['todoa']= json.dumps(postTodoA)
        postData['logName']= urllib2.quote(self.parentDB.projUser.encode('utf-8'))
        if self.httpUname!='' and self.httpPass!='':
            postData['logName']= urllib2.quote(self.httpUname)
            postData['logPass']= urllib2.quote(self.httpPass)

#=todo 242 (http, api) +5: point at project using URL
        postData['rep']= self.httpRepository
        postData['project']= urllib2.quote(self.parentDB.projectName.encode('utf-8'))

        req = urllib2.Request('http://' +self.httpAddr +'/?=flush', str.encode(urllib.urlencode(postData)))
        try:
            response = bytes.decode( urllib2.urlopen(req).read() )
        except Exception as e:
            print('TypeTodo: HTTP server error while flushing. Repository: ' +self.httpRepository)
            print(e)
            return False
        if response=='':
            print('TypeTodo: HTTP server flushing returns unexpected result. Repository: ' +self.httpRepository)
            return False

        allOk= True
#todo 281 (db, flush) +0: compare with postList
        response= json.loads(response)
        for respId in response:
            curTodo= self.parentDB.todoA[int(respId)]

            if not self.parentDB.todoA[int(respId)]:
                print ('TypeTodo: Server responded task ' +respId +' that doesn\'t exists. Skipping')
                continue

            elif response[respId]!=0:
                print ('TypeTodo: Task ' +respId +' was not saved yet. Error returned: ' +response[respId])
                curTodo.setSaved(SAVE_STATES.READY, _dbN)
                allOk= False
            else:
                if curTodo.savedA[_dbN]==SAVE_STATES.HOLD: #edited-while-save todo will not become idle here
                    curTodo.setSaved(SAVE_STATES.IDLE, _dbN)


        self.migrate= False
        return allOk

#macro
#   pre: pick event set
#   wait for pick event to set
#   set return cached
#   go pick next
    def newId(self):
        self.reserveEvent.wait()

        okId= self.reservedId

        self.reserveEvent.clear()
        self.timerReserveId= Timer(0, self.newIdGet).start()

        return okId


#todo 258 (http) +5: release prefetched id at exit
    def newIdRelease(self):
        None

    def newIdGet(self):
        postData= {}
        postData['logName']= urllib2.quote(self.parentDB.projUser.encode('utf-8'))
        if self.httpUname!='' and self.httpPass!='':
            postData['logName']= urllib2.quote(self.httpUname)
            postData['logPass']= urllib2.quote(self.httpPass)

        postData['rep']= self.httpRepository
        postData['project']= urllib2.quote(self.parentDB.projectName.encode('utf-8'))

        req = urllib2.Request('http://' +self.httpAddr +'/?=newid', str.encode(urllib.urlencode(postData)))
        try:
            response= bytes.decode( urllib2.urlopen(req).read() )
        except Exception as e:
            print('TypeTodo: HTTP server error creating todo')
            print(e)
            response= False;
        if str(int(response)) != response:
            print('TypeTodo: HTTP server fails creating todo')
            response= False

        self.reservedId= int(response)
        print('TypeTodo: HTTP id reserved: ' +str(self.reservedId))
        self.reserveEvent.set()


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
        except Exception as e:
            print('TypeTodo: cant fetch http')
            print(e)
            return False

        todoA= {}
        for task in json.loads(response):
            __id= int(task['id'])

#todo 143 (multidb) -1: http; handle cStamp on fetch
            if __id not in todoA:
#=todo 307 (http) +0: change URL addressing scheme to rep/proj; join registered/anon name
                todoA[__id]= TodoTask(__id, self.parentDB.projectName, task['nameuser'], int(task['ustamp']), self.parentDB)

                fetchedStateName= task['namestate']
#todo 257 (http) +0: remove True and False states after migration
#subject to remove after state names migration+
                if fetchedStateName=='False':
                    self.migrate= True
                    fetchedStateName= 'Open'
                if fetchedStateName=='True':
                    self.migrate= True
                    fetchedStateName= 'Close'
#subject to remove after state names migration-
                stateFound= False
                for stateIdx in STATE_LIST:
                    if STATE_LIST[stateIdx]==fetchedStateName:
                        stateFound= True
                        break
                if not stateFound: #defaults to 'opened' todo
                    stateIdx= ''

                tags= task['nametag'].split(',')
                todoA[__id].set(stateIdx, tags, task['priority'], task['namefile'], task['comment'], task['nameuser'], int(task['ustamp']))

        return todoA
