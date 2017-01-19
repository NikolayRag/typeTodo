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


#Replace view region content.
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



#Change todo priority
#
class TypetodoPriorityCommand(sublime_plugin.TextCommand):
    def run(self, _edit, _delta):
        todoRegion = self.view.line(self.view.sel()[0])
        matchRegexp= RE_TODO_EXISTING.match(self.view.substr(todoRegion))
        if not matchRegexp:
            sublime.status_message('Nothing Todo here')
            return

        newPriority= int(matchRegexp.group('priority')) +_delta
        if newPriority>=0:
            newPriority= '+' +str(newPriority)
        newPriority= str(newPriority)
        
        self.view.run_command('typetodo_reg_replace', {
            '_regStart': todoRegion.a+matchRegexp.start('priority'),
            '_regEnd': todoRegion.a+matchRegexp.end('priority'),
            '_replaceWith': newPriority
        })



#Set todo state by supplying it or by calling menu
#
class TypetodoSetCommand(sublime_plugin.TextCommand):
    stateChars= []
    stateRegion= []


    def setState(self, _idx):
        if _idx>=0:
            self.view.run_command('typetodo_reg_replace', {'_regStart': self.stateRegion[0], '_regEnd': self.stateRegion[1], '_replaceWith': self.stateChars[_idx]})


    def run(self, _edit, _state=False):
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


        #display to chose state
        self.stateChars= []
        menuItems= []

        for state in STATE_LIST: #collect menu list
            if state:
                self.stateChars.append(state[0])
                menuItems.append((4-len(state[0]))*' ' +state[0] +'   : ' +state[1])


        self.view.window().show_quick_panel(menuItems, self.setState, sublime.MONOSPACE_FONT)




#open HTTP repository in browser
#
class TypetodoWwwCommand(sublime_plugin.TextCommand):
    def run(self, _edit):
        cDb= WCache().getDB()
        for cCfg in cDb.config.settings:
            if (cCfg.engine=='http' or cCfg.engine=='https') and cCfg.addr!='' and cCfg.base!='':
                webbrowser.open_new_tab(cCfg.engine +'://' +cCfg.addr +'/' +cCfg.base +'/' +cDb.config.projectName)
                return
        sublime.error_message('TypeTodo:\n\n\tProject is not configured for HTTP')



#Open project's .do
#
class TypetodoCfgOpenCommand(sublime_plugin.TextCommand):
    def run(self, _edit):
        fn= WCache().getDB().config.settings[0].file
        if not os.path.isfile(fn):
            sublime.message_dialog('TypeTodo:\n\n\tNo projects .do file,\n\tplease restart Sublime')
            return
        sublime.active_window().open_file(fn, sublime.TRANSIENT)



#Open global .do
#
class TypetodoGlobalOpenCommand(sublime_plugin.TextCommand):
    def run(self, _edit):
        fn= Config().settings[0].file
        if not os.path.isfile(fn):
            sublime.message_dialog('TypeTodo:\n\n\tNo global .do file,\n\tplease restart Sublime')
            return
        sublime.active_window().open_file(fn, sublime.TRANSIENT)


