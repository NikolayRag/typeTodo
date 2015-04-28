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


class TypetodoMaintainCommand(sublime_plugin.TextCommand):
    if sys.version < '3':
        codeColor= sublime.DRAW_OUTLINED
    else:
        codeColor= sublime.DRAW_NO_OUTLINE |sublime.DRAW_NO_FILL |sublime.DRAW_SOLID_UNDERLINE

    def run(self, _edit, _regionStart= False, _regionEnd= False):
        if sublime.load_settings('typetodo.sublime-settings').get('typetodo_nocolorize'):
            self.view.erase_regions('dopletOpenPre')
            self.view.erase_regions('dopletOpen')

            self.view.erase_regions('dopletProgressPre')
            self.view.erase_regions('dopletProgress')

            self.view.erase_regions('dopletInconsistentPre')
            self.view.erase_regions('dopletInconsistent')

            return

#todo 492 (command, fix) +0: should use specified region to speedup
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


        self.view.add_regions('dopletOpenPre', regionsOpenPre, 'comment', 'dot')
        self.view.add_regions('dopletOpen', regionsOpen, 'comment', 'dot', self.codeColor)

        self.view.add_regions('dopletProgressPre', regionsProgressPre, 'string', 'dot')
        self.view.add_regions('dopletProgress', regionsProgress, 'string', 'dot', self.codeColor)

        self.view.add_regions('dopletInconsistentPre', regionsInconsistentPre, 'invalid', 'dot')
        self.view.add_regions('dopletInconsistent', regionsInconsistent, 'invalid', 'dot', self.codeColor)


    def todoValidate(self, _id, _state, _tags, _priority, _comment):
        db= getDB(self.view)
        if db and (int(_id) in db.todoA):
            storedTask= db.todoA[int(_id)]
            if storedTask.state!=_state or ', '.join(storedTask.tagsA)!=_tags or storedTask.lvl!=int(_priority) or storedTask.comment!=_comment:
                return False
        return True


class TypetodoToggleColorizeCommand(sublime_plugin.TextCommand):

    def run(self, _edit):
        cSettings= sublime.load_settings('typetodo.sublime-settings')
        cSettings.set('typetodo_nocolorize', not cSettings.get('typetodo_nocolorize'))
        sublime.save_settings('typetodo.sublime-settings')

        sublime.set_timeout(lambda: self.view.run_command('typetodo_maintain', {}), 0)
