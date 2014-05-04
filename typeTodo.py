# coding= utf-8

#todo 2 (interaction) -1: midline TODO
#todo 1 (interaction) -1: multiline TODO
#todo 8 (interaction) +0: category auto-complete
#todo 9 (interaction) -1: using snippets
#todo 10 (interaction) +0: colorizing
#todo 11 (interaction) -2: make more TODO formats available
#todo 33 (interaction) -10: remove blank TODO from base if set to +
#todo 50 (interaction) +0: make category into tag list

#todo 3 (consistency) +0: check at start
#todo 4 (consistency) +0: check as source edited
#todo 5 (consistency) +0: check as db edited (saved)

#todo 13 (interaction) +0: make 'done' state be dedicated '', '-', '!', 'x' add probably others

#todo 12 (doc) +0: removing TODO from code - dont remove it from db

#todo 60 (issue) +10: task set to '+' and wiped out flushes undo stack


import sublime, sublime_plugin
import re, os, time, codecs

from db import *

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
    lastCat= 'general'
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
        return self.getDB(_view).store(_id, _state, _cat, _lvl, _fileName, _comment)


#todo 21 (general) +0: handle filename change, basically for new unsaved files

    def getDB(self, _view):
        curRoot= os.path.join(sublime.packages_path(),self.packageName)
        curName= ''

        firstFolderA= _view.window().folders()

        if len(firstFolderA) and (firstFolderA[0] != ''):
            curRoot= firstFolderA[0]
            curName= os.path.split(firstFolderA[0])[1]

        #cache time
        if curRoot not in self.projectDbCache:
            self.projectDbCache[curRoot]= TodoDb(curRoot, curName)
        else:
            self.projectDbCache[curRoot].update(curRoot, curName)

        return self.projectDbCache[curRoot]




    def on_load(self, _view):
#todo 46 (assure) +0: is .window() a sufficient condition?
        if _view.window():
            self.getDB(_view)


