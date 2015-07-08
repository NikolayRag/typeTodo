# coding= utf-8

import sublime, sublime_plugin
import sys, os

if sys.version < '3':
    from db import *
else:
    from .db import *


#   Caching mini-god singleton class.
#   Due to Sublime mechanism of having one shared API environment for number
#    of opened windows, the single plugin is also share it stored variables.
#    So it WCache is used to bind TodoDb() class to opened window.
#

class WCache(object):
    __instance = None
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(WCache, cls).__new__(cls, *args, **kwargs)
        return cls.__instance


    dbCache= {} #{window.folders[0]: TodoDb} cache



#   Get TodoDb() instance for current project.
#   Project name is used as identifier.
#
#   return existing or newly created TodoDb() instance.

    #only returns db after inited first time
    def getDB(self, _init= False, _callbackFetch= None):
        cWin= sublime.active_window()
        if not cWin:
            return False

        projectFolder= ''
        projFoldersA= cWin.folders()
        if len(projFoldersA):
            projectFolder= projFoldersA[0]


        if projectFolder not in self.dbCache:
            if not cWin.id() or not _init:
                return False

            self.dbCache[projectFolder]= False #hold place
            self.dbCache[projectFolder]= TodoDb(_callbackFetch, Config(projectFolder))

        return self.dbCache[projectFolder]




#   Plug to flush all databases when all Sublime windows closes.
#   Called with sublime.set_timeout() is only way found so far to detect this event.
#   No special flush neede on closing not-last window because Sublime environment
#    remains live.

    def exitHandler(self):
        if len(sublime.windows())==0: #called at very exit
            for dbI in self.dbCache:
               self.dbCache[dbI].flush()



#find command viewport
    
    resultsViewCache= {} #{window.id(): view} cache


#   Get 'Search todo' results view for window.
#   View is created if not cached or not found by name.

    def getResultsView(self, _create= True):
        cWin= sublime.active_window()
        if not cWin:
            return False

        wId= cWin.id()
        if wId in self.resultsViewCache:
            return self.resultsViewCache[wId]
            
        #check for duplicate
        for cView in cWin.views():
            if cView.name() == 'Doplets found':
                self.resultsViewCache[wId]= cView
                return self.resultsViewCache[wId]

        if not _create:
            return

        self.resultsViewCache[wId]= cWin.new_file()
        self.resultsViewCache[wId].set_name('Doplets found')
        self.resultsViewCache[wId].set_scratch(True)
        return self.resultsViewCache[wId]



#   Check if view with specified .buffer_id() is 'Search todo' results view.
#
#   *Didn't find better place, it shouldn't be here

    def checkResultsView(self, _viewId, _wipe=False):
        viewFind= self.getResultsView(False)
        if not viewFind:
            return

        if _viewId==viewFind.buffer_id():
            if _wipe:
                wId= sublime.active_window().id()
                del self.resultsViewCache[wId]
            return True


wCache= WCache() #hold against GC; Is it needed?
