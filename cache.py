# coding= utf-8

import sublime, sublime_plugin
import sys, os

if sys.version < '3':
    from db import *
else:
    from .db import *



class WCache(object):
    __instance = None
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(WCache, cls).__new__(cls, *args, **kwargs)
        return cls.__instance



    dbCache= {} #{window.id(): TodoDb} cache


    #only returns db after inited first time
    def getDB(self, _global= False, _callbackFetch= None, _init= False):
        cWin= sublime.active_window()
        if not cWin:
            return False

        curRoot= ''
        curName= ''

        if not _global:
            projFolders= cWin.folders()
            if len(projFolders):
                curRoot= projFolders[0]
                curName= os.path.split(projFolders[0])[1]


        wId= cWin.id()
        if wId not in self.dbCache:
            if not _init:
                return False
            self.dbCache[wId]= TodoDb(curRoot, curName, _callbackFetch)
        else:
            self.dbCache[wId].update(curRoot, curName)

        return self.dbCache[wId]



    def exitHandler(self): # one for all, at very exit
        if len(sublime.windows())==0:
            for dbI in self.dbCache:
               self.dbCache[dbI].flush(True)


#find command viewport
    
    resultsViewCache= {} #{window.id(): view} cache


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


    def checkResultsView(self, _viewId, _wipe=False):
        cWin= sublime.active_window()
        if not cWin:
            return

        wId= sublime.active_window().id()
        if wId in self.resultsViewCache and _viewId==self.resultsViewCache[wId].buffer_id():
            if _wipe:
                del self.resultsViewCache[wId]
            return True


wCache= WCache() #hold against GC
