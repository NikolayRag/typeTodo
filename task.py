# coding= utf-8

import sys

if sys.version < '3':
    from c import *
else:
    from .c import *



class TodoTask():
    #static, defined at creation
    id= 0
    project= ''

    #updatable
    state= ''
    tagsA= []
    lvl= ''
    fileName= ''
    comment= ''
    editor= ''
    stamp= False # unix time
    version= 1

    parentDb= False #used to set saved[] state per db engine
    savedA= {} #[DBId]= state; cleared at reseting db's


    def __init__(self, _id, _project, _parentDB):
        self.id= _id
        self.project= _project

        self.savedA= {}
        self.parentDb= _parentDB
        
        self.setSaved(SAVE_STATES.IDLE)

    def setTags(self, _tagsA):
        self.tagsA= []
        for tagName in _tagsA: self.tagsA.append(tagName.strip())

    def set(self, _state, _tagsA, _lvl, _fileName, _comment, _editor, _stamp):
        self.setSaved(SAVE_STATES.READY)

        self.state= _state
        self.setTags(_tagsA)
        self.lvl= int(_lvl) or 0
        self.fileName= _fileName or ''
        self.comment= _comment
        self.editor= _editor
        self.stamp= _stamp

    def setSaved(self, _state, _dbIdx=-1):

        if _dbIdx<0: #set all
            self.savedA= {}
            for dbEN in self.parentDb.dbA:
                self.savedA[dbEN]= _state

            return

        #skip setting saved to hold 'file' always as full set
        if _state==SAVE_STATES.IDLE and self.parentDb.dbA[_dbIdx].settings.engine=='file': #skip explicit 'file'->IDLE; #=todo 209 (db, cleanup) -10: make .savedA[] for file treated as for other engines
            return

        self.savedA[_dbIdx]= _state
