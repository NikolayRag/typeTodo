# coding= utf-8

import sublime, sublime_plugin, webbrowser
import sys, os

if sys.version < '3':
    from db import *
    from cache import *
    from c import *
else:
    from .db import *
    from .cache import *
    from .c import *


class TypetodoRegReplaceCommand(sublime_plugin.TextCommand):
    def run(self, _edit, _regStart= False, _regEnd= False, _replaceWith=''):
        self.view.replace(_edit, sublime.Region(int(_regStart), int(_regEnd)), _replaceWith)


class TypetodoSetStateCommand(sublime_plugin.TextCommand):
    setStateChars= []
    setStateRegion= []

    def setChar(self, _idx):
        if _idx>=0:
            self.view.run_command('typetodo_reg_replace', {'_regStart': self.setStateRegion[0], '_regEnd': self.setStateRegion[1], '_replaceWith': self.setStateChars[_idx]})

    def run(self, _edit):
        todoRegion = self.view.line(self.view.sel()[0])
        _mod= RE_TODO_EXISTING.match(self.view.substr(todoRegion))
        if not _mod:
            sublime.status_message('Nothing Todo here')
            return


        self.setStateChars= []
        menuItems= []

        for state in STATE_LIST: #collect menu list, excluding current state
            if state==_mod.group('state'):
                continue
            self.setStateChars.append(state)
            menuItems.append('\'' +state +'\': ' +str(STATE_LIST[state]))

        self.setStateRegion= (_mod.span('state')[0] +todoRegion.a, _mod.span('state')[1] +todoRegion.a)

        self.view.window().show_quick_panel(menuItems, self.setChar, sublime.MONOSPACE_FONT)


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
        if not sublime.ok_cancel_dialog('TypeTodo WARNING:\n\n\tGlobal .do file will be DELETED\n\tand created back with default settings.\n\n\tIt may contain unsaved database\n\tconnection settings, such as login, pass\n\tor public repository name.\n\n\tGlobal database content\n\twill be copied to new location.\n\n\tProcceed?'):
            return

        if not initGlobalDo(True):
            sublime.message_dialog('TypeTodo error:\n\tCannot reset global .do file,\n\tall remain intact.')
            return

        for iT in cDb.todoA:
            curTodo= cDb.todoA[iT].setSaved(False)
        cDb.dirty= True

        cDb.pushReset(0)


#todo 230 (command) +0: make tool for searching todo's
