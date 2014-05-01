# coding= utf-8

import re, os, time, codecs

class TodoDbFile():
    todoA= None
    projectName= ''
    userName= ''
    cfgString= ''

    #db related
    reTodoParse= re.compile('^([+-])(.*) (\d+): ([+-]\d+) (.+) (\d\d/\d\d/\d\d \d\d:\d\d) \"(.*)\" (.+) (\d\d/\d\d/\d\d \d\d:\d\d)$')
    reCommentParse= re.compile('^\t(.*)$')

    projectFname= ''
    maxId= 0


    def __init__(self, _todoA, _uname, _name, _fname, _cfgStr):
        self.todoA= _todoA
        self.userName= _uname
        self.projectName= _name
        self.projectFname= _fname
        self.cfgString= _cfgStr

        #{id: TodoFileTask()}

        self.fetch()


    def fetch(self):
        with codecs.open(self.projectFname, 'r', 'UTF-8') as f:
            ctxTodo= None
            for ln in f:
                ln= ln.splitlines()[0]
                matchParse= self.reTodoParse.match(ln)
                if matchParse:
                    __id= int(matchParse.group(3))
                    if __id not in self.todoA:
                        self.todoA[__id]= TodoFileTask(__id, self.projectName, matchParse.group(5), matchParse.group(6))
                    ctxTodo= matchParse

                    self.maxId= max(self.maxId, __id)
                    continue

                if ctxTodo:
                    __state= False
                    if ctxTodo.group(1)=='+': __state= True
                    matchComment= self.reCommentParse.match(ln)
                    self.todoA[int(ctxTodo.group(3))].set(__state, ctxTodo.group(2), int(ctxTodo.group(4)), ctxTodo.group(7), matchComment.group(1), ctxTodo.group(8), ctxTodo.group(9))
                    ctxTodo= None



    def flush(self):
        with codecs.open(self.projectFname, 'w+', 'UTF-8') as f:
            f.write(self.cfgString)
            f.write("\n")

            for iT in self.todoA:
                curTodo= self.todoA[iT]

                stateSign= '-'
                if curTodo.state: stateSign= '+'

                if not curTodo.cat: curTodo.cat= ''


                curTodo.lvl= int(curTodo.lvl)
                if curTodo.lvl>=0: curTodo.lvl= '+' +str(curTodo.lvl)

                f.write(stateSign +curTodo.cat +' ' +str(curTodo.id)+ ': ' +' '.join([str(curTodo.lvl), curTodo.creator, curTodo.cStamp, '"'+curTodo.fileName+'"', curTodo.editor, curTodo.stamp]) +"\n\t" +curTodo.comment +"\n\n")


    def store(self, _id, _state, _cat, _lvl, _fileName, _comment):
        _id= int(_id)

        strStamp= time.strftime("%y/%m/%d %H:%M")

        if not _id:
            self.maxId+= 1
            _id= self.maxId
        if _id not in self.todoA:
            self.todoA[_id]= TodoFileTask(_id, self.projectName, self.userName, strStamp)

        self.todoA[_id].set(_state, _cat, _lvl, _fileName, _comment, self.userName, strStamp)
        self.flush()

        return _id





class TodoFileTask():
    #static, defined at creation
    id= 0
    project= ''
    creator= ''
    cStamp= '' #used only for dbFile

    #updatable
    state= False
    cat= ''
    lvl= ''
    fileName= ''
    comment= ''
    editor= ''
    eStamp= ''

    saved= False


    def __init__(self, _id, _project, _creator, _stamp):
        self.saved= False

        self.id= _id
        self.project= _project
        self.creator= _creator
        self.cStamp= _stamp


    def set(self, _state, _cat, _lvl, _fileName, _comment, _editor, _stamp):
        self.saved= False

        if _state != '': self.state= _state
        self.cat= _cat
        self.lvl= _lvl
        self.fileName= _fileName or ''
        self.comment= _comment
        self.editor= _editor
        self.stamp= _stamp

    def setSaved():
        self.saved= True

 
    def get(self):
        return

