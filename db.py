# coding= utf-8

import sys, re, os, time, codecs

if sys.version < '3':
    from dbFile import *
    from dbSql import *
    from dbHttp import *
else:
    from .dbFile import *
    from .dbSql import *
    from .dbHttp import *

#-todo 26 (db) +0: move todo array management to base TodoDb class


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

    cfgA= None

    db= None
    todoA= None

    reCfg= re.compile("^\s*(?:((?P<engine>mysql) (?P<addr>[^\s]+) (?P<login>[^\s]+) (?P<passw>[^\s]+) (?P<scheme>[^\s]+)))\s*$")
#    reCfg= re.compile("^\s*(?:(mysql ([^\s]+) ([^\s]+) ([^\s]+) ([^\s]+))|(http ([^\s]+) ([^\s]+) ([^\s]+)))\s*$")

    def __init__(self, _root, _name):
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

#todo 55 (config) +5: delayed: flush (existing) before reset db[engine]
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
#todo 27 (db) +0: handle delayed update
#todo 29 (db) +0: New tasks Id assigning should NOT be delayed.
#todo 28 (db) +0: make cached access: read task from db as its needed
        self.reset()

        if _fileName and self.projectRoot:
            _fileName= os.path.relpath(_fileName, self.projectRoot)
        _fileName= _fileName or ''

        _id= int(_id)

        strStamp= time.strftime("%y/%m/%d %H:%M")

        if not _id:
#todo 26 (db) +0: handle unresponsive db task creation
            _id= self.db.newId()

        if _id not in self.todoA:
            self.todoA[_id]= TodoTask(_id, self.projectName, self.projUser, strStamp)

        self.todoA[_id].set(_state, _cat, _lvl, _fileName, _comment, self.projUser, strStamp)


        self.db.flush()

        return _id







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

    saved= False


    def __init__(self, _id, _project, _creator, _stamp):
        self.saved= False

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

