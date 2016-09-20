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



#open context menu only for st3+
class TypetodoMouseContextCommand(sublime_plugin.TextCommand):

    if sys.version < '3':
        def run_(self, args):
            self.view.run_command('context_menu', args)
    else:
        def run_(self, view, args):
            mClick= self.view.window_to_text((args['event']['x'], args['event']['y']))
            todoRegion = self.view.line(mClick)
            _mod= RE_TODO_EXISTING.match(self.view.substr(todoRegion))

            if _mod:
                itemsA= []
                fnsA= []

                def makeSetState(_cState):
                    return lambda: self.view.run_command("typetodo_set", {"_state": _cState})

                for cState in STATE_LIST:
                    if cState:
                        itemsA.append(cState[0]+' : '+cState[1])
                        fnsA.append(makeSetState(cState[0]))


                itemsA.append('')
                fnsA.append(None)

                itemsA.append('Jump to .do')
                fnsA.append(lambda: self.view.run_command('typetodo_jump'))

                itemsA.append('Inconsistency')
                fnsA.append(lambda: self.view.run_command('typetodo_revivify'))

                itemsA.append('')
                fnsA.append(None)

                itemsA.append('Find todo')
                fnsA.append(lambda: self.view.run_command('typetodo_find'))

                itemsA.append('Config')
                fnsA.append(lambda: self.view.run_command('typetodo_cfg_open'))

                itemsA.append('HTTP repository')
                fnsA.append(lambda: self.view.run_command('typetodo_www'))



                def runContext(_cEl):
                    if _cEl>-1 and fnsA[_cEl]:
                        fnsA[_cEl]()

                self.view.run_command('drag_select', args)
                self.view.show_popup_menu(itemsA, runContext)

            else:
                self.view.run_command('context_menu', args)




#doubleclick handler for typetodo search results
#
class TypetodoMouseDoubleCommand(sublime_plugin.TextCommand):
    if sys.version < '3':
        def run_(self, args):
            self.run23(args)
    else:
        def run_(self, view, args):
            self.run23(args)


    def run23(self, args):
        #init search with .do id
        todoStr= self.view.substr( self.view.line(self.view.sel()[0]) )

        todoIndo= RE_TODO_STORED.match(todoStr)
        if todoIndo or WCache().checkResultsView(self.view.buffer_id()):
            self.view.run_command('typetodo_jump')
        else:
            self.view.run_command('drag_select', args)
