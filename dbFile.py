# coding= utf-8

import re, os, time, codecs, sys

if sys.version < '3':
    from task import *
else:
    from .task import *

class TodoDbFile():
    name= 'File'

    dbOk= True
    cfgString= ''

    #db related
    reTodoParse= re.compile('^([+-])(.*) (\d+): ([+-]\d+) (.+) (\d\d/\d\d/\d\d \d\d:\d\d) \"(.*)\" (.+) (\d\d/\d\d/\d\d \d\d:\d\d)$')
    reCommentParse= re.compile('^\t?(.*)$')

    projectFname= ''
    maxId= 0

    parentDB= False

    def __init__(self, _cfg, _parentDB):
        self.projectFname= _cfg['file']
        self.cfgString= _cfg['header']

        self.parentDB= _parentDB


#public#


    def flush(self, _dbN):
        if not self.dbOk:
            print("TypeTodo: 'file' db was not properly inited. Saving disabled.")

            return False

        try:
            with codecs.open(self.projectFname, 'w+', 'UTF-8') as f:
                f.write(self.cfgString)
                f.write("\n")

                for iT in self.parentDB.todoA:
                    curTodo= self.parentDB.todoA[iT]
                    if curTodo.savedA[_dbN]: #stands for 'if just inited'
                        continue

                    self.maxId= max(self.maxId, curTodo.id)

                    stateSign= '-'
                    if curTodo.state: stateSign= '+'

                    lvl= curTodo.lvl
                    if curTodo.lvl>=0: lvl= '+' +str(curTodo.lvl)

                    #runtime GMT time to local
                    gmtCtime= time.localtime(curTodo.cStamp)
                    gmtTime= time.localtime(curTodo.stamp)

                    f.write(stateSign +curTodo.cat +' ' +str(curTodo.id)+ ': ' +' '.join([str(lvl), curTodo.creator, time.strftime('%y/%m/%d %H:%M', gmtCtime), '"'+curTodo.fileName+'"', curTodo.editor, time.strftime('%y/%m/%d %H:%M', gmtTime)]) +"\n\t" +curTodo.comment +"\n\n")

            return True

        except:
            print("TypeTodo: 'file' db experienced error while flushing")

            return False


    def newId(self):
        self.maxId+= 1
        return self.maxId


    def fetch(self, _id=False):
        try:
            todoA= {}
            with codecs.open(self.projectFname, 'r', 'UTF-8') as f:
                ctxTodo= None
                for ln in f:
                    ln= ln.splitlines()[0]
                    matchParse= self.reTodoParse.match(ln)
                    if matchParse:
                        __id= int(matchParse.group(3))

                        if _id and _id!=__id: #pick one
                            continue

                        #file holds local time, need to convert to GMT for runtime
                        gmtCtime= time.mktime (time.strptime(matchParse.group(6), '%y/%m/%d %H:%M'))
                        gmtTime= time.mktime (time.strptime(matchParse.group(9), '%y/%m/%d %H:%M'))

                        if __id not in todoA:
                            todoA[__id]= TodoTask(__id, self.parentDB.projectName, matchParse.group(5), gmtCtime, self.parentDB)
                        ctxTodo= matchParse

                        self.maxId= max(self.maxId, __id)
                        continue

                    if ctxTodo:
                        __state= False
                        if ctxTodo.group(1)=='+': __state= True
                        matchComment= self.reCommentParse.match(ln)
                        todoA[int(ctxTodo.group(3))].set(__state, ctxTodo.group(2), int(ctxTodo.group(4)), ctxTodo.group(7), matchComment.group(1), ctxTodo.group(8), gmtTime)
                        ctxTodo= None
            return todoA

        except:
            self.dbOk= False
            return False
