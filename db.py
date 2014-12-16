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

#todo 102 (config) +0: handle 'updated' flag to make global update for HTTP

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

#todo 109 (multidb) +5: Make multiple .db connectons for one base.
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
#todo 145 (cfg) +0: repair onfly switching
        cfgPath= os.path.join(self.projectRoot, self.projectName +'.do')

#todo 149 (cfg) +5: make use of more than one (last) cfg string
        cfgFound= False
        if not _force:
            cfgFound= readCfg(cfgPath)

        if not cfgFound: 
            cfgFound= initGlobalDo()

            if not cfgFound:
                return

#todo 118 (multidb) +0: check why only 'file' mode
            if cfgFound['engine'] != '': #save new project .do
                with codecs.open(cfgPath, 'w+', 'UTF-8') as f:
                  f.write(cfgFound['header'])


        if cfgFound == self.cfgA: #no changes
            return

        self.cfgA= cfgFound

        self.dbA= {}
        self.dbA['file']= TodoDbFile(self.todoA, self.projUser, self.projectName, cfgPath, cfgFound['header']) #throw in cfgString to restore it in file
        if cfgFound['engine']== 'mysql':
            self.dbA['mysql']= TodoDbSql(self.todoA, self.projUser, self.projectName, cfgFound['addr'], cfgFound['login'], cfgFound['passw'], cfgFound['base'])
        if cfgFound['engine']== 'http':
            self.dbA['http']= TodoDbHttp(self.todoA, self.projUser, self.projectName, cfgFound['addr'], cfgFound['base'], cfgFound['login'], cfgFound['passw'])

        self.fetch() #sync all db at first
        self.flush()


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

        strStamp= time.localtime()

#todo 71 (db) +0: instantly remove blank new task from cache before saving if set to +
        if newId not in self.todoA: #for new and repairing tasks
            self.todoA[newId]= TodoTask(newId, self.projectName, self.projUser, strStamp)

        if _id:
            self.dirty= True
            self.todoA[newId].set(_state, _cat, _lvl, _fileName, _comment, self.projUser, strStamp)

        self.timerFlush = Timer(self.flushTimeout, self.flush)
        self.timerFlush.start()

        return newId

#todo 148 (general) +10: handle fucking unresponsive servers! Especially http
    def flush(self, _atExit=False):
        self.timerFlush.cancel()

        flushOk= True
        for db in self.dbA:
            if self.dirty or db=='file':
                flushOk= flushOk and self.dbA[db].flush()
        
        if flushOk:
            sublime.set_timeout(lambda: sublime.status_message('TypeTodo saved'), 0)

#todo 69 (multidb) +0: behave at individual save results of each db
            for iT in self.todoA:
                self.todoA[iT].setSaved(True)

            self.dirty= False
            return

#todo 92 (flush) +0: limit flush retries
        if not _atExit:
            sublime.set_timeout(lambda: sublime.status_message('TypeTodo error: cannot flush todo\'s.  Will retry in 5 sec\'s'), 0)
            self.timerFlush = Timer(self.flushTimeout, self.flush)
            self.timerFlush.start()
        else:
            sublime.error_message('TypeTodo error:\n\tcannot flush todo\'s')


    def fetch(self, _id=False):
        success= True

#todo 119 (multidb) +0: check if self.todoA need to be wiped
        for db in self.dbA:

            todoA= self.dbA[db].fetch(_id)
            if not todoA:
                print(db)
                return False

            for iT in todoA: #each fetched task have to be compared to existing
                task= todoA[iT]
                __id= task.id

#todo 112 (multidb) +0: Use and check tasks .version x

                if __id not in self.todoA:
                    task.setSaved(True)
                    self.todoA[__id]= task

#todo 146 (multidb) +5: check timezone when fetching from distant source
#todo 147 (multidb) +10: item should be unsaved for incomplete db; manage saved[] for different db's
                else:
                    if task.stamp > self.todoA[__id].stamp:
                        task.setSaved(False)
                        self.dirty= True
                        self.todoA[__id]= task

        return success





class TodoTask():
    #static, defined at creation
    id= 0
    project= ''
    creator= ''

    cStamp= False #used only for dbFile

    #updatable
    state= False
    cat= ''
    lvl= ''
    fileName= ''
    comment= ''
    editor= ''
    stamp= False
    version= 1

    canSave= False #for skipping at file mode
    saved= True

    def __init__(self, _id, _project, _creator, _stamp):
        self.canSave= False
        self.saved= True

        self.id= _id
        self.project= _project
        self.creator= _creator
        self.cStamp= _stamp


    def set(self, _state, _cat, _lvl, _fileName, _comment, _editor, _stamp):
        self.canSave= True
        self.saved= False

        if _state != '': self.state= _state
        self.cat= _cat or ''
        self.lvl= int(_lvl) or 0
        self.fileName= _fileName or ''
        self.comment= _comment
        self.editor= _editor
        self.stamp= _stamp

    def setSaved(self, _state=True):
        self.saved= _state

