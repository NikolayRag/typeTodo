#todo 2 (interaction) -1: midline TODO
#todo 1 (interaction) -1: multiline TODO
#todo 8 (interaction) +0: category auto-complete
#todo 9 (interaction) -1: using snippets
#todo 10 (interaction) +0: colorizing
#todo 11 (interaction) -2: make more TODO formats available

#todo 3 (consistency) +0: check at start
#todo 4 (consistency) +0: check as source edited
#todo 5 (consistency) +0: check as db edited (saved)

#todo 13 (interaction) +0: make 'done' state be dedicated '', '-', '!', 'x' add probably others

#todo 12 (doc) +0: removing TODO from code - dont remove it from db


import sublime, sublime_plugin
import re, os, time

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
    reRootFolderFile= re.compile('(.*)\.sublime-project$')

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
        todoId= self.cfgStore(0, False, self.lastCat, self.lastLvl, _view.file_name(), '')

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
        _id= self.cfgStore(_id, _state, _cat, _lvl or 0, _view.file_name(), _comment)

        return _id


    def strReplace(self, _view, _region, _comment):
        self.undoMutexFree= 0
        edit= _view.begin_edit()
        _view.replace(edit, _region, _comment)
        _view.end_edit(edit)
        self.undoMutexFree= 1


    def cfgStore(self, _id, _state, _cat, _lvl, _fileName, _comment):
        projectPair= self.fileFindUpstream(os.path.dirname(_fileName), self.reRootFolderFile)
        for cfgRoot, projectName in [projectPair]:
            break
        if projectName != '':
            _fileName= os.path.relpath(_fileName, cfgRoot)

        if cfgRoot not in self.projectDbCache:
            self.projectDbCache[cfgRoot]= TodoDb(cfgRoot, projectName)

        return self.projectDbCache[cfgRoot].store(_id, _state, _cat, _lvl, _fileName, _comment)


#todo 19 (general) +10: no project returned for new unsaved sourcefile

#   return [folder, fileName] for file
#   where folder is first upstream folder with _reFileMask file
#   and projectName is .group(1) content of that file
    def fileFindUpstream(self, _folderCheck, _reFileMask):
#todo: make cache and check it first
        while True:
            for folderTest in os.listdir(_folderCheck):
                fileTest= _reFileMask.match(folderTest)
                if fileTest and fileTest.group(1):
                    return [_folderCheck, fileTest.group(1)]

            folderUp= os.path.split(_folderCheck)[0]
            if folderUp == _folderCheck:
                break
            _folderCheck= folderUp
        #defaults if not found *.sublime-project
        return [os.path.join(sublime.packages_path(),self.packageName), '']










#   Project-assigned set
#   Read config and set up db engine

class TodoDb():
    db= None

    def __init__(self, _root, _name):

        cfgPath= os.path.join(_root, _name +'.todo')
        with open(cfgPath, 'r') as f:
            f.readline() #db config be here
            f.readline()

#todo 15 (db) +0: read db settings and use proper db engine
        uname= '*Anon'
        if 'USERNAME' in os.environ: uname= os.environ['USERNAME']

        self.db= TodoDbFile(uname, _name, cfgPath)


    def store(self, _id, _state, _cat, _lvl, _fileName, _comment):
        return self.db.store(_id, _state, _cat, _lvl, _fileName, _comment)



