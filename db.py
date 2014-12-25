# coding= utf-8

import sys, re, os, time, codecs
from threading import Timer

if sys.version < '3':
    from dbFile import *
    from dbSql import *
    from dbHttp import *
else:
    from .dbFile import *
    from .dbSql import *
    from .dbHttp import *

#todo 44 (config) +0: handle saving project - existing and blank

#todo 89 (db) +0: save context (+-2 strings of code) with task. NOT for 'file' mode

#todo 102 (config) +0: (wut) handle 'updated' flag to make global update for HTTP

defaultCfg= {
    'path': '',
    'file': '',
    'defaultHttpApi': 'typetodo.com',
    'blankdb': {
        'engine': '',
        'addr': '',
        'login': '',
        'passw': '',
        'base': '',
        'header': "# uncomment and configure. LAST matched line matters:\n"\
            +"# mysql 127.0.0.1 username password scheme\n"\
            +"# http 127.0.0.1 repository [username password]\n"
    }
}


def readCfg(_cfgPath):
    reMysqlStr= "(?P<enginesql>mysql)\s+(?P<addrs>[^\s]+)\s+(?P<logins>[^\s]+)\s+(?P<passws>[^\s]+)\s+(?P<bases>[^\s]+)"
    reHttpStr= "(?P<enginehttp>http)\s+(?P<addrh>[^\s]+)\s+(?P<baseh>[^\s]+)\s*(?P<loginh>[^\s]*)\s*(?P<passwh>[^\s]*)"
    reCfg= re.compile("^\s*(?:" +reMysqlStr +"|" +reHttpStr +")\s*$")

    try:
        f= codecs.open(_cfgPath, 'r', 'UTF-8')
    except:
        f= False
    if not f:
        return False

    foundCfg= defaultCfg['blankdb'].copy()
    headerCollect= ''

    while True:
        l= f.readline().splitlines()
        if l==[] or l[0]=='' or not l[0]:
            break

        cfgString= l[0]

        headerCollect+= cfgString +"\n"
        #catch last matched config
        cfgFoundTry= reCfg.match(cfgString)
        if cfgFoundTry:
            curCfg= cfgFoundTry.groupdict()
            if curCfg['enginesql']:
                foundCfg= {
                    'engine': curCfg['enginesql'],
                    'addr': curCfg['addrs'],
                    'login': curCfg['logins'],
                    'passw': curCfg['passws'],
                    'base': curCfg['bases'],
                }
            elif curCfg['enginehttp']:
                foundCfg= {
                    'engine': curCfg['enginehttp'],
                    'addr': curCfg['addrh'],
                    'login': curCfg['loginh'],
                    'passw': curCfg['passwh'],
                    'base': curCfg['baseh'],
                }

    foundCfg['header']= headerCollect
    foundCfg['file']= _cfgPath
    return foundCfg


def initGlobalDo(_force=False):
    if not _force:
        cfgFoundTry= readCfg(defaultCfg['file'])
        if cfgFoundTry:
            return cfgFoundTry

    cfgFoundTry= defaultCfg['blankdb'].copy()

    httpInitFlag= True

    #request new radnom public repository
    if httpInitFlag:
        req = urllib2.Request('http://' +defaultCfg['defaultHttpApi'] +'/?=newrep')
        try:
            cfgFoundTry['engine']= 'http'
            cfgFoundTry['addr']= defaultCfg['defaultHttpApi']
            cfgFoundTry['base']= bytes.decode( urllib2.urlopen(req).read() )
            cfgFoundTry['header']+= cfgFoundTry['engine'] +" " +cfgFoundTry['addr'] +" " +cfgFoundTry['base'] +"\n"
        except:
            httpInitFlag= False

    if not httpInitFlag:
        cfgFoundTry= defaultCfg['blankdb'].copy()
        sublime.set_timeout(lambda: sublime.error_message('TypeTodo error:\n\tcannot init new HTTP repository,\n\tdefault storage mode will be `file`'), 1000)
    else:
        print("New TypeTodo repository: " +cfgFoundTry['base'])
        sublime.set_timeout(lambda: sublime.status_message('New TypeTodo repository initialized'), 1000)

    try:
        with codecs.open(defaultCfg['file'], 'w+', 'UTF-8') as f:
            f.write(cfgFoundTry['header'])
    except:
        return False

    return cfgFoundTry


def plugin_loaded():
    defaultCfg['path']= os.path.join(sublime.packages_path(), 'User')
    defaultCfg['file']= os.path.join(defaultCfg['path'], '.do')
    initGlobalDo()


if sys.version < '3':
    plugin_loaded()



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
                newId= int(max(newId, self.dbA[db].newId()))

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
#   3. compare if new or updated
#       3.1. join int working list
#       3.2. unset other db's 'saved' flag

    def fetch(self, _id=False):
        success= True

#todo 119 (multidb) +0: check if self.todoA need to be wiped
        for dbN in self.dbA:
            todoA= self.dbA[dbN].fetch(_id)
            if todoA==False:
                return False

            for iT in todoA: #each fetched task have to be compared to existing
                task= todoA[iT]
                __id= task.id

#todo 112 (multidb) +0: Use and check tasks .version
                isNew= __id not in self.todoA
                isUpdated= False
                if not isNew:
                    isUpdated= task.stamp > (self.todoA[__id].stamp +60)

                if isNew or isUpdated:
                    if isUpdated:
                        print ('DB\'s differs at ' +str(dbN) +':' +str(__id))
                    task.setSaved(False) #all but current db are saved for task
                    if dbN != 0: #'coz file db treat .saved other way
                        task.setSaved(True, dbN)
                    self.todoA[__id]= task

                self.dirty= True

        return success





class TodoTask():
    #static, defined at creation
    id= 0
    project= ''
    creator= ''

    cStamp= False #used only for dbFile; unix time

    #updatable
    state= False
    cat= ''
    lvl= ''
    fileName= ''
    comment= ''
    editor= ''
    stamp= False # unix time
    version= 1

    savedA= {} #['engine']= state; cleared at reseting db's

    parentDb= False #used to set saved[] state per db engine

    def __init__(self, _id, _project, _creator, _stamp, _parentDB):
        self.id= _id
        self.project= _project
        self.creator= _creator
        self.cStamp= _stamp

        self.savedA= {}
        self.parentDb= _parentDB
        self.setSaved(True) #'file' (0) indicates it is initial; not set True at flush to save bulk every time after first .set()

    def set(self, _state, _cat, _lvl, _fileName, _comment, _editor, _stamp):
        self.setSaved(False)

        if _state != '': self.state= _state
        self.cat= _cat or ''
        self.lvl= int(_lvl) or 0
        self.fileName= _fileName or ''
        self.comment= _comment
        self.editor= _editor
        self.stamp= _stamp

    def setSaved(self, _state=True, _engine=False):
        if _engine==False: #set all
            for dbEN in self.parentDb.dbA:
                self.savedA[dbEN]= _state
        else:
            self.savedA[_engine]= _state
        return True