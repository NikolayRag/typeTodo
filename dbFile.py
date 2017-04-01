# coding= utf-8

import re, os, time, codecs, sys, json, _strptime

if sys.version < '3':
    from task import *
    from c import *
else:
    from .task import *
    from .c import *

class TodoDbFile():
    name= 'File'

    dbOk= True

    lastId= None
    maxId= 0
    maxIdSaved= 0

    settings= None
    parentDB= False
    dbId= None

    def __init__(self, _parentDB, _settings, _dbId):
        self.settings= _settings
        self.parentDB= _parentDB
        self.dbId= _dbId


#public#

    def flush(self):
        if not self.parentDB.todoAInited:
            return True
            
        if not self.dbOk:
            print("TypeTodo: 'file' db was not properly inited. Saving disabled.")
            return False

        dirty= False
        for iT in self.parentDB.todoA:
            curTodo= self.parentDB.todoA[iT]
            if curTodo.savePending(self.dbId):
                dirty= True

        if dirty or self.maxIdSaved!=self.maxId:
            try:
                with codecs.open(self.settings.fullName, 'w+', 'UTF-8') as f:
                    for iT in sorted(self.parentDB.todoA):
                        curTodo= self.parentDB.todoA[iT]
                        if curTodo.initial:
                            continue

                        lvl= curTodo.lvl
                        if curTodo.lvl>=0: lvl= '+' +str(curTodo.lvl)

                        #runtime GMT time to local
                        gmtTime= time.localtime(curTodo.stamp)

                        f.write(curTodo.state +', '.join(curTodo.tagsA) +' ' +str(curTodo.id)+ ': ' +' '.join([str(lvl), '"'+curTodo.fileName+'"', curTodo.editor, time.strftime('%y/%m/%d %H:%M:%S', gmtTime)]) +"\n\t" +curTodo.comment +"\n\n")

            except Exception as e:
                print("TypeTodo: 'file' db experienced error while flushing")
                print(e)

                return False


        for iT in self.parentDB.todoA:
            self.parentDB.todoA[iT].setSaved(SAVE_STATES.IDLE, self.dbId)

        self.maxIdSaved= self.maxId

        return True




#   newId() is suited to be called in a short sequence, to iplement lowcost retrying.
#   .lastId holds reserved Id and is cached out if matches _wantedId.
#   Id is initially reserved if _wantedId=0, thich is case on every sequence start.
#
#   return actually reserved new Id
#
#   Same is true for other engines.

    def newId(self, _wantedId=0):
        if _wantedId==self.lastId:
            return self.lastId

        self.fetch()
        self.maxId= max(self.maxId, self.loadId())

        self.maxId+= 1
        if _wantedId>self.maxId:
            self.maxId= _wantedId
        
        self.flush()


        self.saveId(self.maxId)


        self.lastId= self.maxId

        return self.lastId

        

#   decrease stored maxid if it is same as current

    def releaseId(self, _atExit=False):
        self.fetch()
        self.maxId= max(self.maxId, self.loadId())
        
        if self.lastId==self.maxId:
            if _atExit:
                self.maxId-= 1
                self.flush()

                self.saveId(self.maxId)


        else:
            self.maxId= 0

        self.lastId= None

        return True



    def saveId(self, _id):
        stateFn= os.path.join(self.settings.fullRoot,'.do.state')

        stateJson= {}
        try:
            with codecs.open(stateFn, 'r', 'UTF-8') as f:
                stateJson= json.loads( f.read() )
        except:
            None

        stateJson[self.settings.fullFile]= int(_id)

        with codecs.open(stateFn, 'w+', 'UTF-8') as f:
            f.write( json.dumps(stateJson, indent=4) )



    def loadId(self):
        stateFn= os.path.join(self.settings.fullRoot,'.do.state')


        stateJson= {}

        try:
            with codecs.open(stateFn, 'r', 'UTF-8') as f:
                stateJson= json.loads( f.read() )

        except:
            return 0


        return stateJson[self.settings.fullFile] if (self.settings.fullFile in stateJson) else 0




#   fetch all tasks from file
#   also set .maxId from tasks and from '.maxid' file

    def fetch(self, _id=False):
        if not os.path.isfile(self.settings.fullName):
            print("TypeTodo: 'file' db does not exist, should be created.")

            codecs.open(self.settings.fullName, 'w+', 'UTF-8')

            return False


        todoA= {}
        try:
            with codecs.open(self.settings.fullName, 'r', 'UTF-8') as f:
                ctxTodo= None
                for ln in f:
                    ln= ln.splitlines()[0]
                    matchParse= RE_TODO_STORED.match(ln)
                    if matchParse:
                        cId= int(matchParse.group('id'))

                        if _id and _id!=cId: #pick one
                            continue

                        #file holds local time, need to convert to GMT for runtime
                        rxEDate= matchParse.group('editdate')
                        rxETime= matchParse.group('edittime')
                        rxESecs= matchParse.group('editsecs') or ':00'
                        gmtTime= time.mktime (time.strptime('%s %s%s' % (rxEDate, rxETime, rxESecs), '%y/%m/%d %H:%M:%S'))

                        if cId not in todoA:
                            todoA[cId]= TodoTask(cId, self.parentDB.config.projectName, self.parentDB)
                        ctxTodo= matchParse

                        if cId > self.maxId: 
                            self.maxIdSaved= self.maxId= cId
                        continue

                    if ctxTodo:
                        matchComment= RE_TODO_STORED_COMMENT.match(ln)
                        todoA[int(ctxTodo.group('id'))].set(ctxTodo.group('prefix'), ctxTodo.group('tags').split(','), int(ctxTodo.group('priority')), ctxTodo.group('context'), matchComment.group('comment'), ctxTodo.group('editor'), gmtTime)
                        ctxTodo= None
                        continue


                    maxIdParse= RE_TODO_FILE_MAXID.match(ln)
                    if maxIdParse:
                        cId= int(maxIdParse.group('maxid'))
                        if cId > self.maxId:
                            self.maxIdSaved= self.maxId= cId
                        continue


        except Exception as e:
            print("TypeTodo: 'file' db experienced error while fetching")
            print(e)

            self.dbOk= False
            return False


        return todoA
