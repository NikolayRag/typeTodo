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

#todo 44 (config, db) +0: handle saving project - existing and blank; transfer db for involved files

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
    resetPending= False
    dirty= False

    reservedId= 0
    reserveEvent= None

    dbA= None
    todoA= None

    callbackFetch= None

    def __init__(self, _callback, _cfg):
        self.dbA= {}
        self.todoA= {}
        self.timerFlush = Timer(0, None) #dummy

        self.callbackFetch= _callback
        self.config= _cfg

        self.reservedId= 0
        self.reserveEvent= threading.Event()
        self.reserveEvent.set()

        self.pushReset()
        






#todo 1250 (db, consistency, feature) +0: fetch db periodically
    def pushReset(self, _delay=1000): #leave 1 to remove spam
        self.resetPending= True
        sublime.set_timeout(self.reset, _delay)

#Macro:
#    - get new cfg
#       - flush if unchanged
#    - fetch using new
#    - flush using new

    def reset(self):
        if not self.resetPending:
            return
        self.resetPending= False


        if not self.config.update() and len(self.dbA):
            self.flush(True)
            return


        print ('TypeTodo: reset db')

        dbId= 0
        self.dbA.clear() #new db array

        cSettingId= -1
        for cSetting in self.config.settings:
            cSettingId+= 1

            if cSetting.engine=='file':
                cEngClass= TodoDbFile(self, cSettingId)
            elif cSetting.engine=='mysql':
                cEngClass= TodoDbSql(self, cSettingId)
            elif cSetting.engine=='http':
                cEngClass= TodoDbHttp(self, cSettingId)
            else:
                continue

            self.dbA[dbId]= cEngClass
            dbId+= 1


        self.newId() #run prefetch

        for iT in self.todoA: #set all unsaved
            self.todoA[iT].setSaved(SAVE_STATES.READY)

        self.fetch() #sync all db at first
        self.flush(True)








#macro
#   pre: pick event set
#   wait for pick event to set
#   set return cached
#   go pick next
    def newId(self):
        self.reserveEvent.wait()

        okId= self.reservedId #first call is initial, result should not be used

        self.reserveEvent.clear() #second call to newId() will suspend till newIdGet() done
        sublime.set_timeout(self.newIdGet, 0)

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
            cId= self.newId()

        if not cId:
            sublime.status_message('Todo creation failed, see console for info')
            return False

        strStamp= int(time.time())

#todo 71 (db, cleanup) -1: instantly remove blank new task from cache before saving if set to + or !
        if cId not in self.todoA: #for new and repairing tasks
            self.todoA[cId]= TodoTask(cId, self.config.projectName, self.config.projectUser, strStamp, self)

        if _id:
            self.dirty= True
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
        
#todo 280 (db, flush, cleanup) +0: .dirty used only to display message; should be removed at all
        if not self.dirty: #todo 240 (db, flush, cleanup) +0: hadn't to save, needed for file mode;  should be reviewed
            return
            
        if flushOk:
            sublime.set_timeout(lambda: sublime.status_message('TypeTodo saved'), 0)

            self.dirty= False
            return

        if not _runOnce:
            self.flushRetries-= 1
            if self.flushRetries>0:
                sublime.set_timeout(lambda: sublime.status_message('TypeTodo error: cannot flush todo\'s.  Will retry ' +str(self.flushRetries) +' more times in ' +str(self.flushTimeout) +' sec\'s'), 0)
                self.timerFlush = Timer(self.flushTimeout, self.flush)
                self.timerFlush.start()

        if _runOnce or self.flushRetries==0:
            sublime.set_timeout(lambda: sublime.error_message('TypeTodo error:\n\tcannot flush todo\'s'), 0)








#macro
#   1. roll over all db's
#   2. fetch unbinded task lists
#   3. compare if new or updated or outdated
#       3.1. join into working list
#       3.2. reset other db's 'saved' flag

    def fetch(self, _id=False):
        success= False

        for dbN in self.dbA:
            todoA= self.dbA[dbN].fetch(_id)
            if todoA==False:
                continue

            success= True

            maybeNew= 0
            for iT in todoA: #each fetched task have to be compared to existing
                task= todoA[iT]
                __id= task.id

                isNew= __id not in self.todoA
                diffStamp= 0
                if not isNew:
                    diffStamp= task.stamp -self.todoA[__id].stamp
#todo 279 (check) +0: see if states dont interfere while task is in-save
                if not isNew:
                    self.todoA[__id].setSaved(SAVE_STATES.IDLE, dbN)

                if isNew or diffStamp>0:
                    if diffStamp>60: #some tasks can be skipped (in report only!) due to unsaved seconds in 'file' db
                        print ('TypeTodo: \'' +self.dbA[dbN].name +'\' DB is new at ' +str(__id))
                    elif diffStamp>0:
                        maybeNew+= 1
                    self.todoA[__id]= task
                    self.todoA[__id].setSaved(SAVE_STATES.READY) #all but current db are saved for task
                    self.todoA[__id].setSaved(SAVE_STATES.IDLE, dbN)

                elif diffStamp<0:
                    print ('TypeTodo: \'' +self.dbA[dbN].name +'\' DB is old at ' +str(__id))
                    self.todoA[__id].setSaved(SAVE_STATES.READY, dbN)

                self.dirty= True

            #'apparently new' mean that stamp difference is less than 60s. It is likely a subject, when comparing with 'file' DB with seconds truncated. In this case 'file' is treated as little older and is replaced. As 'file' is anyway replaced at each flush, it doesn't make any difference to normal behavior and is messaged just in case.
            if maybeNew>0:
                print ('TypeTodo: \'' +self.dbA[dbN].name +'\' DB have ' +str(maybeNew) +' tasks apparently new')

        if self.callbackFetch:
            sublime.set_timeout(self.callbackFetch, 0)

        return success