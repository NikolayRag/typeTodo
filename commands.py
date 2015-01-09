import sublime, sublime_plugin, webbrowser
import sys, os

if sys.version < '3':
    from db import *
    from cache import *
else:
    from .db import *
    from .cache import *



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
#todo 164 (command) +0: only 'file' mode is saved instantly, additional dbs saved at exit/edit
        cDb.reset()
