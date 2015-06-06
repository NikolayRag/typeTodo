# coding= utf-8

import sys, re, os, time, codecs, threading
from threading import Timer

if sys.version < '3':
    from cfg import *
    from dbFile import *
    from dbSql import *
    from dbHttp import *
    from task import *
else:
    from .cfg import *
    from .dbFile import *
    from .dbSql import *
    from .dbHttp import *
    from .task import *

#todo 44 (config, db, feature, unsolved) +0: handle saving project - existing and blank; transfer db for involved files

#todo 89 (db, feature) +0: save context (+-2 strings of code) with task. NOT for 'file' mode


'''
   per-project task set
   Read config and set up db engine
'''

'''
    Read and hold all latest versions of tasks at reset()
     from all specified engines.
    Then store them back if inconsistence found,
     thus making them synchronised.
'''
class TodoDb():
    config= None

    maxflushRetries= 3
    flushTimeout= 30 #seconds
    timerFlush= None
    timerReset= None
    resetPending= 0
    resetId= 0

    reservedId= 0
    reserveEvent= None

    dbA= None
    todoA= None

    callbackFetch= None

    reportFetchReset= False
    reportFlush= False

    def __init__(self, _callback, _cfg):
        self.dbA= {}
        self.todoA= {}
        self.timerFlush = Timer(0, None) #dummy
        self.timerReset = Timer(0, None) #dummy

        self.callbackFetch= _callback
        self.config= _cfg

        self.reservedId= 0
        self.reserveEvent= threading.Event()
        self.reserveEvent.set()

        self.pushReset()
        



#=todo 1662 (fix, db) +0: unsaved doplet is overriden probably at changing config

    def pushReset(self, _delay=1000): #leave 1 to remove spam
        rId= self.resetId+1
        self.resetPending= rId
        sublime.set_timeout(lambda: self.reset(rId), _delay)
        self.resetId= rId

#Macro:
#    - get new cfg
#       - flush if unchanged
#    - fetch using new
#    - flush using new

    def resetDo(self):
        self.fetch()
        self.flush(True)

    def reset(self, _checkId):
        if _checkId!=self.resetPending:
            return
        self.resetPending= 0


        self.timerReset.cancel()
        if not self.config.update() and len(self.dbA):
            self.timerReset= Timer(0, self.resetDo)
            self.timerReset.start()
            return


        print ('TypeTodo: reset db')

        dbId= -1
        self.dbA.clear() #new db array

        for cSetting in self.config.settings:
            dbId+= 1
            if cSetting.engine=='file':
                cEngClass= TodoDbFile
            elif cSetting.engine=='mysql':
                cEngClass= TodoDbSql
            elif cSetting.engine=='http':
                cEngClass= TodoDbHttp
            else:
                continue

            self.dbA[dbId]= cEngClass(self, cSetting)


        self.newId() #run prefetch

        for iT in self.todoA: #set all unsaved
            self.todoA[iT].setSaved(SAVE_STATES.READY)

        self.reportFetchReset= True
        self.timerReset= Timer(0, self.resetDo)
        self.timerReset.start()








#macro
#   pre: pick event set
#   wait for pick event to set
#   set return cached
#   go pick next
    def newId(self):
        self.reserveEvent.wait()

        okId= self.reservedId #first call is initial, result should not be used

        self.reserveEvent.clear() #second call to newId() will suspend till newIdGet() done
        Timer(0, self.newIdGet).start()

        return okId





    def newIdGet(self):
        cId= 0

        tries= 10
        while True:
            ids= []
            for db in self.dbA:
                ids.append(self.dbA[db].newId(cId) or 0)

            cId= max(ids)
            if cId==min(ids):
                break

            if tries<=0:
                print('TypeTodo warning: Cannot synchronize new Id within db\'s.')
                break
        
            tries-= 1

        self.reservedId= cId
        print('TypeTodo: Id reserved: ' +str(self.reservedId))
        self.reserveEvent.set()









    def store(self, _id, _state, _tags, _lvl, _fileName, _comment):
        self.timerFlush.cancel()

        if _fileName and self.config.projectRoot:
            if (os.path.splitdrive(_fileName)[0]==os.path.splitdrive(self.config.projectRoot)[0]):
                _fileName= os.path.relpath(_fileName, self.config.projectRoot)
                
        _fileName= _fileName or ''

        _id= int(_id)

        cId= _id or 0
        if not _id:
#todo 1499 (check, db) -5: check newId() fail
            cId= self.newId()

            if not cId:
                sublime.status_message('Todo creation failed, see console for info')
                return False


        if cId not in self.todoA: #for new and repairing tasks
            self.todoA[cId]= TodoTask(cId, self.config.projectName, self)

        if _id:
            if self.todoA[cId].initial and _comment=='' and (_state=='+' or _state=='!'):
                del self.todoA[cId]
            else:
                self.reportFlush= True
                strStamp= int(time.time())
                self.todoA[cId].set(_state, _tags, _lvl, _fileName, _comment, self.config.projectUser, strStamp)

        self.flushRetries= self.maxflushRetries
        self.timerFlush= Timer(self.flushTimeout, self.flush)
        self.timerFlush.start()

        return cId









    def flush(self, _runOnce=False):
        self.timerFlush.cancel()


        flushOk= True
        for dbN in self.dbA:
            flushOk= flushOk and self.dbA[dbN].flush(dbN)
        
        if flushOk:
            if self.reportFlush:
                sublime.set_timeout(lambda: sublime.status_message('TypeTodo saved'), 0)

            self.reportFlush= False

            self.pushReset(30000)

            return


        if not _runOnce:
            self.flushRetries-= 1
            if self.flushRetries>0:
                sublime.set_timeout(lambda: sublime.status_message('TypeTodo error: cannot flush todo\'s.  Will retry ' +str(self.flushRetries) +' more times in ' +str(self.flushTimeout) +' sec\'s'), 0)
                self.timerFlush = Timer(self.flushTimeout, self.flush)
                self.timerFlush.start()

        if _runOnce or self.flushRetries==0:
            sublime.set_timeout(lambda: sublime.error_message('TypeTodo error:\n\n\tcannot flush todo\'s'), 0)








#macro
#   1. roll over all db's
#   2. fetch unbinded task lists
#   3. compare if new or updated or outdated
#       3.1. join into working list
#       3.2. reset other db's 'saved' flag

    def fetch(self):
        success= False

        for dbN in self.dbA:
            cDb= self.dbA[dbN]
            todoA= cDb.fetch()
            if todoA==False:
                continue

            success= True

            maybeNew= 0
            maybeOld= 0
            for iT in todoA: #each fetched task have to be compared to existing
                task= todoA[iT]
                __id= task.id

                isNew= __id not in self.todoA
                diffStamp= 0
                if not isNew:
                    diffStamp= task.stamp -self.todoA[__id].stamp
#todo 279 (check) +0: see if states dont interfere while task is in-save

                if isNew or diffStamp>0:
                    if not self.reportFetchReset or diffStamp>60: #some tasks can be skipped (in report only!) due to unsaved seconds in 'file' db
                        print ('TypeTodo: \'' +cDb.name +'\' DB is new at ' +str(__id))
                    elif diffStamp>0:
                        maybeNew+= 1
                    self.todoA[__id]= task
                    self.todoA[__id].setSaved(SAVE_STATES.READY) #all but current db are saved for task
                    self.todoA[__id].setSaved(SAVE_STATES.IDLE, dbN)

                elif diffStamp<0:
                    if self.reportFetchReset:
                        if diffStamp<-60: #some tasks can be skipped (in report only!) due to unsaved seconds in 'file' db
                            print ('TypeTodo: \'' +cDb.name +'\' DB is old at ' +str(__id))
                        else:
                            maybeOld+= 1
                    self.todoA[__id].setSaved(SAVE_STATES.READY, dbN)


            #'apparently new' mean that stamp difference is less than 60s. It is likely a subject, when comparing with 'file' DB with seconds truncated. In this case 'file' is treated as little older and is replaced. As 'file' is anyway replaced at each flush, it doesn't make any difference to normal behavior and is messaged just in case.
            if self.reportFetchReset:
                if maybeNew>0:
                    print ('TypeTodo: \'' +cDb.name +'\' DB have ' +str(maybeNew) +' tasks apparently new')
                if maybeOld>0:
                    print ('TypeTodo: \'' +cDb.name +'\' DB have ' +str(maybeOld) +' tasks apparently old')


        self.reportFetchReset= False

        if self.callbackFetch:
            sublime.set_timeout(self.callbackFetch, 0)

        return success