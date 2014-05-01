# coding= utf-8

#todo 2 (interaction) -1: midline TODO
#todo 1 (interaction) -1: multiline TODO
#todo 8 (interaction) +0: category auto-complete
#todo 9 (interaction) -1: using snippets
#todo 10 (interaction) +0: colorizing
#todo 11 (interaction) -2: make more TODO formats available
#todo 33 (interaction) -10: remove blank TODO from base if set to +

#todo 3 (consistency) +0: check at start
#todo 4 (consistency) +0: check as source edited
#todo 5 (consistency) +0: check as db edited (saved)

#todo 13 (interaction) +0: make 'done' state be dedicated '', '-', '!', 'x' add probably others

#todo 12 (doc) +0: removing TODO from code - dont remove it from db


import sublime, sublime_plugin
import re, os, time, codecs

from dbFile import *
from dbSql import *
from dbHttp import *

class TodoCommand(sublime_plugin.EventListener):
    packageName= 'typeTodo'

    #{projectFolder: TodoDb} cache
    projectDbCache= {}

    undoMutexFree= 1
    prevTxt= ''
#todo: remove '$' for new so #todo can be placed before existing text
    reTodoNew= re.compile('^\s*((?://|#)\s*)todo:$')
    reTodoExisting= re.compile('^(?:(?://|#)\s*)([\+\-])?todo\s+(\d+)(?:\s+\((.*)\))?(?:\s+([\+\-]\d+))?\s*:\s*(.*)\s*$')

#todo: make cached stuff per-project (or not?)
    lastCat= 'blank'
    lastLvl= '+0'

    def on_modified(self, _view):
        #more than one cursors skipped for number of reasons
        if (len(_view.sel())!=1) or (not self.undoMutexFree):
            return

        todoRegion = _view.line(_view.sel()[0])
        todoText = _view.substr(todoRegion)
#todo: need to get 'previous' string state without caching to avoid bugs when typing part of 'todo:' while changing cursor position
#in general - make triggering more clear
#use command_history()? Its also dont fit perfect
        prevCheck= self.prevTxt
        self.prevTxt= todoText

        _new = self.reTodoNew.match(todoText)
        #get the moment ':' is added to avoid triggering on undo/redo/paste
        if _new and (todoText==prevCheck+':'):
            resNew= self.substNew(_new.group(1), _view, todoRegion)
            if not resNew:
                sublime.status_message('Todo creation failed')
            return

        _mod= self.reTodoExisting.match(todoText)
        if _mod :
            resUpdate= self.substUpdate(_mod.group(1), _mod.group(2), _mod.group(3), _mod.group(4), _mod.group(5), _view, todoRegion)
            if not resUpdate:
                sublime.status_message('Todo update failed')
            return

    #create new todo in db and return string to replace original 'todo:'
    def substNew(self, _pfx, _view, _region):
        todoId= self.cfgStore(_view, 0, False, self.lastCat, self.lastLvl, _view.file_name(), '')

        todoComment= _pfx + 'todo ' +str(todoId) +' (' +self.lastCat +') ' +self.lastLvl +': '
        self.strReplace(_view, _region, todoComment)

        return todoId


    #store to db and, if changed state, remove comment
    def substUpdate(self, _state, _id, _cat, _lvl, _comment, _view, _region):
        if _cat != None:
            self.lastCat= _cat
        if _lvl != None:
            self.lastLvl= _lvl

        _state= _state=='+'
        if _state:
            self.strReplace(_view, _view.full_line(_region), '')
        _id= self.cfgStore(_view, _id, _state, _cat, _lvl or 0, _view.file_name(), _comment)

        return _id


    def strReplace(self, _view, _region, _comment):
        self.undoMutexFree= 0
        edit= _view.begin_edit()
        _view.replace(edit, _region, _comment)
        _view.end_edit(edit)
        self.undoMutexFree= 1


    def cfgStore(self, _view, _id, _state, _cat, _lvl, _fileName, _comment):
        projectPair= self.getProject(_view)

        for cfgRoot, projectName in [projectPair]:
            break
        if projectName != '':
            if _fileName:
                _fileName= os.path.relpath(_fileName, cfgRoot)
            else:
                _fileName= ''

        if cfgRoot not in self.projectDbCache:
            self.projectDbCache[cfgRoot]= TodoDb(cfgRoot, projectName)

        return self.projectDbCache[cfgRoot].store(_id, _state, _cat, _lvl, _fileName, _comment)


#todo 21 (general) +0: handle filename change, basically for new unsaved file

#   return [folder, projectName] where
#       folder is full path used for project first
#       projectName name ot that folder itself
    def getProject(self, _view):
        firstFolderA= _view.window().folders()
        if len(firstFolderA) and (firstFolderA[0] != ''):
            return [firstFolderA[0], os.path.split(firstFolderA[0])[1]]

        return [os.path.join(sublime.packages_path(),self.packageName), '']









#-todo 26 (db) +0: move todo array management to base TodoDb class
#todo 27 (db) +0: handle delayed update
#todo 29 (db) +0: New tasks Id assigning should NOT be delayed. Or yes? 
#todo 28 (db) +0: make cached access: read task from db as its needed

#   Project-assigned task set
#   Read config and set up db engine

class TodoDb():
    db= None
    todoA= None

    reCfg= re.compile("^\s*(?:(mysql ([^\s]+) ([^\s]+) ([^\s]+) ([^\s]+)))\s*$")
#    reCfg= re.compile("^\s*(?:(mysql ([^\s]+) ([^\s]+) ([^\s]+) ([^\s]+))|(http ([^\s]+) ([^\s]+) ([^\s]+)))\s*$")

    def __init__(self, _root, _name):
        self.todoA= {}

        uname= '*Anon'
        if 'USERNAME' in os.environ: uname= os.environ['USERNAME']

        cfgPath= os.path.join(_root, _name +'.todo')

#todo 38 (config) +0: reread if changed
        cfgFound= None
        cfgHeaderStrings= ''

        try:
            with codecs.open(cfgPath, 'r', 'UTF-8') as f:
                while True:
                    cfgString= f.readline().splitlines()[0] #db config be here
                    if cfgString == '' or not cfgString:
                        break

                    cfgHeaderStrings+= cfgString +"\n"
                    #catch last matched config
                    cfgFoundTry= self.reCfg.match(cfgString)
                    if cfgFoundTry:
                        cfgFound= cfgFoundTry

        except:
            with codecs.open(cfgPath, 'w+', 'UTF-8') as f:
                f.write('')

            cfgHeaderStrings= "# uncomment and configure:\n"\
              +"# mysql 127.0.0.1 username password scheme\n"

#todo 30 (doc) +0: config is taken: 1. project.todo first string, (2. global .todo first string), (3. env variables), (4. hardcoded)
#todo 31 (doc) +0: config string format: 1. '' - full, 2. 'mysql [host] [log] [pas] [scheme] [table]', (3. 'http [host] [repId] [pass]'), (4. 'breef; ...' for duplication)


        if cfgFound and cfgFound.group(1):
            dbAddr= cfgFound.group(2)
            dbUname= cfgFound.group(3)
            dbPass= cfgFound.group(4)
            dbScheme= cfgFound.group(5)

            self.db= TodoDbSql(self.todoA, uname, _name, dbAddr, dbUname, dbPass, dbScheme)

#        elif cfgFound and cfgFound.group(6):

        else:
            self.db= TodoDbFile(self.todoA, uname, _name, cfgPath, cfgHeaderStrings) #throw in sfgString to restore it in file


    def store(self, _id, _state, _cat, _lvl, _fileName, _comment):
        return self.db.store(_id, _state, _cat, _lvl, _fileName, _comment)



