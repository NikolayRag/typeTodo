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



defaultCfg= {
    'path': '',
    'file': '',
    'factorydb': {
        'engine': 'http',
        'addr': 'jobr.c',
        'login': '',
        'passw': '',
        'base': '',
        'header': "# uncomment and configure. LAST matched line matters:\n"\
            +"# mysql 127.0.0.1 username password scheme\n"\
            +"# http 127.0.0.1 repository [username] [password]\n"
    }
}

#todo 80 (config) +0: initialize with http engine
def initGlobalDo():
    cfgFound= defaultCfg['factorydb'].copy()
    cfgFound['base']= '1212122'
    cfgFound['header']+= cfgFound['engine'] +" " +cfgFound['addr'] +" " +cfgFound['base'] +"\n"

    with codecs.open(defaultCfg['file'], 'w+', 'UTF-8') as f:
      f.write(cfgFound['header'])

    return cfgFoundTry


def plugin_loaded():
    defaultCfg['path']= os.path.join(sublime.packages_path(), 'User')
    defaultCfg['file']= os.path.join(defaultCfg['path'], '.do')
    if not os.path.isfile(defaultCfg['file']):
        print initGlobalDo()


if sys.version < '3':
    plugin_loaded()



'''
   per-project task set
   Read config and set up db engine
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

    db= None
    todoA= None


    def __init__(self, _root, _name):
        self.timerFlush = Timer(0, None) #dummy

        self.update(_root, _name)
        self.reset()

    def update(self, _root, _name):
        if 'USERNAME' in os.environ: self.projUser= os.environ['USERNAME']

        self.projectName= _name
        self.projectRoot= _root
        if _root == '':
            self.projectRoot= defaultCfg['path']


##
    def reset(self):
        cfgPath= os.path.join(self.projectRoot, self.projectName +'.do')

        try: #projects config
            cfgFound= self.readCfg(cfgPath)
        except:
            try: #try load default .do config
                cfgFound= self.readCfg(defaultCfg['file'])

            except: #create default .do config
                cfgFound= initGlobalDo()

            if cfgFound['engine'] != 'file': #save new project .do
                with codecs.open(cfgPath, 'w+', 'UTF-8') as f:
                  f.write(cfgFound['header'])


        if cfgFound == self.cfgA:
            return

        self.flush(True)

        self.cfgA= cfgFound
        self.todoA= {}

        if cfgFound['engine']== 'mysql':
            self.db= TodoDbSql(self.todoA, self.projUser, self.projectName, cfgFound['addr'], cfgFound['login'], cfgFound['passw'], cfgFound['base'])
        elif cfgFound['engine']== 'http':
            self.db= TodoDbHttp(self.todoA, self.projUser, self.projectName, cfgFound['addr'], cfgFound['login'], cfgFound['passw'], cfgFound['base'])
        else:
            self.db= TodoDbFile(self.todoA, self.projUser, self.projectName, cfgPath, cfgFound['header']) #throw in sfgString to restore it in file



    def readCfg(self, _cfgPath):
        reMysqlStr= "(?P<engines>mysql)\s+(?P<addrs>[^\s]+)\s+(?P<logins>[^\s]+)\s+(?P<passws>[^\s]+)\s+(?P<bases>[^\s]+)"
        reHttpStr= "(?P<engineh>http)\s+(?P<addrh>[^\s]+)\s+(?P<baseh>[^\s]+)\s*(?P<loginh>[^\s]*)\s*(?P<passwh>[^\s]*)"
        reCfg= re.compile("^\s*(?:" +reMysqlStr +"|" +reHttpStr +")\s*$")
    
        foundCfg= {
            'engine': 'file',
            'addr': '',
            'login': '',
            'passw': '',
            'base': ''
        }
        collectHeader= ''

        with codecs.open(_cfgPath, 'r', 'UTF-8') as f:
            while True:
                l= f.readline().splitlines()
                if l == []: break
                cfgString= l[0]
                if cfgString == '' or not cfgString:
                    break

                collectHeader+= cfgString +"\n"
                #catch last matched config
                cfgFoundTry= reCfg.match(cfgString)
                if cfgFoundTry:
                    curCfg= cfgFoundTry.groupdict()
                    if curCfg['engines']:
                        foundCfg= {
                            'engine': curCfg['engines'],
                            'addr': curCfg['addrs'],
                            'login': curCfg['logins'],
                            'passw': curCfg['passws'],
                            'base': curCfg['bases'],
                        }
                    elif curCfg['engineh']:
                        foundCfg= {
                            'engine': curCfg['engineh'],
                            'addr': curCfg['addrh'],
                            'login': curCfg['loginh'],
                            'passw': curCfg['passwh'],
                            'base': curCfg['baseh'],
                        }


        foundCfg['header']= collectHeader

        return foundCfg

    def store(self, _id, _state, _cat, _lvl, _fileName, _comment):
        self.reset()

#todo 82 (fix) +0: error on creating/flushing todos in the file that is placed NOT under project path
        if _fileName and self.projectRoot:
            _fileName= os.path.relpath(_fileName, self.projectRoot)
        _fileName= _fileName or ''

        _id= int(_id)

        strStamp= time.strftime("%y/%m/%d %H:%M")

#todo 66 (db) +0: handle unresponsive db task creation
        newId= _id or self.db.newId()

#todo 71 (db) +0: instantly remove blank new task from cache before saving if set to +
        if newId not in self.todoA: #for new and repairing tasks
            self.todoA[newId]= TodoTask(newId, self.projectName, self.projUser, strStamp)

        if _id:
            self.dirty= True
            self.todoA[newId].set(_state, _cat, _lvl, _fileName, _comment, self.projUser, strStamp)

        self.timerFlush.cancel()
        self.timerFlush = Timer(self.flushTimeout, self.flush)
        self.timerFlush.start()

        return newId

    def flush(self, _final=False):
        self.timerFlush.cancel()

        if not self.dirty: return

        if self.db.flush():
            sublime.set_timeout(lambda: sublime.status_message('TypeTodo saved'), 0)
            self.dirty= False
            return
        
        if not _final:
            sublime.set_timeout(lambda: sublime.status_message('TypeTodo error:\n\tcannot flush todo\'s\n\nWill retry in 5 sec\'s'), 0)
            self.timerFlush = Timer(self.flushTimeout, self.flush)
            self.timerFlush.start()
        else:
            sublime.error_message('TypeTodo error:\n\tcannot flush todo\'s')


class TodoTask():
    #static, defined at creation
    id= 0
    project= ''
    creator= ''
    cStamp= '' #used only for dbFile

    #updatable
    state= False
    cat= ''
    lvl= ''
    fileName= ''
    comment= ''
    editor= ''
    stamp= ''

    saved= True

    def __init__(self, _id, _project, _creator, _stamp):
        self.saved= True

        self.id= _id
        self.project= _project
        self.creator= _creator
        self.cStamp= _stamp


    def set(self, _state, _cat, _lvl, _fileName, _comment, _editor, _stamp):
        self.saved= False

        if _state != '': self.state= _state
        self.cat= _cat
        self.lvl= _lvl
        self.fileName= _fileName or ''
        self.comment= _comment
        self.editor= _editor
        self.stamp= _stamp

    def setSaved(self):
        self.saved= True

