


class TodoTask():
    #static, defined at creation
    id= 0
    project= ''
    creator= ''

    cStamp= False #used only for dbFile; unix time

    #updatable
    state= ''
    cat= ''
    lvl= ''
    fileName= ''
    comment= ''
    editor= ''
    stamp= False # unix time
    version= 1

    parentDb= False #used to set saved[] state per db engine
    savedA= {} #[DBId]= state; cleared at reseting db's

    def __init__(self, _id, _project, _creator, _stamp, _parentDB):
        self.id= _id
        self.project= _project
        self.creator= _creator
        self.cStamp= _stamp

        self.savedA= {}
        self.parentDb= _parentDB
        
        self.setSaved(True)

    def set(self, _state, _cat, _lvl, _fileName, _comment, _editor, _stamp):
        self.setSaved(False)

        self.state= _state
        self.cat= _cat or ''
        self.lvl= int(_lvl) or 0
        self.fileName= _fileName or ''
        self.comment= _comment
        self.editor= _editor
        self.stamp= _stamp

    def setSaved(self, _state=True, _engine=-1):
        #'file' (0) indicates it is initial; dont set True at flush to save bulk every time after first .set()
        if _state==True and _engine==0: #skip explicit 'file'->True; #todo 209 (db) -10: make .savedA[] for file treated as for other engines
            return True

        if _engine<0: #set all
            for dbEN in self.parentDb.dbA:
                self.savedA[dbEN]= _state
        else:
            self.savedA[_engine]= _state
        return True
