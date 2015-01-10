# coding= utf-8

import sys, re, os, time, codecs
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

#todo 44 (config) +0: handle saving project - existing and blank

#todo 89 (db) +0: save context (+-2 strings of code) with task. NOT for 'file' mode


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
    projUser= '*Anon*'
    projectRoot= ''
    projectName= ''

#todo 67 (general) +0: move cfg to class
    cfgA= None

    flushTimeout= 5 #seconds
    timerFlush= None
    dirty= False

    dbA= {}
    todoA= None


    def __init__(self, _root, _name):
        self.dbA= {}

        self.timerFlush = Timer(0, None) #dummy

        self.todoA= {}
        self.update(_root, _name)
        self.reset()
        

    def update(self, _root, _name):
        if 'USERNAME' in os.environ: self.projUser= os.environ['USERNAME']

        self.projectName= _name
        self.projectRoot= _root
        if _root == '':
            self.projectRoot= defaultCfg['path']


##
    def reset(self, _force=False):
        cfgPath= os.path.join(self.projectRoot, self.projectName +'.do')

#todo 149 (cfg) +5: make use of more than one (last) cfg string
        cfgFound= False
        if not _force: #else skip directly to global init
            cfgFound= readCfg(cfgPath)


        if not cfgFound: 
            cfgFound= initGlobalDo()

            if not cfgFound:
                return

            if self.projectName != '': #save new named project .do
                self.todoA.clear() #old tasks are trash
                
                cfgFound['file']= cfgPath
                with codecs.open(cfgPath, 'w+', 'UTF-8') as f:
                  f.write(cfgFound['header'])

        if cfgFound == self.cfgA: #no changes
            return

        print ('TypeTodo: reset db')
        self.cfgA= cfgFound

#todo 170 (cfg) +0: build list of cfg's to pass to db.reset()
        dbId= 0
        self.dbA.clear() #new db array

        if True:
            self.dbA[dbId]= TodoDbFile(cfgFound, self)
            dbId+= 1
        if cfgFound['engine']== 'mysql':
            self.dbA[dbId]= TodoDbSql(cfgFound, self)
            dbId+= 1
        if cfgFound['engine']== 'http':
            self.dbA[dbId]= TodoDbHttp(cfgFound, self)
            dbId+= 1

        for iT in self.todoA: #set all unsaved
            self.todoA[iT].setSaved(False)

        self.fetch() #sync all db at first
        self.flush(True)


    def store(self, _id, _state, _cat, _lvl, _fileName, _comment):
        self.timerFlush.cancel()
        self.reset()

#todo 82 (fix) +0: error on creating/flushing todos in the file that is placed NOT under project path
        if _fileName and self.projectRoot:
            _fileName= os.path.relpath(_fileName, self.projectRoot)
        _fileName= _fileName or ''

        _id= int(_id)

#todo 66 (db) +0: handle unresponsive db task creation
        newId= _id or 0
        if not _id:
            for db in self.dbA:
                tryMaxId= self.dbA[db].newId()
                if not tryMaxId:
                    continue
                newId= max(newId, tryMaxId)

        if not newId:
            sublime.status_message('Todo creation failed, see console for info')
            return False

        strStamp= int(time.time())

#todo 71 (db) +0: instantly remove blank new task from cache before saving if set to +
        if newId not in self.todoA: #for new and repairing tasks
            self.todoA[newId]= TodoTask(newId, self.projectName, self.projUser, strStamp, self)

        if _id:
            self.dirty= True
            self.todoA[newId].set(_state, _cat, _lvl, _fileName, _comment, self.projUser, strStamp)

        self.timerFlush = Timer(self.flushTimeout, self.flush)
        self.timerFlush.start()

        return newId

    def flush(self, _atExit=False):
        self.timerFlush.cancel()

        flushOk= True
        for dbN in self.dbA:
            if (self.dirty) or (dbN==0):
                flushOk= flushOk and self.dbA[dbN].flush(dbN)
        
        if flushOk:
            sublime.set_timeout(lambda: sublime.status_message('TypeTodo saved'), 0)

            self.dirty= False
            return

#todo 92 (flush) +0: limit flush retries
        if not _atExit:
            sublime.set_timeout(lambda: sublime.status_message('TypeTodo error: cannot flush todo\'s.  Will retry in 5 sec\'s'), 0)
            self.timerFlush = Timer(self.flushTimeout, self.flush)
            self.timerFlush.start()
        else:
            sublime.error_message('TypeTodo error:\n\tcannot flush todo\'s')


#macro
#   1. roll over all db's
#   2. fetch unbinded task lists
#   3. compare if new or updated or outdated
#       3.1. join int working list
#       3.2. reset other db's 'saved' flag

    def fetch(self, _id=False):
        success= True

        for dbN in self.dbA:
            todoA= self.dbA[dbN].fetch(_id)
            if todoA==False:
                return False

            maybeNew= 0
            for iT in todoA: #each fetched task have to be compared to existing
                task= todoA[iT]
                __id= task.id

#todo 112 (multidb) +0: Use and check tasks .version
                isNew= __id not in self.todoA
                diffStamp= 0
                if not isNew:
                    diffStamp= task.stamp -self.todoA[__id].stamp

                if not isNew:
                    self.todoA[__id].setSaved(True, dbN)

                if isNew or diffStamp>0:
                    if diffStamp>60: #some tasks can be skipped (in report only!) due to unsaved seconds in 'file' db
                        print ('TypeTodo: \'' +self.dbA[dbN].name +'\' DB is new at ' +str(__id))
                    elif diffStamp>0:
                        maybeNew+= 1
                    self.todoA[__id]= task
                    self.todoA[__id].setSaved(False) #all but current db are saved for task
                    self.todoA[__id].setSaved(True, dbN)

                elif diffStamp<0:
                    print ('TypeTodo: \'' +self.dbA[dbN].name +'\' DB is old at ' +str(__id))
                    self.todoA[__id].setSaved(False, dbN)

                self.dirty= True

            if maybeNew>0:
                print ('TypeTodo: \'' +self.dbA[dbN].name +'\' DB have ' +str(maybeNew) +' tasks apparently new')

        return success


