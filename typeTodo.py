# coding= utf-8

#todo 1 (interaction) -1: multiline TODO
#todo 8 (interaction) +0: category auto-complete
#todo 9 (interaction) -1: using snippets
#todo 10 (interaction) +0: colorizing
#todo 11 (interaction) -2: make more TODO formats available

#todo 3 (consistency,v2) -10: check at start
#todo 4 (consistency,v2) -10: check as source edited
#todo 5 (consistency,v2) -10: check as db edited (saved)

#=todo 225 (interaction) +0: ask the reason for 'Cancel'

import sublime, sublime_plugin
import sys, re

if sys.version < '3':
    from db import *
    from cache import *
    from c import *
else:
    from .db import *
    from .cache import *
    from .c import *


#todo 65 (code) -1: make class for db cache
#{projectFolder: TodoDb} cache
projectDbCache= {}

def exitHandler(): # one for all, at very exit
    if len(sublime.windows())==0:
        for dbI in projectDbCache:
           projectDbCache[dbI].flush()

def getDB(_view=False, _folder=False):
#todo 74 (db) -1: make better caching of projectDbCache
#    if _view.TTDB: return _view.TTDB
#todo 46 (assure) +0: is .window() a sufficient condition?
    curRoot= ''
    curName= ''

    if _folder!=False:
        firstFolderA=(_folder,)
    elif _view!=False and _view.window():
        firstFolderA= _view.window().folders()
    else:
        return False

    if len(firstFolderA) and (firstFolderA[0] != ''):
        curRoot= firstFolderA[0]
        curName= os.path.split(firstFolderA[0])[1]

    #cache time
    if curRoot not in projectDbCache:
        projectDbCache[curRoot]= TodoDb(curRoot, curName)
    else:
        projectDbCache[curRoot].update(curRoot, curName)

#    _view.TTDB= projectDbCache[curRoot]
    return projectDbCache[curRoot]



class TypetodoEvent(sublime_plugin.EventListener):
    mutexUnlocked= 1

    def on_deactivated(self,_view):
#todo 148 (general) +10: handle fucking unresponsive servers! Especially http
        sublime.set_timeout(exitHandler, 0) #timeout is needed to let sublime.windows() be [] at exit

#todo 86 (issue) +0: db init doesn't run if 2nd sublime window opened with other unconfigured project
    def on_activated(self, _view):
        db=getDB(_view)
        if db:
            sublime.set_timeout(db.reset, 0)

    #maybe lil overheat here, but it works
    def on_selection_modified(self, _view):
        if self.mutexUnlocked:
            self.mutexUnlocked= 0
            _view.run_command('typetodo_subst')
            self.mutexUnlocked= 1

    def on_modified(self, _view):
        if self.mutexUnlocked:
            self.mutexUnlocked= 0
            _view.run_command('typetodo_subst', {'_modified': True})
            self.mutexUnlocked= 1


#todo 210 (general) +0: implement editing of project .do file

class TypetodoSubstCommand(sublime_plugin.TextCommand):
#todo: make cached stuff per-project (or not?)
    lastCat= ['general']
    lastLvl= '+0'

    prevTriggerNew= None
    prevStateMod= None
    prevText= ''

    def run(self, _edit, _modified= False):
        if len(self.view.sel())!=1: #more than one cursors skipped for number of reasons
            return;
            
        todoRegion = self.view.line(self.view.sel()[0])
        todoText = self.view.substr(todoRegion)

        #shortcut
        if todoText == self.prevText:
            return
        self.prevText= todoText

        _mod= RE_TODO_EXISTING.match(todoText) #mod goes first to allow midline todo
        if _mod:
            #should trigger at '+' or '!' entered
            doWipe= _mod.group('state')=='+' and self.prevStateMod!='+'
            if not doWipe: doWipe= _mod.group('state')=='!' and self.prevStateMod!='!'
            self.prevStateMod= _mod.group('state')

            if _modified:
                self.substUpdate(_mod.group('state'), _mod.group('id'), _mod.group('tags'), _mod.group('priority'), _mod.group('comment'), _mod.group('prefix'), _edit, todoRegion, doWipe)

            return

        _new = RE_TODO_NEW.match(todoText)
        if _new:
            #should trigger at ':' entered
            doTrigger= _new.group('trigger')==':' and self.prevTriggerNew!=':'
            self.prevTriggerNew= _new.group('trigger')

            if _modified and doTrigger:
                self.substNew(_new.group('prefix'), _new.group('comment'), _edit, todoRegion)

            return

    #create new todo in db and return string to replace original 'todo:'
    def substNew(self, _prefx, _postfx, _edit, _region):
        todoId= self.cfgStore(0, '', self.lastCat[0], self.lastLvl, self.view.file_name(), '')

        todoComment= _prefx + 'todo ' +str(todoId) +' (' +self.lastCat[0] +') ' +self.lastLvl +': ' +_postfx
        self.view.replace(_edit, _region, todoComment)

        if _postfx != '': #need to save if have comment at creation
            self.substUpdate('', todoId, self.lastCat[0], self.lastLvl, _postfx, _prefx, _edit, _region)

        return todoId

    #store to db and, if changed state, remove comment
    def substUpdate(self, _state, _id, _tags, _lvl, _comment, _prefix, _edit, _region, _wipe=False):
        if _tags != None:
            self.lastCat[0]= _tags

        _id= self.cfgStore(_id, _state, _tags, _lvl or 0, self.view.file_name(), _comment)
        if _wipe:
            if _prefix!='': #dont compress line for mid-todo
                _prefix+= "\n"
            self.view.replace(_edit, self.view.full_line(_region), _prefix)
        return _id

    def cfgStore(self, _id, _state, _tags, _lvl, _fileName, _comment):
        return getDB(self.view).store(_id, _state, (_tags or '').split(','), _lvl, _fileName, _comment)

#todo 21 (general) +0: handle filename change, basically for new unsaved files
