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

#todo 30 (doc) +0: config is taken: 1. project.do first string, 2. copy from global .do first string, 3. hardcoded



defaultCfg= {
    'path': '',
    'file': '',
    'db': {'engine': 'file'},
    'header': "# uncomment and configure. LAST matched line matters:\n"\
        +"# mysql 127.0.0.1 username password scheme\n"
}

def plugin_loaded():
    defaultCfg['path']= os.path.join(sublime.packages_path(), 'User')
    defaultCfg['file']= os.path.join(defaultCfg['path'], '.do')
    if not os.path.isfile(defaultCfg['file']):
        with codecs.open(defaultCfg['file'], 'w+', 'UTF-8') as f:
            f.write(defaultCfg['header'])

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

#todo 75 (general) +0: make longer flush delay when having on_exit analog
    flushTimeout= 2 #seconds
    timerFlush= None
    dirty= False

    db= None
    todoA= None

    reCfg= re.compile("^\s*(?:((?P<engine>mysql) (?P<addr>[^\s]+) (?P<login>[^\s]+) (?P<passw>[^\s]+) (?P<scheme>[^\s]+)))\s*$")
#    reCfg= re.compile("^\s*(?:(mysql ([^\s]+) ([^\s]+) ([^\s]+) ([^\s]+))|(http ([^\s]+) ([^\s]+) ([^\s]+)))\s*$")

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

        cfgFound= defaultCfg['db']
        cfgHeaderStrings= defaultCfg['header']

        cfgFoundA= [cfgFound]
        try:
            cfgHeaderStrings= self.readCfg(cfgPath, cfgFoundA)
            cfgFound= cfgFoundA[0]
        except:
            #try load default .do config; and create if none
            try:
                cfgHeaderStrings= self.readCfg(defaultCfg['file'], cfgFoundA)
                cfgFound= cfgFoundA[0]

            except: #create default .do config
                with codecs.open(defaultCfg['file'], 'w+', 'UTF-8') as f:
                  f.write(cfgHeaderStrings)


            if cfgFound['engine'] != 'file': #save new blank cfg
                with codecs.open(cfgPath, 'w+', 'UTF-8') as f:
                  f.write(cfgHeaderStrings)


        if cfgFound == self.cfgA:
            return

        self.flush(True)

        self.cfgA= cfgFound
        self.todoA= {}

        if cfgFound['engine']== 'mysql':
            self.db= TodoDbSql(self.todoA, self.projUser, self.projectName, cfgFound['addr'], cfgFound['login'], cfgFound['passw'], cfgFound['scheme'])
#        elif cfgFound['engine']== 'http':
#            return
        else:
            self.db= TodoDbFile(self.todoA, self.projUser, self.projectName, cfgPath, cfgHeaderStrings) #throw in sfgString to restore it in file



    def readCfg(self, _cfgPath, _cfgFound):
        cfgHeaderStrings= ''

        with codecs.open(_cfgPath, 'r', 'UTF-8') as f:
            while True:
                l= f.readline().splitlines()
                if l == []: break
                cfgString= l[0]
                if cfgString == '' or not cfgString:
                    break

                cfgHeaderStrings+= cfgString +"\n"
                #catch last matched config
                cfgFoundTry= self.reCfg.match(cfgString)
                if cfgFoundTry:
                    _cfgFound[0]= cfgFoundTry.groupdict()

            return cfgHeaderStrings

    def store(self, _id, _state, _cat, _lvl, _fileName, _comment):
#todo 28 (db) +0: make cached access: read task from db as its needed
        self.reset()

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

