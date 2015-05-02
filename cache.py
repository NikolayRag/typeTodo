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



#=todo 701 (db) +0: change cache key to window.id()
#{projectFolder: TodoDb} cache
    dbCache= {}

    def getDB(self, _global= False):
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

        #cache time
        wId= cWin.id()
        if wId not in self.dbCache:
            self.dbCache[wId]= TodoDb(curRoot, curName)
        else:
            self.dbCache[wId].update(curRoot, curName)

        return self.dbCache[wId]



    def exitHandler(self): # one for all, at very exit
        if len(sublime.windows())==0:
            for dbI in self.dbCache:
               self.dbCache[dbI].flush(True)
