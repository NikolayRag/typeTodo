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
class TypetodoContextMouseCommand(sublime_plugin.TextCommand):
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

                itemsA.append('Search todo')
                fnsA.append(lambda: self.view.run_command('typetodo_find'))

                itemsA.append('Update inconsistency')
                fnsA.append(lambda: self.view.run_command('typetodo_revivify'))

                itemsA.append('')
                fnsA.append(None)


                def makeSetState(_cState):
                    return lambda: self.view.run_command("typetodo_set_state", {"_replaceWith": _cState})

                for cState in STATE_LIST:
                    itemsA.append('\''+cState+'\': '+STATE_LIST[cState])
                    fnsA.append(makeSetState(cState))


                itemsA.append('')
                fnsA.append(None)

                itemsA.append('Open http base')
                fnsA.append(lambda: self.view.run_command('typetodo_www'))

                itemsA.append('Open config')
                fnsA.append(lambda: self.view.run_command('typetodo_cfg_open'))



                def runContext(_cEl):
                    if _cEl>-1 and fnsA[_cEl]:
                        fnsA[_cEl]()

                self.view.run_command('drag_select', args)
                self.view.show_popup_menu(itemsA, runContext)

            else:
                self.view.run_command('context_menu', args)




#doubleclick handler for typetodo search results
#
class TypetodoJumpMouseCommand(sublime_plugin.TextCommand):
    if sys.version < '3':
        def run_(self, args):
            self.run23(args)
    else:
        def run_(self, view, args):
            self.run23(args)


    def run23(self, args):
        if WCache().checkResultsView(self.view.buffer_id()):
            self.view.run_command('typetodo_find', {'_query':False})
        else:
            self.view.run_command('drag_select', args)
