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


class TypetodoJumpCommand(sublime_plugin.TextCommand):
#    newWFlags= sublime.ENCODED_POSITION|sublime.TRANSIENT
#    if sys.version < '3': # ST2 hangs if both flags set
    newWFlags= sublime.ENCODED_POSITION


#todo 348 (command) +0: fix focusing on file open
    def focusTodo(self, _view, _begin, _end):
        _view.sel().clear()
        _view.sel().add(sublime.Region(_begin, _begin))
        _view.show(sublime.Region(_begin, _end))
        sublime.set_timeout(lambda: sublime.active_window().focus_view(_view), 0)

#todo 341 (command) +0: jump: deal with multiple matches
    def findTodoInViews(self, _id):
        for cView in sublime.active_window().views():
            for cLine in cView.lines(sublime.Region(0,cView.size())):
                foundIncode= RE_TODO_EXISTING.match(cView.substr(cLine))
                if foundIncode and foundIncode.group('id')==_id:
                    foundPos= cLine.a +foundIncode.start('id')
                    self.focusTodo(cView, foundPos, cLine.b)

                    return True

        return False


    def findTodoInFile(self, _fn, _test, _id):
        try:
            with codecs.open(_fn, 'r', 'UTF-8') as f:
                lNum= 0
                for ln in f:
                    lNum+= 1
                    foundEntry= _test.match(ln)
                    if foundEntry and foundEntry.group('id')==_id:
                        cView= sublime.active_window().open_file(_fn+':'+str(lNum)+':'+str(foundEntry.start('id')), self.newWFlags)

                        #this duplication should stay alone, but it doesnt work itself without timeout
                        sublime.set_timeout(lambda: self.focusTodo(cView, cView.text_point(lNum-1, foundEntry.start('id')), cView.text_point(lNum, 0) -5), 100)

                        return True
        except:
            None

        return False


    def findTodoInProject(self, _id):
        for cFolder in sublime.active_window().folders():
            for cWalk in os.walk(cFolder):
                for cFile in cWalk[2]:
                    fn= os.path.join(cWalk[0], cFile)
                    if self.findTodoInFile(fn, RE_TODO_EXISTING, _id):
                        return True

        return False


    def findNamed(self, _text):
        if _text=='':
            return

        if self.findTodoInViews(_text):
            return
        
        if len(sublime.active_window().folders())>0:
            if self.findTodoInProject(_text):
                return

        sublime.message_dialog('TypeTodo error:\n\tDoplet #' +_text +' was not found in source')


    def run(self, _edit):
        todoRegion = self.view.line(self.view.sel()[0])

        #jump to .do file
        todoIncode= RE_TODO_EXISTING.match(self.view.substr(todoRegion))
        if todoIncode:
            cDb= getDB(self.view)
            fn= os.path.join(cDb.projectRoot, cDb.projectName +'.do')
            if not os.path.isfile(fn):
                sublime.message_dialog('TypeTodo error:\n\tCannot find projects .do file')
                return

            if not self.findTodoInFile(fn, RE_TODO_STORED, todoIncode.group('id')):
                sublime.message_dialog('TypeTodo error:\n\tDoplet #' +todoIncode.group('id') +' not found in project\'s .do')

            return


        #jump to code
        todoIndo= RE_TODO_STORED.match(self.view.substr(todoRegion))
        if todoIndo:
            if self.findTodoInViews(todoIndo.group('id')):
                return
            
            if len(sublime.active_window().folders())>0:
                if self.findTodoInProject(todoIndo.group('id')):
                    return

            sublime.message_dialog('TypeTodo error:\n\tDoplet #' +todoIndo.group('id') +' was not found in source')
            return

        #search by string
        sublime.active_window().show_input_panel('TypeTodo search for:', '', self.findNamed, None, self.findNamed)



#command is used to keep python flow unruined
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

        currentState= _mod.group('state')
        defaultState= ''
        if currentState=='':
            defaultState= '='
        elif currentState=='=':
            defaultState= '+'

        self.setStateChars.append(defaultState)
        menuItems.append('\'' +defaultState +'\': ' +str(STATE_LIST[defaultState]))

        for state in STATE_LIST: #collect menu list, excluding current and default state
            if state==currentState or state==defaultState:
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
            curTodo= cDb.todoA[iT].setSaved(SAVE_STATES.READY)
        cDb.dirty= True

        cDb.pushReset(0)


