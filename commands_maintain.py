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


#Implicitly called command for validating visible doplets and colorizing
#
class TypetodoMaintainCommand(sublime_plugin.TextCommand):
    if sys.version < '3':
        codeColor= sublime.DRAW_OUTLINED
    else:
        codeColor= sublime.DRAW_NO_OUTLINE |sublime.DRAW_NO_FILL |sublime.DRAW_SOLID_UNDERLINE


    def run(self, _edit, _delayed=True):
        _region= sublime.Region(0,self.view.size())
        contentA= []
        for cLine in self.view.substr(_region).split('\n'):
            if len(cLine)>SKIP_SEARCH_LINESIZE:
                cLine= ''
            contentA.append(cLine)

        content= '\n'.join(contentA)


        todos= []
        regionsOpenPre= []
        regionsOpen= []
        regionsProgressPre= []
        regionsProgress= []
        regionsInconsistentPre= []
        regionsInconsistent= []


        for cTodo in RE_TODO_INCONSISTENT.finditer(content):
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

        sublime.set_timeout(lambda: self.view.add_regions('dopletProgressPre', regionsProgressPre, 'constant.language', 'dot'), 150*_delayed)
        sublime.set_timeout(lambda: self.view.add_regions('dopletProgress', regionsProgress, 'constant.language', 'dot', self.codeColor), 150*_delayed)

        sublime.set_timeout(lambda: self.view.add_regions('dopletInconsistentPre', regionsInconsistentPre, 'invalid', 'dot'), 300*_delayed)
        sublime.set_timeout(lambda: self.view.add_regions('dopletInconsistent', regionsInconsistent, 'invalid', 'dot', self.codeColor), 300*_delayed)



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







#Double all inconsistent doplets with actual version
#
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
