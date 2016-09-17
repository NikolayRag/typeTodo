# coding= utf-8

#todo 1 (interaction, feature) +1: multiline TODO

#=todo 232 (feature) +1: introduce sub-todo's that are part of other



import sublime, sublime_plugin
import sys, re

if sys.version < '3':
    from db import *
    from cache import *
    from c import *
else:
    from .db import *
    from .cache import *
    from .c import *



#callback at end of fetching DB
def dbMaintainance():
    cWnd= sublime.active_window()
    if not cWnd: return

    cView= cWnd.active_view()
    if not cView: return

    cView.run_command('typetodo_maintain', {})



class TypetodoEvent(sublime_plugin.EventListener):
    mutexUnlocked= 1
    view= None



#   React on all Sublime window close event.
#   React on switching project in window.

    def on_deactivated(self, _view):
#todo 1783 (cleanup, uncertain) -1: switching project in window not clearly fixed, need review
        sublime.set_timeout(lambda: self.on_activated(_view), 200) #spike to catch switching project in existing window

        sublime.set_timeout(WCache().exitHandler, 0) #sublime's timeout is needed to let sublime.windows() be [] at exit





#   React on switching into view, initializing DB fetch-synchronize-save.
#   Switching into view actually duplicated number of times with several
#    handlers, but this handler is main and is used for TodoDb() creation.

    def on_activated(self, _view):
        constCorrect(_view) #coz settings are delayed at load

        cDb= WCache().getDB(True, dbMaintainance) #really applies only once

        #set 'file' syntax where it is not right and check consistency
        if cDb:
            cDb.pushReset()

            #set .do synthax for all 'file' databases
            for cSetting in cDb.config.settings:
                if cSetting.engine=='file':
                    if cSetting.file==_view.file_name() and _view.settings().get('syntax')!='Packages/TypeTodo/typeTodo.tmLanguage':
                        _view.set_syntax_file('Packages/TypeTodo/typeTodo.tmLanguage')


        self.on_load_activate(_view)



#   Shortcut for on_activated()

    def on_load(self, _view):
        self.on_load_activate(_view)



#   Set readonly for results; maintain and colorize

    def on_load_activate(self, _view):
        if WCache().checkResultsView(_view.buffer_id()):
            sublime.set_timeout(lambda: _view.set_read_only(True), 0)
 
        sublime.set_timeout(lambda: _view.run_command('typetodo_maintain', {}), 0)



#   Wipe results view from cache

    def on_close(self, _view):
        WCache().checkResultsView(_view.buffer_id(), True)





#   Both on_modified and on_selection_modified deal with cursor position,
#    saving current inside-doplet context to be used later,
#    on_modified also reacts on doplet editing.

    def on_selection_modified(self, _view):
        #not for results view
        if WCache().checkResultsView(_view.buffer_id()):
            return

        if self.mutexUnlocked:
            self.mutexUnlocked= 0
            self.view= _view
            sublime.set_timeout(self.matchTodo, 0) #negative undo effects if no timeout
            self.mutexUnlocked= 1


    def on_modified(self, _view):
        if self.mutexUnlocked:
            self.mutexUnlocked= 0
            self.view= _view
            self.matchTodo(True)
            self.mutexUnlocked= 1



#   Use previously format autocompletion list.
#   It is formed every time when cursor moves into doplet.

    def on_query_completions(self, view, prefix, locations):
        return self.autoList












    lastCat= ['general']
    lastLvl= '+0'

    prevTriggerNew= None
    prevStateMod= None
    todoCursorPlace= False
    todoMatch= None

    autoList= False


#   Collect all tags from existing database and form them for autocompletion.
#
#   Return list suitable for autocompletion.

    def tagsAutoCollect(self):
        cDb= WCache().getDB()
        if not cDb:
            return


        tagsA= []

        if cDb:
            todosA= cDb.todoA
            for cTask in todosA:
                for cTag in todosA[cTask].tagsA:
                    if cTag not in tagsA:
                        tagsA.append(cTag)

        tagsListA= [(' ','')]
        for cTag in tagsA:
            tagsListA.append(('tag: '+cTag, cTag))

        return tagsListA



#   Check current line at every cursor movement or text modification.
#   If line is doplet then:
#       context is saved for later use (on_query_context)
#       autocomplete list is formed from database tags
#       readonly is set
#       doplet edits are saved into database
#   If line is doplet keyword (#todo):
#       new doplet is created
#   If line is neither:
#       readonly is removed

    def matchTodo(self, _modified= False):
        self.autoList= False
        self.todoCursorPlace= False
        if len(self.view.sel())!=1: #more than one cursors skipped for number of reasons
            return;
        
        todoRegion = self.view.line(self.view.sel()[0])
        todoText = self.view.substr(todoRegion)

        self.todoMatch= todoModMatch= RE_TODO_EXISTING.match(todoText) #mod goes first to allow midline todo
        if todoModMatch:
            #resolve cursor place
            selStart= self.view.rowcol(self.view.sel()[0].a)[1]
            selEnd= selStart +self.view.sel()[0].b -self.view.sel()[0].a
            if selStart>selEnd:
                tmp= selStart
                selStart= selEnd
                selEnd= tmp

            #store doplet field name under cursor
            self.todoCursorPlace= 'preTodo'
            if selStart>=todoModMatch.end('prefix') and selEnd<=todoModMatch.end('postfix'):
                self.todoCursorPlace= 'todo'
                for rangeName in ('prefix', 'state', 'tags', 'priority', 'postfix'):
                    if selStart>=todoModMatch.start(rangeName) and selEnd<=todoModMatch.end(rangeName):
                        self.todoCursorPlace= rangeName
                        break

            #protect fields
            self.view.set_read_only(self.todoCursorPlace=='todo')

#todo 1239 (interaction, unsolved) +0: get rid of snippets for tags autocomplete
            #toggle default autocomplete to avoid exceeding entries for doplet
            self.view.settings().erase('auto_complete_selector')
            if self.todoCursorPlace=='tags':
                self.autoList= self.tagsAutoCollect()
                self.view.settings().set('auto_complete_selector', 'source')


            #should trigger at '+' or '!' entered
            doWipe= todoModMatch.group('state')=='+' and self.prevStateMod!='+'
            if not doWipe: doWipe= todoModMatch.group('state')=='!' and self.prevStateMod!='!'
            self.prevStateMod= todoModMatch.group('state')

            if _modified:
                self.substUpdate(todoModMatch.group('state'), todoModMatch.group('id'), todoModMatch.group('tags'), todoModMatch.group('priority'), todoModMatch.group('comment'), todoModMatch.group('prefix'), todoRegion, doWipe)
                sublime.set_timeout(lambda: self.view.run_command('typetodo_maintain', {'_delayed':0}), 0)

            return

        self.view.set_read_only(False)


        todoNewMatch = RE_TODO_NEW.match(todoText)
        if todoNewMatch:
            #should trigger at ':' entered
            doTrigger= todoNewMatch.group('trigger')==':' and self.prevTriggerNew!=':'
            self.prevTriggerNew= todoNewMatch.group('trigger')

            if _modified and doTrigger:
                self.substNew(todoNewMatch.group('prefix'), todoNewMatch.group('comment'), todoRegion)
                sublime.set_timeout(lambda: self.view.run_command('typetodo_maintain', {'_delayed':0}), 0)

            return


#   Create new todo in db and return string to replace original 'todo:'
#   Saves first version of task if _postfx supplied, that is used when
#    creating doplet in mid-line.

    def substNew(self, _prefx, _postfx, _region):
        todoId= self.cfgStore(0, '', self.lastCat[0], self.lastLvl, self.view.file_name(), '')

        todoComment= _prefx + ' todo ' +str(todoId) +' (${1:' +self.lastCat[0] +'}) ${2:' +self.lastLvl +'}: ${0:}' +_postfx +''
        self.view.run_command('typetodo_reg_replace', {'_regStart': _region.a, '_regEnd': _region.b})
        self.view.run_command("insert_snippet", {"contents": todoComment})

        if _postfx != '': #need to save if have comment at creation
            self.substUpdate('', todoId, self.lastCat[0], self.lastLvl, _postfx, _prefx, _region)

        return todoId


#   Store to db and, if changed state, remove comment
#
#   Return function to be used in substUpdate()

    def substDoUpdate(self, _updVals):
        def func(_txt=False):
            if _txt==False or _txt=='':
                _txt= _updVals['_comment']

            cView= _updVals['_view']
            if _updVals['_tags'] != None:
                self.lastCat[0]= _updVals['_tags']

            _updVals['_id']= self.cfgStore(_updVals['_id'], _updVals['_state'], _updVals['_tags'], _updVals['_lvl'] or 0, self.view.file_name(), _txt)

            if _updVals['_wipe']:
                todoRegion= cView.full_line(_updVals['_region'])
                if _updVals['_prefix']!='': #midline todo
                    todoRegion= sublime.Region(
                        todoRegion.a +len(_updVals['_prefix']),
                        todoRegion.b
                    )

                cView.run_command('typetodo_reg_replace', {'_regStart': todoRegion.a, '_regEnd': todoRegion.b-1})


        return func



#Cancel deleting todo
#
    def substRestore(self, _updVals):
        def func(_txt=False):
            cDb= WCache().getDB()
            if not cDb:
                return

            #restore todo string
            cString= self.view.substr(_updVals['_region'])
            cTodo= RE_TODO_EXISTING.match(cString)
            storedTask= cDb.todoA[int(_updVals['_id'])]

            replaceTodo= storedTask.state +'todo ' +str(storedTask.id) +' (' +', '.join(storedTask.tagsA) +') +' +str(storedTask.lvl) +': ' +storedTask.comment

            self.view.run_command('typetodo_reg_replace', {'_regStart': _updVals['_region'].a+cTodo.start('state'), '_regEnd': _updVals['_region'].a+cTodo.end('comment'), '_replaceWith': replaceTodo})

        return func



#   Update existing task.
#   Ask for 'reason' for 'cancel' state.

    def substUpdate(self, _state, _id, _tags, _lvl, _comment, _prefix, _region, _wipe=False):
        updVals= {'_view':self.view, '_state':_state, '_id':_id, '_tags':_tags, '_lvl':_lvl, '_comment':_comment, '_prefix':_prefix, '_region':_region, '_wipe':_wipe}

        if _state=='!' and _comment!='':
            self.view.window().show_input_panel('Reason of canceling:', '', self.substDoUpdate(updVals), None, self.substRestore(updVals))
        else:
            self.substDoUpdate(updVals)()



#   Gate to TodoDB().store()
#   Store new or existing values as task.

    def cfgStore(self, _id, _state, _tags, _lvl, _fileName, _comment):
        cDb= WCache().getDB()
        if cDb:
            return cDb.store(_id, _state, (_tags or '').split(','), _lvl, _fileName, _comment)

        sublime.message_dialog('TypeTodo error:\n\n\tTypeTodo was not properly initialized. \n\tMaybe reinstalling will help')



try:
    if sys.version < '3':
        from test import *
    else:
        from .test import *
except:
    None