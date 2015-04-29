# coding= utf-8

#todo 1 (interaction) -1: multiline TODO
#todo 8 (interaction) +0: tag auto-complete; or use command to choose tag
#todo 11 (interaction) -2: make more TODO formats available

#todo 232 (feature) +0: introduce sub-todo's that are part of other


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


def exitHandler(): # one for all, at very exit
    if len(sublime.windows())==0:
        for dbI in projectDbCache:
           projectDbCache[dbI].flush(True)



class TypetodoEvent(sublime_plugin.EventListener):
    mutexUnlocked= 1
#todo 236 (db, config) +0: reset db after editing .do
    view= None

    def on_deactivated(self,_view):
        db=getDB(_view)
        if db:
            db.pushReset()

        sublime.set_timeout(exitHandler, 0) #sublime's timeout is needed to let sublime.windows() be [] at exit


    def on_activated(self,_view):
        db=getDB(_view)
        if db:
            db.lastActiveView= _view
        sublime.set_timeout(lambda: _view.run_command('typetodo_maintain', {}), 0)


    def on_load(self,_view):
        db=getDB(_view)
        if db:
            db.lastActiveView= _view
        sublime.set_timeout(lambda: _view.run_command('typetodo_maintain', {}), 0)


    def on_close(self,_view):
        global resultsView
        wId= sublime.active_window().id()
        if wId in resultsView and _view.buffer_id()==resultsView[wId].buffer_id():
            del resultsView[wId]


    #maybe lil overheat here, but it works
    def on_selection_modified(self, _view):
        if sublime.active_window():
            global resultsView
            wId= sublime.active_window().id()
            if wId in resultsView and _view.buffer_id()==resultsView[wId].buffer_id():
                return

        if self.mutexUnlocked:
            self.mutexUnlocked= 0
            self.view= _view
            sublime.set_timeout(self.matchTodo, 0) #negative effects at undo if no timeout
            self.mutexUnlocked= 1


    def on_modified(self, _view):
        if sublime.active_window():
            global resultsView
            wId= sublime.active_window().id()
            if wId in resultsView and _view.buffer_id()==resultsView[wId].buffer_id():
                return

        if self.mutexUnlocked:
            self.mutexUnlocked= 0
            self.view= _view
            self.matchTodo(True)
            self.mutexUnlocked= 1


#=todo 563 (interaction) +0: allow to change doplet state by pressing corresponding key (-/+/=/!) everywhere in protected doplet; same for up/down for priority
#todo 449 (fix) -1: too much code duplicated from matchTodo()
    def on_query_context(self, _view, _key, _op, _val, _match):
        if _key=='typetodoUp' or _key=='typetodoDown' or _key=='typetodoSet':
            if len(_view.sel())!=1: #more than one cursors skipped for number of reasons
                return;

            todoRegion = _view.line(_view.sel()[0])
            todoText = _view.substr(todoRegion)

            _mod= RE_TODO_EXISTING.match(todoText) #mod goes first to allow midline todo
            if _mod:
                if _key=='typetodoSet':
                    return True

                selStart= _view.rowcol(_view.sel()[0].a)[1]
                selEnd= selStart +_view.sel()[0].b -_view.sel()[0].a
                if selStart>selEnd:
                    tmp= selStart
                    selStart= selEnd
                    selEnd= tmp

                if selStart>=_mod.start('priority') and selEnd<=_mod.end('priority'):
                    addValue= 1
                    if _key=='typetodoDown':
                        addValue= -1
                    newPriority= int(_mod.group('priority')) +addValue
                    newPriPfx= ''
                    if newPriority>=0:
                        newPriPfx= '+'
                    newPriority= newPriPfx +str(newPriority)
                    
                    _view.run_command('typetodo_reg_replace', {'_regStart': todoRegion.a+_mod.start('priority'), '_regEnd': todoRegion.a+_mod.end('priority'), '_replaceWith': newPriority})
                    return True

#todo 210 (db) -1: implement editing of project .do file


#todo 229 (ux) +0: make cached stuff per-project (or not?)
    lastCat= ['general']
    lastLvl= '+0'

    prevTriggerNew= None
    prevStateMod= None


    def matchTodo(self, _modified= False):
        if len(self.view.sel())!=1: #more than one cursors skipped for number of reasons
            return;
        
        todoRegion = self.view.line(self.view.sel()[0])
        todoText = self.view.substr(todoRegion)

        _mod= RE_TODO_EXISTING.match(todoText) #mod goes first to allow midline todo
        if _mod:
            #set readonly
            selStart= self.view.rowcol(self.view.sel()[0].a)[1]
            selEnd= selStart +self.view.sel()[0].b -self.view.sel()[0].a
            if selStart>selEnd:
                tmp= selStart
                selStart= selEnd
                selEnd= tmp

            allowFlag= False
            if selStart<=_mod.end('prefix') and selEnd>=_mod.start('postfix'):
                allowFlag= True
            else:
                for rangeName in ('prefix', 'state', 'tags', 'priority', 'postfix'):
                    if selStart>=_mod.start(rangeName) and selEnd<=_mod.end(rangeName):
                        allowFlag= True
                        break
            self.view.set_read_only(not allowFlag)


            #should trigger at '+' or '!' entered
            doWipe= _mod.group('state')=='+' and self.prevStateMod!='+'
            if not doWipe: doWipe= _mod.group('state')=='!' and self.prevStateMod!='!'
            self.prevStateMod= _mod.group('state')

            if _modified:
                self.substUpdate(_mod.group('state'), _mod.group('id'), _mod.group('tags'), _mod.group('priority'), _mod.group('comment'), _mod.group('prefix'), todoRegion, doWipe)
                sublime.set_timeout(lambda: self.view.run_command('typetodo_maintain', {'_regionStart': int(todoRegion.a), '_regionEnd': int(todoRegion.b)}), 0)

            return

        self.view.set_read_only(False)


        _new = RE_TODO_NEW.match(todoText)
        if _new:
            #should trigger at ':' entered
            doTrigger= _new.group('trigger')==':' and self.prevTriggerNew!=':'
            self.prevTriggerNew= _new.group('trigger')

            if _modified and doTrigger:
                self.substNew(_new.group('prefix'), _new.group('comment'), todoRegion)
                sublime.set_timeout(lambda: self.view.run_command('typetodo_maintain', {'_regionStart': int(todoRegion.a), '_regionEnd': int(todoRegion.b)}), 0)

            return

    #create new todo in db and return string to replace original 'todo:'
    def substNew(self, _prefx, _postfx, _region):
        todoId= self.cfgStore(getDB(self.view), 0, '', self.lastCat[0], self.lastLvl, self.view.file_name(), '')

        todoComment= _prefx + 'todo ' +str(todoId) +' (${1:' +self.lastCat[0] +'}) ${2:' +self.lastLvl +'}: ${0:}' +_postfx +''
        self.view.run_command('typetodo_reg_replace', {'_regStart': _region.a, '_regEnd': _region.b})
        self.view.run_command("insert_snippet", {"contents": todoComment})

        if _postfx != '': #need to save if have comment at creation
            self.substUpdate('', todoId, self.lastCat[0], self.lastLvl, _postfx, _prefx, _region)

        return todoId

    #store to db and, if changed state, remove comment
    updVals= None
    def substDoUpdate(self, _txt=False):
        cView= self.updVals['_view']
        if self.updVals['_tags'] != None:
            self.lastCat[0]= self.updVals['_tags']

        if _txt==False or _txt=='':
            _txt= self.updVals['_comment']
        self.updVals['_id']= self.cfgStore(getDB(cView), self.updVals['_id'], self.updVals['_state'], self.updVals['_tags'], self.updVals['_lvl'] or 0, self.view.file_name(), _txt)

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

#=todo 21 (general) +0: handle filename change, basically for new unsaved files


try:
    if sys.version < '3':
        from test import *
    else:
        from .test import *
except:
    None