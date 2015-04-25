# coding= utf-8

#todo 1 (interaction) -1: multiline TODO
#todo 8 (interaction) +0: tag auto-complete; or use command to choose tag
#todo 9 (interaction) -1: using snippets
#todo 10 (interaction) +0: colorizing
#todo 11 (interaction) -2: make more TODO formats available

#todo 232 (feature) +0: introduce sub-todo's that are part of other

#todo 3 (consistency,v2) -10: check at start
#todo 4 (consistency,v2) -10: check as source edited
#todo 5 (consistency,v2) -10: check as db edited (saved)

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
    view= None

#todo 236 (db, config) +0: reset db after editing .do

    def on_deactivated(self,_view):
        db=getDB(_view)
        if db:
            db.pushReset()

        sublime.set_timeout(exitHandler, 0) #sublime's timeout is needed to let sublime.windows() be [] at exit


    #maybe lil overheat here, but it works
    def on_selection_modified(self, _view):
        if self.mutexUnlocked:
            self.mutexUnlocked= 0
#            self.view= _view
#            self.runa(None)
            _view.run_command('typetodo_subst')
            self.mutexUnlocked= 1

    def on_modified(self, _view):
        if self.mutexUnlocked:
            self.mutexUnlocked= 0
#            self.view= _view
#            self.runa(None, True)
            _view.run_command('typetodo_subst', {'_modified': True})
            self.mutexUnlocked= 1


#=todo 377 (interaction) +0: Add +/- shortcut to change priority
    def on_query_context(self, _view, _key, _op, _val, _match):
        if _key=='typetodoUp' or _key=='typetodoDown':
            if len(_view.sel())!=1: #more than one cursors skipped for number of reasons
                return;

            todoRegion = _view.line(_view.sel()[0])
            todoText = _view.substr(todoRegion)

            _mod= RE_TODO_EXISTING.match(todoText) #mod goes first to allow midline todo
            if _mod:
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


#todo 210 (general) +0: implement editing of project .do file


class TypetodoSubstCommand(sublime_plugin.TextCommand):
#todo 229 (ux) +0: make cached stuff per-project (or not?)
    lastCat= ['general']
    lastLvl= '+0'

    prevTriggerNew= None
    prevStateMod= None
    noundo= False

    def setRO(self, _ro):
        return
#        if self.noundo:
#            self.view.set_read_only(0)
#            self.view.end_edit(self.noundo)
#            self.noundo= False

        if _ro:
#            self.noundo= self.view.begin_edit()
            self.view.set_read_only(True)
#            return
        else:
            self.view.set_read_only(False)


    def run(self, _edit, _modified= False):
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
            self.setRO(not allowFlag)




            #should trigger at '+' or '!' entered
            doWipe= _mod.group('state')=='+' and self.prevStateMod!='+'
            if not doWipe: doWipe= _mod.group('state')=='!' and self.prevStateMod!='!'
            self.prevStateMod= _mod.group('state')

            if _modified:
                self.substUpdate(_mod.group('state'), _mod.group('id'), _mod.group('tags'), _mod.group('priority'), _mod.group('comment'), _mod.group('prefix'), todoRegion, doWipe)

            return

        self.setRO(0)


        _new = RE_TODO_NEW.match(todoText)
        if _new:
            #should trigger at ':' entered
            doTrigger= _new.group('trigger')==':' and self.prevTriggerNew!=':'
            self.prevTriggerNew= _new.group('trigger')

            if _modified and doTrigger:
                self.substNew(_new.group('prefix'), _new.group('comment'), todoRegion)

            return

    #create new todo in db and return string to replace original 'todo:'
    def substNew(self, _prefx, _postfx, _region):
        todoId= self.cfgStore(0, '', self.lastCat[0], self.lastLvl, self.view.file_name(), '')

        todoComment= _prefx + 'todo ' +str(todoId) +' (${1:' +self.lastCat[0] +'}) ${2:' +self.lastLvl +'}: ${0:}' +_postfx +''
        self.view.run_command('typetodo_reg_replace', {'_regStart': _region.a, '_regEnd': _region.b})
        self.view.run_command("insert_snippet", {"contents": todoComment})

        if _postfx != '': #need to save if have comment at creation
            self.substUpdate('', todoId, self.lastCat[0], self.lastLvl, _postfx, _prefx, _region)

        return todoId

    #store to db and, if changed state, remove comment
    updVals= None
    def substDoUpdate(self, _txt=False):
        if self.updVals['_tags'] != None:
            self.lastCat[0]= self.updVals['_tags']

        if _txt==False:
            _txt= self.updVals['_comment']
        self.updVals['_id']= self.cfgStore(self.updVals['_id'], self.updVals['_state'], self.updVals['_tags'], self.updVals['_lvl'] or 0, self.view.file_name(), _txt)

        if self.updVals['_wipe']:
            todoRegion= self.view.full_line(self.updVals['_region'])
            if self.updVals['_prefix']!='': #midline todo
                todoRegion= sublime.Region(
                    todoRegion.a +len(self.updVals['_prefix']),
                    todoRegion.b -1
                )

            self.view.run_command('typetodo_reg_replace', {'_regStart': todoRegion.a, '_regEnd': todoRegion.b})


    def substUpdate(self, _state, _id, _tags, _lvl, _comment, _prefix, _region, _wipe=False):
        self.updVals= {'_state':_state, '_id':_id, '_tags':_tags, '_lvl':_lvl, '_comment':_comment, '_prefix':_prefix, '_region':_region, '_wipe':_wipe}

        if _state=='!':
            self.view.window().show_input_panel('Reason of canceling:', '', self.substDoUpdate, None, self.substDoUpdate)
        else:
            self.substDoUpdate()


    def cfgStore(self, _id, _state, _tags, _lvl, _fileName, _comment):
        return getDB(self.view).store(_id, _state, (_tags or '').split(','), _lvl, _fileName, _comment)

#=todo 21 (general) +0: handle filename change, basically for new unsaved files


try:
    if sys.version < '3':
        from test import *
    else:
        from .test import *
except:
    None