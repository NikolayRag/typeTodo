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


import sys, json, encodings.idna

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

    lastId= None

    settings= None
    parentDB= False


    def __init__(self, _parentDB, _settings):
        self.settings= _settings
        self.parentDB= _parentDB

#todo 270 (http, cleanup) +0: implement http timeout

#todo 307 (http, cleanup, unsure) +0: change URL addressing scheme to rep/proj; join registered/anon name
    def flush(self, _dbN):
        postData= {}
        postList= list()
        postTodoA= {}

        for iT in self.parentDB.todoA:
            curTodo= self.parentDB.todoA[iT]
            if not curTodo.savePending(_dbN):
                continue

            curTodo.setSaved(SAVE_STATES.HOLD, _dbN) #poke out from saving elsewhere

            postList.append(str(curTodo.id))
            postTodoA['state' +str(curTodo.id)]= STATE_LIST[curTodo.state]
            postTodoA['file' +str(curTodo.id)]= curTodo.fileName
            postTodoA['tags' +str(curTodo.id)]= ','.join(curTodo.tagsA)
            postTodoA['lvl' +str(curTodo.id)]= curTodo.lvl
            postTodoA['comm' +str(curTodo.id)]= curTodo.comment
            postTodoA['stamp' +str(curTodo.id)]= curTodo.stamp
        if not len(postList):
            return True

        postTodoA['ids']= ','.join(postList)
        postData['v']= 1
        postData['todoa']= json.dumps(postTodoA)
        postData['logName']= urllib2.quote(self.parentDB.config.projectUser)
        if self.settings.login!='' and self.settings.passw!='':
            postData['logName']= urllib2.quote(self.settings.login)
            postData['logPass']= urllib2.quote(self.settings.passw)

        postData['rep']= self.settings.base
        postData['project']= urllib2.quote(self.parentDB.config.projectName)

        req = urllib2.Request('http://' +self.settings.addr +'/?=flush', str.encode(urllib.urlencode(postData)))
        try:
            response = bytes.decode( urllib2.urlopen(req).read() )
        except Exception as e:
            print('TypeTodo: HTTP server error while flushing. Repository: ' +self.settings.base)
            print(e)
            return False
        if response=='':
            print('TypeTodo: HTTP server flushing returns unexpected result. Repository: ' +self.settings.base)
            return False

        allOk= True
#todo 281 (db, flush, cleanup) +0: compare with postList
        response= json.loads(response)
        for respId in response:
            curTodo= self.parentDB.todoA[int(respId)]

            if not self.parentDB.todoA[int(respId)]:
                print ('TypeTodo: Server responded task ' +respId +' that doesn\'t exists. Skipping')
                continue

            elif response[respId]!=0:
                print ('TypeTodo: Task ' +respId +' was not saved yet. Error returned: ' +response[respId])
                allOk= False
            else:
                if curTodo.saveProgress(_dbN): #edited-while-save todo will not become idle here
                    curTodo.setSaved(SAVE_STATES.IDLE, _dbN)


        return allOk




    def newId(self, _wantedId=0):
        if _wantedId==self.lastId:
            return self.lastId

        postData= {}
        postData['wantedId']= _wantedId
        postData['logName']= urllib2.quote(self.parentDB.config.projectUser)
        if self.settings.login!='' and self.settings.passw!='':
            postData['logName']= urllib2.quote(self.settings.login)
            postData['logPass']= urllib2.quote(self.settings.passw)

        postData['rep']= self.settings.base
        postData['project']= urllib2.quote(self.parentDB.config.projectName)

        req = urllib2.Request('http://' +self.settings.addr +'/?=new_task_id', str.encode(urllib.urlencode(postData)))
        try:
            response= bytes.decode( urllib2.urlopen(req).read() )
        except Exception as e:
            print('TypeTodo: HTTP server error creating todo')
            print(e)
            response= False;
        if str(int(response)) != response:
            print('TypeTodo: HTTP server fails creating todo')
            response= False

        self.lastId= int(response)
        return self.lastId




    def releaseId(self):
        postData= {}
        postData['wantedId']= self.lastId
        postData['logName']= urllib2.quote(self.parentDB.config.projectUser)
        if self.settings.login!='' and self.settings.passw!='':
            postData['logName']= urllib2.quote(self.settings.login)
            postData['logPass']= urllib2.quote(self.settings.passw)

        postData['rep']= self.settings.base
        postData['project']= urllib2.quote(self.parentDB.config.projectName)

        req = urllib2.Request('http://' +self.settings.addr +'/?=release_task_id', str.encode(urllib.urlencode(postData)))
        try:
            response= bytes.decode( urllib2.urlopen(req).read() )
            self.lastId= None
        except Exception as e:
            print('TypeTodo: HTTP server error creating todo')
            print(e)
            response= False;
        if str(int(response)) != response:
            print('TypeTodo: HTTP server fails creating todo')
            response= False

        return response




    def fetch(self):
        postData= {}
        postData['rep']= self.settings.base
        postData['project']= urllib2.quote(self.parentDB.config.projectName)
        if self.settings.login!='' and self.settings.passw!='':
            postData['logName']= urllib2.quote(self.settings.login)
            postData['logPass']= urllib2.quote(self.settings.passw)
        req = urllib2.Request('http://' +self.settings.addr +'/?=fetch_tasks', str.encode(urllib.urlencode(postData)))
        try:
            response= bytes.decode( urllib2.urlopen(req).read() )
        except Exception as e:
            print('TypeTodo: cant fetch http')
            print(e)
            return False

        todoA= {}
        for task in json.loads(response):
            __id= int(task['id'])

            if __id not in todoA:
                todoA[__id]= TodoTask(__id, self.parentDB.config.projectName, self.parentDB)

                fetchedStateName= task['namestate']

                stateIdx= ''
                for cState in STATE_LIST:
                    if STATE_LIST[cState]==fetchedStateName:
                        stateIdx= cState
                        break

                tags= task['nametag'].split(',')
                todoA[__id].set(stateIdx, tags, task['priority'], task['namefile'], task['comment'], task['nameuser'], int(task['ustamp']))

        return todoA
