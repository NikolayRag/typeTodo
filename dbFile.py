# coding= utf-8

import re, os, time, codecs, sys

if sys.version < '3':
    from task import *
    from c import *
else:
    from .task import *
    from .c import *

class TodoDbFile():
    name= 'File'

    dbOk= True

    #db related
    reTodoParse= re.compile('^([\+\-\!\=])(.*) (\d+): ([+-]\d+) (.+) (\d\d/\d\d/\d\d \d\d:\d\d) \"(.*)\" (.+) (\d\d/\d\d/\d\d \d\d:\d\d)$')
    reCommentParse= re.compile('^\t?(.*)$')

    lastId= None
    maxId= 0

    settings= None
    parentDB= False

    def __init__(self, _parentDB, _settings):
        self.settings= _settings
        self.parentDB= _parentDB


#public#


    def flush(self, _dbN):
        if not self.dbOk:
            print("TypeTodo: 'file' db was not properly inited. Saving disabled.")

            return False

        try:
            with codecs.open(self.settings.file, 'w+', 'UTF-8') as f:
                f.write(self.settings.head)
                f.write("\n")

                for iT in sorted(self.parentDB.todoA):
                    curTodo= self.parentDB.todoA[iT]
                    if curTodo.savedA[_dbN]==SAVE_STATES.IDLE: #stands for 'if just inited'
                        continue

                    self.maxId= max(self.maxId, curTodo.id)

                    stateSign= curTodo.state
                    if stateSign=='': stateSign='-'

                    lvl= curTodo.lvl
                    if curTodo.lvl>=0: lvl= '+' +str(curTodo.lvl)

                    #runtime GMT time to local
                    gmtCtime= time.localtime(curTodo.cStamp)
                    gmtTime= time.localtime(curTodo.stamp)

                    f.write(stateSign +', '.join(curTodo.tagsA) +' ' +str(curTodo.id)+ ': ' +' '.join([str(lvl), curTodo.creator, time.strftime('%y/%m/%d %H:%M', gmtCtime), '"'+curTodo.fileName+'"', curTodo.editor, time.strftime('%y/%m/%d %H:%M', gmtTime)]) +"\n\t" +curTodo.comment +"\n\n")

            return True

        except Exception as e:
            print("TypeTodo: 'file' db experienced error while flushing")
            print(e)

            return False


    def newId(self, _wantedId=0):
        if _wantedId==self.lastId:
            return self.lastId

        self.maxId+= 1
        if _wantedId>self.maxId:
            self.maxId= _wantedId
        
        self.lastId= self.maxId
        return self.lastId


    def fetch(self, _id=False):
        if not os.path.isfile(self.settings.file):
            print("TypeTodo: 'file' db does not exist, should to be created.")
            return False


        try:
            todoA= {}
            with codecs.open(self.settings.file, 'r', 'UTF-8') as f:
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
                            todoA[__id]= TodoTask(__id, self.parentDB.config.projectName, matchParse.group(5), gmtCtime, self.parentDB)
                        ctxTodo= matchParse

                        self.maxId= max(self.maxId, __id)
                        continue

                    if ctxTodo:
                        __state= ctxTodo.group(1)
                        if ctxTodo.group(1)=='-': __state= ''
                        matchComment= self.reCommentParse.match(ln)
                        todoA[int(ctxTodo.group(3))].set(__state, ctxTodo.group(2).split(','), int(ctxTodo.group(4)), ctxTodo.group(7), matchComment.group(1), ctxTodo.group(8), gmtTime)
                        ctxTodo= None
            return todoA

        except Exception as e:
            print("TypeTodo: 'file' db experienced error while fetching")
            print(e)

            self.dbOk= False
            return False
