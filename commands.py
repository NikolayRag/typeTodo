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


##+service commands


#Replace view region.
#Command is used to keep python flow unruined
#
class TypetodoRegReplaceCommand(sublime_plugin.TextCommand):
    def run(self, _edit, _regStart= False, _regEnd= False, _replaceWith=''):
        self.view.set_read_only(False) #will reset instantly
        self.view.replace(_edit, sublime.Region(int(_regStart), int(_regEnd)), _replaceWith)
 


#Focus view, place and show cursor
#
class TypetodoJumpViewCommand(sublime_plugin.TextCommand):
    def showLinecol(self, _line, _col):
        focusBegin= self.view.text_point(_line, _col)
        focusLine= sublime.Region(focusBegin, self.view.line(focusBegin).b)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(focusBegin, focusBegin))
        self.view.show(focusLine)

    def run(self, _edit, _line=-1, _col=0):
        sublime.active_window().focus_view(self.view)
        if _line!=-1:
            sublime.set_timeout(lambda: self.showLinecol(_line,_col), 100)

##-service commands


class TypetodoSetCommand(sublime_plugin.TextCommand):
    stateChars= []
    stateRegion= []


    def setState(self, _idx):
        if _idx>=0:
            self.view.run_command('typetodo_reg_replace', {'_regStart': self.stateRegion[0], '_regEnd': self.stateRegion[1], '_replaceWith': self.stateChars[_idx]})


    def run(self, _edit, _state=False, _priority=False):
        #prevented while in 'Search todo' results
        foundView= WCache().getResultsView(False)
        if foundView and foundView.buffer_id()==self.view.buffer_id():
            return

        todoRegion = self.view.line(self.view.sel()[0])
        matchRegexp= RE_TODO_EXISTING.match(self.view.substr(todoRegion))
        if not matchRegexp:
            sublime.status_message('Nothing Todo here')
            return

        self.stateRegion= (matchRegexp.span('state')[0] +todoRegion.a, matchRegexp.span('state')[1] +todoRegion.a)


        #explicit state
        if _state!=False:
            self.stateChars= [_state]
            self.setState(0)
            return


        #explicit priority
        if _priority!=False:
            return


        #display to chose state
        self.stateChars= []
        menuItems= []

        for state in STATE_LIST: #collect menu list
            if state:
                self.stateChars.append(state[0])
                menuItems.append((4-len(state[0]))*' ' +state[0] +'   : ' +state[1])


        self.view.window().show_quick_panel(menuItems, self.setState, sublime.MONOSPACE_FONT)




class TypetodoWwwCommand(sublime_plugin.TextCommand):
    def run(self, _edit):
        cDb= WCache().getDB()
        for cCfg in cDb.config.settings:
            if cCfg.engine=='http' and cCfg.addr!='' and cCfg.base!='':
                webbrowser.open_new_tab('http://' +cCfg.addr +'/' +cCfg.base +'/' +cDb.config.projectName)
                return
        sublime.error_message('TypeTodo:\n\n\tProject is not configured for HTTP')



class TypetodoCfgOpenCommand(sublime_plugin.TextCommand):
    def run(self, _edit):
        fn= WCache().getDB().config.settings[0].file
        if not os.path.isfile(fn):
            sublime.message_dialog('TypeTodo:\n\n\tNo projects .do file,\n\tplease restart Sublime')
            return
        sublime.active_window().open_file(fn, sublime.TRANSIENT)



class TypetodoGlobalOpenCommand(sublime_plugin.TextCommand):
    def run(self, _edit):
        fn= Config().settings[0].file
        if not os.path.isfile(fn):
            sublime.message_dialog('TypeTodo:\n\n\tNo global .do file,\n\tplease restart Sublime')
            return
        sublime.active_window().open_file(fn, sublime.TRANSIENT)



class TypetodoGlobalResetCommand(sublime_plugin.TextCommand):
    cDb= None

    def resetCB(self):
        if not self.cDb:
            return
        cDb= self.cDb
        self.cDb= None

        if not cDb.config.globalInited and not cDb.config.initGlobalDo(True):
            sublime.message_dialog('TypeTodo error:\n\n\tCannot reset global .do file,\n\tall remain intact.')
            return

        for iT in cDb.todoA:
            cDb.todoA[iT].setSaved(SAVE_STATES.FORCE)

        cDb.pushReset(0)


    def run(self, _edit):
        if not sublime.ok_cancel_dialog('TypeTodo WARNING:\n\n\tGlobal .do file will be DELETED\n\tand created back with default settings.\n\n\tIt may contain unsaved database\n\tconnection settings, such as login, pass\n\tor public repository name.\n\n\tGlobal database content\n\twill be copied to new location.\n\n\tProcceed?'):
            return

        self.cDb= TodoDb(self.resetCB, Config())

