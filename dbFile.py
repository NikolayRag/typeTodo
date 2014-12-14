# coding= utf-8

import re, os, time, codecs, sys

if sys.version < '3':
    from db import *
else:
    from .db import *

class TodoDbFile():
    dbOk= True

    todoA= None
    projectName= ''
    cfgString= ''

    #db related
    reTodoParse= re.compile('^([+-])(.*) (\d+): ([+-]\d+) (.+) (\d\d/\d\d/\d\d \d\d:\d\d) \"(.*)\" (.+) (\d\d/\d\d/\d\d \d\d:\d\d)$')
    reCommentParse= re.compile('^\t(.*)$')

    projectFname= ''
    maxId= 0


    def __init__(self, _todoA, _uname, _name, _fname, _cfgStr):
        self.todoA= _todoA
        self.projectName= _name
        self.projectFname= _fname
        self.cfgString= _cfgStr

        #{id: TodoTask()}
        self.fetch() #file mode flushes entire db every time, so it must init with full shot
        self.flush()




#public#


    def flush(self):
        if not self.dbOk:
            print("TypeTodo: 'file' db was not properly inited. Disabled.")

            return False

        try:
            with codecs.open(self.projectFname, 'w+', 'UTF-8') as f:
                f.write(self.cfgString)
                f.write("\n")

                for iT in self.todoA:
                    curTodo= self.todoA[iT]
                    self.maxId= max(self.maxId, curTodo.id)

                    stateSign= '-'
                    if curTodo.state: stateSign= '+'

                    if not curTodo.cat: curTodo.cat= ''


                    curTodo.lvl= int(curTodo.lvl)
                    if curTodo.lvl>=0: curTodo.lvl= '+' +str(curTodo.lvl)

                    f.write(stateSign +curTodo.cat +' ' +str(curTodo.id)+ ': ' +' '.join([str(curTodo.lvl), curTodo.creator, curTodo.cStamp, '"'+curTodo.fileName+'"', curTodo.editor, curTodo.stamp]) +"\n\t" +curTodo.comment +"\n\n")

            return True

        except:
            print("TypeTodo: 'file' db experienced error while flushing")

            return False


    def newId(self):
        self.maxId+= 1
        return self.maxId


    def fetch(self, _id=False):
        try:
            with codecs.open(self.projectFname, 'r', 'UTF-8') as f:
                ctxTodo= None
                for ln in f:
                    ln= ln.splitlines()[0]
                    matchParse= self.reTodoParse.match(ln)
                    if matchParse:
                        __id= int(matchParse.group(3))

                        if _id and _id!=__id: #pick one
                            continue

                        if __id not in self.todoA:
                            self.todoA[__id]= TodoTask(__id, self.projectName, matchParse.group(5), matchParse.group(6))
                        ctxTodo= matchParse

                        self.maxId= max(self.maxId, __id)
                        continue

                    if ctxTodo:
                        __state= False
                        if ctxTodo.group(1)=='+': __state= True
                        matchComment= self.reCommentParse.match(ln)
                        self.todoA[int(ctxTodo.group(3))].set(__state, ctxTodo.group(2), int(ctxTodo.group(4)), ctxTodo.group(7), matchComment.group(1), ctxTodo.group(8), ctxTodo.group(9))
                        ctxTodo= None
        except:
            self.dbOk= False
            return False

        return True
