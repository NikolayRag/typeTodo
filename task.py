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
    lvl= 0
    fileName= ''
    comment= ''
    editor= ''
    stamp= False # unix time


    #shadow, used to save on actual changes only
    old_state= ''
    old_tagsA= []
    old_lvl= ''
    old_fileName= ''
    old_comment= ''



    parentDb= False #used to set saved[] state per db engine
    savedA= {} #[DBId]= state; cleared at reseting db's
    initial= True

    def __init__(self, _id, _project, _parentDB):
        self.id= _id
        self.project= _project

        self.savedA= {}
        self.parentDb= _parentDB
        
        self.setSaved(SAVE_STATES.IDLE)
        self.initial= True


    def setTags(self, _tagsA):
        self.tagsA= []
        for tagName in _tagsA: self.tagsA.append(tagName.strip())

    def set(self, _state, _tagsA, _lvl, _fileName, _comment, _editor, _stamp):
        self.setSaved(SAVE_STATES.READY)

        self.state= _state or STATE_DEFAULT[0]
        self.setTags(_tagsA)
        self.lvl= int(_lvl) or 0
        self.fileName= _fileName or ''
        self.comment= _comment
        self.editor= _editor

        self.stamp= _stamp





    def savedReset(self):
        self.savedA= {}
        self.setSaved(SAVE_STATES.INIT)


    def setSaved(self, _state, _dbIdx=-1):
        self.initial= False

        if _dbIdx<0: #set all
            for _dbIdx in self.parentDb.dbA:
                self.setSavedDb(_state, _dbIdx)

        else:
            self.setSavedDb(_state, _dbIdx)


        self.shadowCast()



    def setSavedDb(self, _state, _dbIdx):
        #restrict FORCE to READY
        if _dbIdx in self.savedA and _state==SAVE_STATES.READY and self.savedA[_dbIdx]==SAVE_STATES.FORCE:
            return

        self.savedA[_dbIdx]= _state





#   Store rest state for saved (all-IDLE) only

    def shadowCast(self):
        for cSaved in self.savedA:
            if self.savedA[cSaved]!=SAVE_STATES.IDLE:
                return

        self.old_state= self.state
        self.old_tagsA= self.tagsA
        self.old_lvl= self.lvl
        self.old_fileName= self.fileName
        self.old_comment= self.comment



    def shadowDiffers(self):
        return self.differs(self.old_state, self.old_tagsA, self.old_lvl, self.old_fileName, self.old_comment)


    def taskDiffers(self, _task):
        return self.differs(_task.state, _task.tagsA, _task.lvl, _task.fileName, _task.comment)


    def differs(self, _state, _tagsA, _lvl, _fileName, _comment):
        if _state!= self.state:
            return True
        if sorted(_tagsA)!= sorted(self.tagsA):
            return True
        if _lvl!= self.lvl:
            return True
        if _fileName!= self.fileName:
            return True
        if _comment!= self.comment:
            return True





    def savePending(self, _dbIdx):
        if self.savedA[_dbIdx]==SAVE_STATES.FORCE:
            return True

        if self.savedA[_dbIdx]==SAVE_STATES.READY and self.shadowDiffers():
            return True


    def saveProgress(self, _dbIdx):
        if self.savedA[_dbIdx]==SAVE_STATES.HOLD:
            return True


    def saveInit(self, _dbIdx):
        if self.savedA[_dbIdx]==SAVE_STATES.INIT:
            return True
