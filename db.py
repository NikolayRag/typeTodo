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

#=todo 44 (config, doc) +0: handle saving project - existing and blank; transfer db for involved files

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

#todo 67 (cfg) +0: move cfg to class
#=todo 333 (cfg) +0: make .do read-save cycle more crisp and time-compact
    cfgA= None

    maxflushRetries= 3
    flushTimeout= 30 #seconds
    timerFlush= None
    timerReset= None
    dirty= False

    dbA= {}
    todoA= None


    def __init__(self, _root, _name):
        self.dbA= {}

        self.timerFlush = Timer(0, None) #dummy
        self.timerReset = Timer(0, None) #dummy

        self.todoA= {}
        self.update(_root, _name)
        self.pushReset()
        

    def update(self, _root, _name):
        if 'USERNAME' in os.environ: self.projUser= os.environ['USERNAME']

        self.projectName= _name
        self.projectRoot= _root
        if _root == '':
            self.projectRoot= defaultCfg['path']


    def pushReset(self, _delay=1): #leave 1 to remove spam
        self.timerReset.cancel()
        self.timerReset= Timer(_delay, self.reset)
        self.timerReset.start()

#Macro:
#    - get new cfg
#    - flush using old if any
#    - fetch using new
#    - flush using new

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

        self.flush(True)

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
            self.todoA[iT].setSaved(SAVE_STATES.READY)

        self.fetch() #sync all db at first
        self.flush(True)


    def store(self, _id, _state, _tags, _lvl, _fileName, _comment):
        self.timerFlush.cancel()

        if _fileName and self.projectRoot:
            if (os.path.splitdrive(_fileName)[0]==os.path.splitdrive(self.projectRoot)[0]):
                _fileName= os.path.relpath(_fileName, self.projectRoot)
                
        _fileName= _fileName or ''

        _id= int(_id)

#=todo 305 (general) +10: make .newId take in respect all db's at once
        newId= _id or 0
        if not _id:
            for db in self.dbA:
                newId= max(newId, self.dbA[db].newId() or 0)

        if not newId:
            sublime.status_message('Todo creation failed, see console for info')
            return False

        strStamp= int(time.time())

#=todo 71 (db) -1: instantly remove blank new task from cache before saving if set to +
        if newId not in self.todoA: #for new and repairing tasks
            self.todoA[newId]= TodoTask(newId, self.projectName, self.projUser, strStamp, self)

        if _id:
            self.dirty= True
            self.todoA[newId].set(_state, _tags, _lvl, _fileName, _comment, self.projUser, strStamp)

        self.flushRetries= self.maxflushRetries
        self.timerFlush= Timer(self.flushTimeout, self.flush)
        self.timerFlush.start()

        return newId


    def flush(self, _runOnce=False):
        self.timerFlush.cancel()
        if not self.cfgA:
            return

        flushOk= True
        for dbN in self.dbA:
            flushOk= flushOk and self.dbA[dbN].flush(dbN)
        
#todo 280 (db, flush) +0: .dirty used only to display message; should be removed at all
        if not self.dirty: #todo 240 (db, flush) +0: hadn't to save, needed for file mode;  should be reviewed
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

        sublime.set_timeout(self.maintain, 0)

        return success


    def maintain(self):
        cWnd= sublime.active_window()
        if not cWnd: return

        cView= cWnd.active_view()
        if not cView: return

        cView.run_command('typetodo_maintain', {})

