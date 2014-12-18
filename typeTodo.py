# coding= utf-8

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


import sublime, sublime_plugin, webbrowser
import sys, re, os, time, codecs

if sys.version < '3':
    from db import *
else:
    from .db import *



#todo 65 (code) -1: make class for db cache
#{projectFolder: TodoDb} cache
projectDbCache= {}

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


class TypetodoWwwCommand(sublime_plugin.TextCommand):
    def run(self, _edit):
        cDb= getDB(self.view)
        cCfg= cDb.cfgA
        if cCfg['engine']!='http' or cCfg['addr']=='' or cCfg['base']=='':
            sublime.error_message('TypeTodo:\n\n\tProject is not configured for HTTP')
            return
        webbrowser.open_new_tab('http://' +cCfg['addr'] +'/' +cCfg['base'] +'/' +cDb.projectName)



class TypetodoCfgOpenCommand(sublime_plugin.TextCommand):
    def run(self, _edit):
        cDb= getDB(self.view)
        fn= os.path.join(cDb.projectRoot, cDb.projectName +'.do')
        if not os.path.isfile(fn):
            sublime.message_dialog('TypeTodo:\n\tNo projects .do file,\n\tplease restart Sublime')
            return
        sublime.active_window().open_file(fn, sublime.TRANSIENT)


class TypetodoGlobalOpenCommand(sublime_plugin.TextCommand):
    def run(self, _edit):
        cDb= getDB(False,'')
        fn= os.path.join(cDb.projectRoot, cDb.projectName +'.do')
        if not os.path.isfile(fn):
            sublime.message_dialog('TypeTodo:\n\tNo global .do file,\n\tplease restart Sublime')
            return
        sublime.active_window().open_file(fn, sublime.TRANSIENT)

class TypetodoGlobalResetCommand(sublime_plugin.TextCommand):
    def run(self, _edit):
        cDb= getDB(False,'')
        if not sublime.ok_cancel_dialog('TypeTodo WARNING:\n\n\tGlobal .do file will be DELETED\n\tand created back with default settings\n\n\tIt may contain unsaved database\n\tconnection settings, such as login, pass\n\tor public repository name.\n\n\tGlobal database content\n\twill be copied to new location.\n\n\tProcceed anyway?'):
            return

        cDb.flush(True)
        if not cDb.fetch() or not initGlobalDo(True):
            sublime.message_dialog('TypeTodo error:\n\tCannot reset global .do file,\n\tall remain intact.')
            return

        cDb.reset()
        for iT in cDb.todoA:
            curTodo= cDb.todoA[iT].setSaved(False)
        cDb.dirty= True
        cDb.flush(True)



class TypetodoEvent(sublime_plugin.EventListener):
    mutexUnlocked= 1

    def on_deactivated(self,_view):
#todo 148 (general) +10: handle fucking unresponsive servers! Especially http
        getDB(_view).flush(True)

#todo 86 (issue) +0: db init doesn't run if 2nd sublime window opened with other unconfigured project
    def on_activated(self, _view):
        getDB(_view)

    #maybe lil overheat here, but it works
    def on_selection_modified(self, _view):
        if self.mutexUnlocked:
            self.mutexUnlocked= 0
            if len(_view.sel())==1: #more than one cursors skipped for number of reasons
                _view.run_command('typetodo_subst')
            self.mutexUnlocked= 1

    def on_modified(self, _view):
        if self.mutexUnlocked:
            self.mutexUnlocked= 0
            if len(_view.sel())==1: #more than one cursors skipped for number of reasons
                _view.run_command('typetodo_subst', {'_modified': True})
            self.mutexUnlocked= 1


class TypetodoSubstCommand(sublime_plugin.TextCommand):
#todo: make cached stuff per-project (or not?)
    lastCat= ['general']
    lastLvl= '+0'

    stateList= {
        '+': True,
        '-': False,
        None: False
    }

    prevMatchNew= None
#todo 2 (interaction) -1: midline TODO
    reTodoNew= re.compile('^(\s*(?://|#)\s*)todo(:)?$')

    prevMatchMod= None
    reTodoExisting= re.compile('^(?:\s*(?://|#)\s*)([\+\-])?todo\s+(\d+)(?:\s+\((.*)\))?(?:\s+([\+\-]\d+))?\s*:\s*(.*)\s*$')

    prevText= ''

    def run(self, _edit, _modified= False):
        todoRegion = self.view.line(self.view.sel()[0])
        todoText = self.view.substr(todoRegion)

        #shortcut
        if todoText == self.prevText:
            return
        self.prevText= todoText

        _new = self.reTodoNew.match(todoText)
        if _new:
            #should trigger if ':' entered but was not here
            if _modified and (_new.group(2) and self.prevMatchNew):
                self.substNew(_new.group(1), _edit, todoRegion)

            self.prevMatchNew= _new.group(2)==None
            return

        _mod= self.reTodoExisting.match(todoText)
        if _mod:
            state= self.stateList[_mod.group(1)]
            #should trigger if '+' is either absent or was not here;
            if _modified and (not state or self.prevMatchMod):
                self.substUpdate(state, _mod.group(2), _mod.group(3), _mod.group(4), _mod.group(5), _edit, todoRegion)

            self.prevMatchMod= state==False
            return
 
    #create new todo in db and return string to replace original 'todo:'
    def substNew(self, _pfx, _edit, _region):
        todoId= self.cfgStore(0, False, self.lastCat[0], self.lastLvl, self.view.file_name(), '')

        todoComment= _pfx + 'todo ' +str(todoId) +' (' +self.lastCat[0] +') ' +self.lastLvl +': '
        self.view.replace(_edit, _region, todoComment)

        return todoId


    #store to db and, if changed state, remove comment
    def substUpdate(self, _state, _id, _cat, _lvl, _comment, _edit, _region):
        if _cat != None:
            self.lastCat[0]= _cat

        _id= self.cfgStore(_id, _state, _cat, _lvl or 0, self.view.file_name(), _comment)
        if _state:
            self.view.replace(_edit, self.view.full_line(_region), '')
        return _id

    def cfgStore(self, _id, _state, _cat, _lvl, _fileName, _comment):
        return getDB(self.view).store(_id, _state, _cat, _lvl, _fileName, _comment)

#todo 21 (general) +0: handle filename change, basically for new unsaved files
