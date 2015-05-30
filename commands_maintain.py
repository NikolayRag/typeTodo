# coding= utf-8

import sublime, sublime_plugin
import sys, os

if sys.version < '3':
    from db import *
    from cache import *
    from c import *
else:
    from .db import *
    from .cache import *
    from .c import *


class TypetodoMaintainCommand(sublime_plugin.TextCommand):
    if sys.version < '3':
        codeColor= sublime.DRAW_OUTLINED
    else:
        codeColor= sublime.DRAW_NO_OUTLINE |sublime.DRAW_NO_FILL |sublime.DRAW_SOLID_UNDERLINE


    def run(self, _edit, _delayed=True, _regionStart= False, _regionEnd= False):
        if sublime.load_settings('typetodo.sublime-settings').get('typetodo_nocolorize'):
            self.view.erase_regions('dopletOpenPre')
            self.view.erase_regions('dopletOpen')

            self.view.erase_regions('dopletProgressPre')
            self.view.erase_regions('dopletProgress')

            self.view.erase_regions('dopletInconsistentPre')
            self.view.erase_regions('dopletInconsistent')

        else:
            self.colorize(_edit, _delayed, _regionStart, _regionEnd)




    def colorize(self, _edit, _delayed=True, _regionStart= False, _regionEnd= False):
#todo 492 (command, cleanup) -5: should use specified region to speedup at editing
#        if _regionStart and _regionEnd:
#            _region= sublime.Region(_regionStart, _regionEnd)
#        else:
        _region= sublime.Region(0,self.view.size())
        content= self.view.substr(_region)

        todos= []
        regionsOpenPre= []
        regionsOpen= []
        regionsProgressPre= []
        regionsProgress= []
        regionsInconsistentPre= []
        regionsInconsistent= []

        for cTodo in RE_TODO_OLD.finditer(content):
            regionTodo= sublime.Region(cTodo.end('prefix'), cTodo.end('comment'))
            regionsInconsistent.append(regionTodo)

        for cTodo in RE_TODO_EXISTING.finditer(content):
            regionMark= sublime.Region(cTodo.end('prefix'), cTodo.start('state'))
            regionTodo= sublime.Region(cTodo.start('state'), cTodo.end('comment'))

            if not self.todoValidate(cTodo.group('id'), cTodo.group('state'), cTodo.group('tags'), cTodo.group('priority'), cTodo.group('comment')):
                regionsInconsistentPre.append(regionMark)
                regionsInconsistent.append(regionTodo)
                continue

            if cTodo.group('state')=='=':
                regionsProgressPre.append(regionMark)
                regionsProgress.append(regionTodo)
            else:
                regionsOpenPre.append(regionMark)
                regionsOpen.append(regionTodo)


        _delayed= int(_delayed)
        
        self.view.add_regions('dopletOpenPre', regionsOpenPre, 'comment', 'dot')
        self.view.add_regions('dopletOpen', regionsOpen, 'comment', 'dot', self.codeColor)

        sublime.set_timeout(lambda: self.view.add_regions('dopletProgressPre', regionsProgressPre, 'constant.language', 'dot'), 100*_delayed)
        sublime.set_timeout(lambda: self.view.add_regions('dopletProgress', regionsProgress, 'constant.language', 'dot', self.codeColor), 100*_delayed)

        sublime.set_timeout(lambda: self.view.add_regions('dopletInconsistentPre', regionsInconsistentPre, 'invalid', 'dot'), 200*_delayed)
        sublime.set_timeout(lambda: self.view.add_regions('dopletInconsistent', regionsInconsistent, 'invalid', 'dot', self.codeColor), 200*_delayed)



    def todoValidate(self, _id, _state, _tags, _priority, _comment):
        db= WCache().getDB()
        if db and (int(_id) in db.todoA):
            storedTask= db.todoA[int(_id)]
            tagsA= []
            for cTag in _tags.split(','):
                tagsA.append(cTag.strip())

            if storedTask.state!=_state or sorted(storedTask.tagsA)!=sorted(tagsA) or storedTask.lvl!=int(_priority) or storedTask.comment!=_comment:
                return False

        return True








class TypetodoToggleColorizeCommand(sublime_plugin.TextCommand):
    def run(self, _edit):
        cSettings= sublime.load_settings('typetodo.sublime-settings')
        cSettings.set('typetodo_nocolorize', not cSettings.get('typetodo_nocolorize'))
        sublime.save_settings('typetodo.sublime-settings')

        sublime.set_timeout(lambda: self.view.run_command('typetodo_maintain', {}), 0)








#todo 1554 (command, fix) +0: should adjust cursor position
class TypetodoRevivifyCommand(sublime_plugin.TextCommand):
    def run(self, _edit):
        _region= sublime.Region(0,self.view.size())
        content= self.view.substr(_region)
        contentA= []
        for cTodo in RE_TODO_EXISTING.finditer(content):
            contentA.append(cTodo)

        for cTodo in reversed(contentA):
            regionTodo= sublime.Region(cTodo.end('prefix'), cTodo.end('comment'))

            cId= cTodo.group('id')
            if not self.todoValidate(cId, cTodo.group('state'), cTodo.group('tags'), cTodo.group('priority'), cTodo.group('comment')):
                storedTask= WCache().getDB().todoA[int(cId)]
                commentType= self.view.substr(sublime.Region(cTodo.end('prefix'), cTodo.start('state')))

                replaceTodo= commentType +storedTask.state +'todo ' +cId +' (' +', '.join(storedTask.tagsA) +') +' +str(storedTask.lvl) +': ' +storedTask.comment

                self.view.replace(_edit, sublime.Region(cTodo.end('comment')+1, cTodo.end('comment')+1), replaceTodo+'\n')
                self.view.replace(_edit, sublime.Region(cTodo.end('state'), cTodo.start('id')), '     ')



    def todoValidate(self, _id, _state, _tags, _priority, _comment):
        db= WCache().getDB()
        if db and (int(_id) in db.todoA):
            storedTask= db.todoA[int(_id)]
            tagsA= []
            for cTag in _tags.split(','):
                tagsA.append(cTag.strip())

            if storedTask.state!=_state or sorted(storedTask.tagsA)!=sorted(tagsA) or storedTask.lvl!=int(_priority) or storedTask.comment!=_comment:
                return False

        return True
