# coding= utf-8

import re, os, time, codecs, sys, _strptime

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

    settings= None
    parentDB= False

    def __init__(self, _parentDB, _settings):
        self.settings= _settings
        self.parentDB= _parentDB


#public#


    def flush(self, _dbN):
        dirty= False
        for iT in self.parentDB.todoA:
            curTodo= self.parentDB.todoA[iT]
            if curTodo.savePending(_dbN):
                dirty= True

        if not dirty:
            return True


        if not self.dbOk:
            print("TypeTodo: 'file' db was not properly inited. Saving disabled.")
            return False


        try:
            with codecs.open(self.settings.file, 'w+', 'UTF-8') as f:
                f.write(self.settings.head)
                f.write("\n")

                for iT in sorted(self.parentDB.todoA):
                    curTodo= self.parentDB.todoA[iT]
                    if curTodo.initial:
                        continue

                    self.maxId= max(self.maxId, curTodo.id)

                    stateSign= curTodo.state
                    if stateSign=='': stateSign='-'

                    lvl= curTodo.lvl
                    if curTodo.lvl>=0: lvl= '+' +str(curTodo.lvl)

                    #runtime GMT time to local
                    gmtTime= time.localtime(curTodo.stamp)

                    f.write(stateSign +', '.join(curTodo.tagsA) +' ' +str(curTodo.id)+ ': ' +' '.join([str(lvl), '"'+curTodo.fileName+'"', curTodo.editor, time.strftime('%y/%m/%d %H:%M', gmtTime)]) +"\n\t" +curTodo.comment +"\n\n")


        except Exception as e:
            print("TypeTodo: 'file' db experienced error while flushing")
            print(e)

            return False


        for iT in self.parentDB.todoA:
            self.parentDB.todoA[iT].setSaved(SAVE_STATES.IDLE, _dbN)


        return True




#   newId() is suited to be called in a short sequence, to iplement lowcost retrying.
#   .lastId holds reserved Id and is cached out if matches _wantedId.
#   Id is initially rteserved if _wantedId=0, thich is case on every sequence start.
#
#   return actually reserved new Id
#
#   Same is true for other engines.

    def newId(self, _wantedId=0):
        self.fetch()
            
        if _wantedId==self.lastId:
            return self.lastId

        self.maxId+= 1
        if _wantedId>self.maxId:
            self.maxId= _wantedId
        
        self.lastId= self.maxId
        return self.lastId



    def releaseId(self, _id):
        None;




    def fetch(self, _id=False):
        if not os.path.isfile(self.settings.file):
            print("TypeTodo: 'file' db does not exist, should be created.")
            return False


        try:
            todoA= {}
            with codecs.open(self.settings.file, 'r', 'UTF-8') as f:
                ctxTodo= None
                for ln in f:
                    ln= ln.splitlines()[0]
                    matchParse= RE_TODO_STORED.match(ln)
                    if matchParse:
                        __id= int(matchParse.group('id'))

                        if _id and _id!=__id: #pick one
                            continue

                        #file holds local time, need to convert to GMT for runtime
                        rxETime= matchParse.group('edited')
                        gmtTime= time.mktime (time.strptime(rxETime, '%y/%m/%d %H:%M'))

                        if __id not in todoA:
                            todoA[__id]= TodoTask(__id, self.parentDB.config.projectName, self.parentDB)
                        ctxTodo= matchParse

                        self.maxId= max(self.maxId, __id)
                        continue

                    if ctxTodo:
                        __state= ctxTodo.group('prefix')
                        if ctxTodo.group(1)=='-': __state= ''
                        matchComment= RE_TODO_STORED_COMMENT.match(ln)
                        todoA[int(ctxTodo.group('id'))].set(__state, ctxTodo.group('tags').split(','), int(ctxTodo.group('priority')), ctxTodo.group('context'), matchComment.group('comment'), ctxTodo.group('editor'), gmtTime)
                        ctxTodo= None
                return todoA

        except Exception as e:
            print("TypeTodo: 'file' db experienced error while fetching")
            print(e)

            self.dbOk= False
            return False
