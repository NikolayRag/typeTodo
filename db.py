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

#todo 89 (db, feature) +0: save context (+-2 strings of code) with task


#
#   Manages .todoA[] task collection within .dbA[] databases.
#   Uses supplied .config to locate '.do' config file.
#

class TodoDb():
    config= None #Config()

    flushLastResult= True
    flushTimeout= 30 #seconds
    timerReset= None

    reservedId= 0 #returned by .new()
    reserveLocker= None

    dbA= None #active databases, defined from config
    todoA= None #doplets

    callbackFetch= None

    reportFetchReset= False
    reportFlush= False

    def __init__(self, _fetchCallback, _cfg):
        self.dbA= {}
        self.todoA= {}
        self.timerReset = Timer(0, None) #dummy

        self.callbackFetch= _fetchCallback
        self.config= _cfg

        self.reservedId= 0
        self.reserveLocker= threading.Event()
        self.reserveLocker.set()

        self.pushReset()
        



#todo 1662 (check, db) +0: unsaved doplet is overriden probably at changing config



#   (re)Start .reset() asynchronously.
#   _delay used to join spammed requests into one.

    def pushReset(self, _delay=1): #leave 1 to remove spam
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
        if not self.config.update() and len(self.dbA):
            self.fetch()
            self.flush()
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

        self.fetch()
        self.flush()







#   Cache newIdGet() value to be returned next call.
#   newId() works asynchronously to avoid database access lag, mostly HTTP.
#   *First call is initial, returning 0;
#    it caches new ID to be returned in subsequent calls
#
#   Return previously cached newIdGet() value

    def newId(self):
        self.reserveLocker.wait()

        okId= self.reservedId

        self.reserveLocker.clear() #second call to newId() will suspend till newIdGet() done
        Timer(0, self.newIdGet).start()

        return okId



#   Get same mininum available new task ID from all databases.
#
#   Return new task ID

#todo 1797 (db, cleanup) +0: React on newId() errors correctly

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
        self.reserveLocker.set()







#   Release database's unused reserved ID
#   Called at the Sublime's exit.
#=todo 258 (db, cleanup) +5: release prefetched id at exit

    def releaseId(self):
        for db in self.dbA:
            self.dbA[db].releaseId(self.reservedId)





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
            flushOk= flushOk and self.dbA[dbN].flush(dbN)

            #resave 'hang' tasks, mainly at db error
            for iT in self.todoA:
                curTodo= self.todoA[iT]
                if curTodo.savedA[dbN]==SAVE_STATES.HOLD:
                    curTodo.setSaved(SAVE_STATES.READY, dbN)


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
#       1.2. compare if new or updated or outdated
#           1.2.1. join into working list
#           1.2.2. reset other db's 'saved' flag

#todo 1818 (db) +0: make compairing inconsistencies by versions where they available (not file atm)
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
