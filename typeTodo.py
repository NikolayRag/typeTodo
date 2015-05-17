# coding= utf-8

#todo 1 (interaction, feature) -1: multiline TODO
#todo 11 (interaction, unsure) -10: make more TODO formats available

#todo 232 (feature) +0: introduce sub-todo's that are part of other
#todo 210 (db, feature, unsure) -5: implement editing of project .do file


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

    def on_deactivated(self,_view):
        db= WCache().getDB()
        if db:
            db.pushReset()

        sublime.set_timeout(WCache().exitHandler, 0) #sublime's timeout is needed to let sublime.windows() be [] at exit


    def on_activated(self,_view):
        WCache().getDB(True, dbMaintainance) #really applies only once

        sublime.set_timeout(lambda: _view.run_command('typetodo_maintain', {}), 0)


    def on_load(self,_view):
        sublime.set_timeout(lambda: _view.run_command('typetodo_maintain', {}), 0)


    def on_close(self,_view):
            WCache().checkResultsView(_view.buffer_id(), True)



    def on_selection_modified(self, _view):
        if WCache().checkResultsView(_view.buffer_id()):
            return

        if self.mutexUnlocked:
            self.mutexUnlocked= 0
            self.view= _view
            sublime.set_timeout(self.matchTodo, 0) #negative effects at undo if no timeout
            self.mutexUnlocked= 1


    def on_modified(self, _view):
        if self.mutexUnlocked:
            self.mutexUnlocked= 0
            self.view= _view
            self.matchTodo(True)
            self.mutexUnlocked= 1




    def on_query_completions(self, view, prefix, locations):
        return self.autoList



    def on_query_context(self, _view, _key, _op, _val, _match):

        if self.todoCursorPlace!=False:
            todoRegion = _view.line(_view.sel()[0])


            if _key=='typetodoUp':
                addValue= 1

            elif _key=='typetodoDown':
                addValue= -1

            else:
                return

            newPriority= int(self.todoMatch.group('priority')) +addValue
            newPriPfx= ''
            if newPriority>=0:
                newPriPfx= '+'
            newPriority= newPriPfx +str(newPriority)
            
            _view.set_read_only(False)
            _view.run_command('typetodo_reg_replace', {
                '_regStart': todoRegion.a+self.todoMatch.start('priority'),
                '_regEnd': todoRegion.a+self.todoMatch.end('priority'),
                '_replaceWith': newPriority
            })
            return True










    lastCat= ['general']
    lastLvl= '+0'

    prevTriggerNew= None
    prevStateMod= None
    todoCursorPlace= False
    todoMatch= None

    autoList= False

    def tagsAutoCollect(self):
        tagsA= []
        todosA= WCache().getDB().todoA
        for cTask in todosA:
            for cTag in todosA[cTask].tagsA:
                if cTag not in tagsA:
                    tagsA.append(cTag)

        tagsListA= [(' ','')]
        for cTag in tagsA:
            tagsListA.append((cTag, cTag))

        return tagsListA



    def matchTodo(self, _modified= False):
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

            self.todoCursorPlace= 'todoString'
            if selStart>=todoModMatch.end('prefix') and selEnd<=todoModMatch.end('postfix'):
                self.todoCursorPlace= 'todo'
                for rangeName in ('prefix', 'state', 'tags', 'priority', 'postfix'):
                    if selStart>=todoModMatch.start(rangeName) and selEnd<=todoModMatch.end(rangeName):
                        self.todoCursorPlace= rangeName
                        break

            self.view.set_read_only(self.todoCursorPlace=='todo')

#todo 1239 (interaction, unsolved) +0: get rid of snippets for tags autocomplete
            #toggle autocomplete
            self.autoList= False
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
                sublime.set_timeout(lambda: self.view.run_command('typetodo_maintain', {'_delayed':0, '_regionStart': int(todoRegion.a), '_regionEnd': int(todoRegion.b)}), 0)

            return

        self.view.set_read_only(False)


        todoNewMatch = RE_TODO_NEW.match(todoText)
        if todoNewMatch:
            #should trigger at ':' entered
            doTrigger= todoNewMatch.group('trigger')==':' and self.prevTriggerNew!=':'
            self.prevTriggerNew= todoNewMatch.group('trigger')

            if _modified and doTrigger:
                self.substNew(todoNewMatch.group('prefix'), todoNewMatch.group('comment'), todoRegion)
                sublime.set_timeout(lambda: self.view.run_command('typetodo_maintain', {'_delayed':0, '_regionStart': int(todoRegion.a), '_regionEnd': int(todoRegion.b)}), 0)

            return

    #create new todo in db and return string to replace original 'todo:'
    def substNew(self, _prefx, _postfx, _region):
        todoId= self.cfgStore(WCache().getDB(), 0, '', self.lastCat[0], self.lastLvl, self.view.file_name(), '')

        todoComment= _prefx + 'todo ' +str(todoId) +' (${1:' +self.lastCat[0] +'}) ${2:' +self.lastLvl +'}: ${0:}' +_postfx +''
        self.view.run_command('typetodo_reg_replace', {'_regStart': _region.a, '_regEnd': _region.b})
        self.view.run_command("insert_snippet", {"contents": todoComment})

        if _postfx != '': #need to save if have comment at creation
            self.substUpdate('', todoId, self.lastCat[0], self.lastLvl, _postfx, _prefx, _region)

        return todoId

    #store to db and, if changed state, remove comment
#todo 690 (check) +0: since updVals passed delayed, there can be inconsistence
    updVals= None
    def substDoUpdate(self, _txt=False):
        cView= self.updVals['_view']
        if self.updVals['_tags'] != None:
            self.lastCat[0]= self.updVals['_tags']

        if _txt==False or _txt=='':
            _txt= self.updVals['_comment']
        self.updVals['_id']= self.cfgStore(WCache().getDB(), self.updVals['_id'], self.updVals['_state'], self.updVals['_tags'], self.updVals['_lvl'] or 0, self.view.file_name(), _txt)

        if self.updVals['_wipe']:
            todoRegion= cView.full_line(self.updVals['_region'])
            if self.updVals['_prefix']!='': #midline todo
                todoRegion= sublime.Region(
                    todoRegion.a +len(self.updVals['_prefix']),
                    todoRegion.b
                )

            cView.run_command('typetodo_reg_replace', {'_regStart': todoRegion.a, '_regEnd': todoRegion.b-1})


    def substUpdate(self, _state, _id, _tags, _lvl, _comment, _prefix, _region, _wipe=False):
        self.updVals= {'_view':self.view, '_state':_state, '_id':_id, '_tags':_tags, '_lvl':_lvl, '_comment':_comment, '_prefix':_prefix, '_region':_region, '_wipe':_wipe}

        if _state=='!':
            self.view.window().show_input_panel('Reason of canceling:', '', self.substDoUpdate, None, self.substDoUpdate)
        else:
            self.substDoUpdate()


    def cfgStore(self, _db, _id, _state, _tags, _lvl, _fileName, _comment):
        if _db:
            return _db.store(_id, _state, (_tags or '').split(','), _lvl, _fileName, _comment)

        sublime.message_dialog('TypeTodo error:\n\tDoplet was not saved. \n\tThis is known issue and\n\twill be fixed')

#todo 21 (interaction, feature) +0: handle filename change, basically for new unsaved files


try:
    if sys.version < '3':
        from test import *
    else:
        from .test import *
except:
    None