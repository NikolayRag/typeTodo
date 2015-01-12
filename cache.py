# coding= utf-8

import sublime, sublime_plugin
import sys, os

if sys.version < '3':
    from db import *
else:
    from .db import *



#todo 65 (code) -1: make class for db cache
#{projectFolder: TodoDb} cache
projectDbCache= {}

def exitHandler(): # one for all, at very exit
    if len(sublime.windows())==0:
        for dbI in projectDbCache:
           projectDbCache[dbI].flush()

def getDB(_view=False, _folder=False):
#todo 74 (db) -1: make better caching of projectDbCache
#    if _view.TTDB: return _view.TTDB
#todo 46 (assure) +0: is .window() a sufficient condition?
    curRoot= ''
    curName= ''

    if _folder!=False:
        firstFolderA=(_folder,)
    elif _view!=False and _view.window():
        firstFolderA= _view.window().folders()
    else:
        return False

    if len(firstFolderA) and (firstFolderA[0] != ''):
        curRoot= firstFolderA[0]
        curName= os.path.split(firstFolderA[0])[1]

    #cache time
    if curRoot not in projectDbCache:
        projectDbCache[curRoot]= TodoDb(curRoot, curName)
    else:
        projectDbCache[curRoot].update(curRoot, curName)

#    _view.TTDB= projectDbCache[curRoot]
    return projectDbCache[curRoot]

