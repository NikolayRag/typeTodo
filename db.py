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

#  todo 44 (config, db, feature, unsolved) -1: handle saving project - existing and blank; transfer db for involved files

#  todo 89 (db, feature) +1: save context (+-2 strings of code) with task

# todo 2045 (db, issue, fix) +0: New Id sync warning when having 2 http noticed
#
#   Manages .todoA[] task collection within .dbA[] databases.
#   Uses supplied .config to locate '.do' config file.
#

class TodoDb():
    config= None #Config()

    flushLastResult= True
    flushTimeout= 30 #seconds
    timerReset= None
    resetMutex= False

    reservedId= 0 #returned by .new()
    reserveLocker= None
    reusedId= None #for immediately canceled tasks

    dbA= None #active databases, defined from config
    todoA= None #doplets
    todoAInited= False

    callbackFetch= None

    reportFlush= False

    def __init__(self, _fetchCallback, _cfg):
        self.dbA= {}
        self.todoA= {}
        self.timerReset = Timer(0, None) #dummy

        self.callbackFetch= _fetchCallback
        self.config= _cfg

        self.reserveLocker= threading.Event() #dummy
        self.reserveLocker.set()

        self.pushReset()
        






#   (re)Start .reset() asynchronously.
#   _delay used to join spammed requests into one.
    def pushReset(self, _delay=1): #leave 1 to remove spam
        if self.resetMutex:
            return
            
        self.timerReset.cancel()
        self.timerReset= Timer(_delay, self.reset)
        self.timerReset.start()



#   Reread config for current project and maintain databases list consistency.
#   Synchronises all databases contents by fetching all and then saving back
#    difference.
#
#Macro:
#   1. get new cfg
#       1.1. flush if unchanged
#   2. fetch using new
#   3. flush using new

    def reset(self):
        self.resetMutex= True

        if not self.config.update() and len(self.dbA):
            self.fetch()
            self.flush()

            self.resetMutex= False
            return


        print('TypeTodo: reset db')

        self.releaseId()

        dbId= 0
        self.dbA.clear() #new db array

        for cSetting in self.config.getSettings():
            if cSetting.engine=='file':
                cEngClass= TodoDbFile
            elif cSetting.engine=='mysql':
                cEngClass= TodoDbSql
            elif cSetting.engine=='http':
                cEngClass= TodoDbHttp
            else:
                continue

            self.dbA[dbId]= cEngClass(self, cSetting, dbId)
            dbId+= 1

        self.newId() #run prefetch

        self.fetch(True)
        self.flush()

        self.resetMutex= False







#   Cache newIdGet() value to be returned next call.
#   newId() works asynchronously to avoid database access lag, mostly HTTP.
#   *First call is initial, returning None;
#    it caches new ID to be returned in subsequent calls
#
#   Return previously cached newIdGet() value, None on first call

    def newId(self):
        self.reserveLocker.wait()

        okId= self.reservedId

        self.reserveLocker.clear() #second call to newId() will suspend till newIdGet() done
        Timer(0, self.newIdGet).start()

        return okId



#   Get same mininum available new task ID from all databases.
#
#   Return new task ID if any DB succeeded
#   Return False if none DB succeeded

    def newIdGet(self):
        cId= self.reservedId +1

        tries= 1
        while True:
            ids= []
            for cDb in self.dbA:
                ids.append(self.dbA[cDb].newId(cId) or 0)

            cId= max(ids)
            if cId==min(ids):
                break

            if tries<=0:
                if not max(ids):
                    print('TypeTodo error: Cannot reserve new ID for any databases. Check their settings.')

                for cDb in self.dbA:
                    if ids[cDb] != max(ids):
                        print('TypeTodo warning: Cannot synchronize new Id within ' +self.dbA[cDb].name +' database.')

                break

            tries-= 1

        self.reservedId= cId
        print('TypeTodo: Id reserved: ' +str(self.reservedId))
        self.reserveLocker.set()







#   Release database's unused reserved ID
#   Called at the Sublime's exit and config reset.

# todo 1984 (db, issue, fix) +0: some db's are skipped at exit if *some* dbs configured (tested 3 other than File)
    def releaseId(self, _atExit=False):
        self.reservedId-= 1 #used to continue id when all db's changed at once
        for db in self.dbA:
            self.dbA[db].releaseId(_atExit)







#   Form new or updated task and (re)init asynchronous flush()
#
#   Return actual task ID, meaningful for new task creation;
#   Or 0 on error.

    def store(self, _id, _state, _tags, _lvl, _fileName, _comment):
        if _fileName and self.config.projectRoot:
            if (os.path.splitdrive(_fileName)[0]==os.path.splitdrive(self.config.projectRoot)[0]):
                _fileName= os.path.relpath(_fileName, self.config.projectRoot)
                
        _fileName= _fileName or ''

        _id= int(_id)

        cId= _id or 0
        if not _id:
            if self.reusedId:
                cId= self.reusedId
                self.reusedId= None
            else:
                cId= self.newId()

            if not cId:
                sublime.status_message('Todo creation failed, see console for info')
                return False


        if cId not in self.todoA: #for new and repairing tasks
            self.todoA[cId]= TodoTask(cId, self.config.projectName, self)

        if _id:
            if self.todoA[cId].initial and _comment=='' and (_state=='+' or _state=='!'):
                del self.todoA[cId]
                self.reusedId= cId
            else:
                self.reportFlush= True
                strStamp= int(time.time())
                self.todoA[cId].set(_state, _tags, _lvl, _fileName, _comment, self.config.projectUser, strStamp)

        self.pushReset(self.flushTimeout)

        return cId







#   Flush all tasks from .todoA[] collection to all .dbA[] databases
#   Retry on any error
#   Shows error message at first error, reset at first succeed afterwards.
#
#   *Notice that task have .savedA[] state for every database so it should not be
#    saved subsequently if succeeded once for particular database.

    def flush(self):
        flushOk= True

        for dbN in self.dbA:
            flushEngineOk= self.dbA[dbN].flush()
            flushOk= flushOk and flushEngineOk

            #resave 'hang' tasks, mainly at db error
            for iT in self.todoA:
                curTodo= self.todoA[iT]
                if curTodo.saveProgress(dbN):
                    curTodo.setSaved(SAVE_STATES.FORCE, dbN) #'FORCE' coz task already pass shadow filter


        if flushOk:
            if self.reportFlush:
                sublime.set_timeout(lambda: sublime.status_message('TypeTodo saved'), 0)

            self.pushReset(self.flushTimeout)

            self.reportFlush= False
            self.flushLastResult= True
            return


        if self.flushLastResult:
            self.flushLastResult= False
            sublime.set_timeout(lambda: sublime.error_message('TypeTodo error:\n\n\tcannot flush todo\'s.  Will retry later'), 0)
        else:
            sublime.set_timeout(lambda: sublime.status_message('TypeTodo error: cannot flush todo\'s.  Will retry later'), 0)


        self.pushReset(self.flushTimeout)










#   Fetch all databases specified in .dbA[] (set within .reset())
#   Updates active tasks .todoA[] collection with newtasks based on UTC timestamp
#
#   return True if ANY of DB was fetched
#
#macro
#
#   1. roll over all db's
#       1.1. fetch unbinded task lists
#       1.2. compare each fetched task against actual for being:
#           1.2.1. new or updated
#           1.2.2. outdated
#           1.2.3. equal
#       1.3. all remaining tasks are marked to be saved as unexistent

# todo 1818 (db) +0: make compairing inconsistencies by versions where they available (not file atm)
    def fetch(self, _resetDb=False):
        self.todoAInited= False #lock, mainly for file newId/resetId consistence

        if _resetDb:
            for iT in self.todoA: #reset all existing unsaved, coz states got loose from db's
                self.todoA[iT].savedReset()

        for dbN in self.dbA: #oved dbs
            cDb= self.dbA[dbN]
            todoA= cDb.fetch()
            if todoA==False:
                continue

            for iT in todoA: #over tasks
                task= todoA[iT]

                isNew= iT not in self.todoA
                diffStamp= 0
                if not isNew:
                    diffStamp= task.stamp -self.todoA[iT].stamp


                if isNew or diffStamp>0:
                    if not _resetDb or diffStamp>0: #skip initially added, coz its redundant
                        print('TypeTodo: \'' +cDb.name +'\' DB is new at ' +str(iT))

                    self.todoA[iT]= task
                    self.todoA[iT].setSaved(SAVE_STATES.FORCE) #all but current db are saved for task
                    self.todoA[iT].setSaved(SAVE_STATES.IDLE, dbN)


                elif diffStamp<0:
                    if _resetDb: #show verbose only at start/reconfiguring, otherwise 'new' message is enough
                        print('TypeTodo: \'' +cDb.name +'\' DB is old at ' +str(iT))
                    
                    self.todoA[iT].setSaved(SAVE_STATES.FORCE, dbN)


                #relax equal tasks
                if not isNew and diffStamp==0:
                    self.todoA[iT].setSaved(SAVE_STATES.IDLE, dbN)


            #fill INIT back for one was unexistent in dbN
            for iT in self.todoA:
                if self.todoA[iT].saveInit(dbN):
                    print('TypeTodo: \'' +cDb.name +'\' DB is missing at ' +str(iT))
                    self.todoA[iT].setSaved(SAVE_STATES.FORCE, dbN)

            self.todoAInited= True


        if self.callbackFetch:
            sublime.set_timeout(self.callbackFetch, 0)
