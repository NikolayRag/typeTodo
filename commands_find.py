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


class TypetodoJumpPointCommand(sublime_plugin.TextCommand):
    def run(self, _edit, _line, _col):
        focusBegin= self.view.text_point(_line, _col)
        focusLine= sublime.Region(focusBegin, self.view.line(focusBegin).b)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(focusBegin, focusBegin))
        self.view.show(focusLine)

class TypetodoJumpCommand(sublime_plugin.TextCommand):

    def focusTodo(self, _view, _line, _col):
        sublime.active_window().focus_view(_view)
        sublime.set_timeout(lambda: _view.run_command('typetodo_jump_point', {'_line': _line, '_col': _col}), 100)


#todo 341 (command) +0: jump: deal with multiple matches
    def findTodoInViews(self, _id):
        for cView in sublime.active_window().views():
            lNum= 0
            for cLine in cView.lines(sublime.Region(0,cView.size())):
                lNum+= 1
                foundIncode= RE_TODO_EXISTING.match(cView.substr(cLine))
                if foundIncode and foundIncode.group('id')==_id:
                    self.focusTodo(cView, lNum-1, foundIncode.end('prefix'))

                    return True

        return False


    def findTodoInFile(self, _fn, _test, _id):
        foundEntry= None
        lNum= 0
        try:
            with codecs.open(_fn, 'r', 'UTF-8') as f:
                success= False
                for ln in f:
                    lNum+= 1
                    foundEntry= _test.match(ln)
                    if foundEntry and foundEntry.group('id')==_id:
                        success= True
                        break

            if not success:
                return False

        except Exception as e:
            return False

        cView= sublime.active_window().open_file(_fn, sublime.TRANSIENT)
        self.focusTodo(cView, lNum-1, foundEntry.end('prefix'))

        return True



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
