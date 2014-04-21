
import sublime, sublime_plugin
import re, os, time


class TodoCommand(sublime_plugin.EventListener):
    #folder: TodoSet
    cfgA= {}

    undoMutexFree= 1
    prevTxt= ''
#todo: remove '$' for new so #todo can be placed before existing text
    reTodoNew= re.compile('^\s*((?://|#)\s*)todo:$')
    reTodoExisting= re.compile('^(?:(?://|#)\s*)([\+\-])?todo\s+(\d+)(?:\s+\((.*)\))?(?:\s+([\+\-]\d+))?\s*:\s*(.*)\s*$')
    reRootFolderFile= re.compile('(.*)\.sublime-project$')

#todo: make cached stuff per-project (or not?)
    lastCat= 'blank'
    lastLvl= '+0'


    def on_modified(self, _view):
        #more than one cursors skipped for number of reasons
        if (len(_view.sel())!=1) or (not self.undoMutexFree):
            return

        todoRegion = _view.line(_view.sel()[0])
        todoText = _view.substr(todoRegion)
#todo: need to get 'previous' string state without caching to avoid bugs when typing part of 'todo:' while changing cursor position
#in general - make triggering more clear
#use command_history()? Its also dont fit perfect
        prevCheck= self.prevTxt
        self.prevTxt= todoText

        _new = self.reTodoNew.match(todoText)
        #get the moment ':' is added to avoid triggering on undo/redo/paste
        if _new and (todoText==prevCheck+':'):
            resNew= self.substNew(_new.group(1), _view, todoRegion)
            if not resNew:
                sublime.status_message('Todo creation failed')
            return

        _mod= self.reTodoExisting.match(todoText)
        if _mod :
            resUpdate= self.substUpdate(_mod.group(1), _mod.group(2), _mod.group(3), _mod.group(4), _mod.group(5), _view, todoRegion)
            if not resUpdate:
                sublime.status_message('Todo update failed')
            return

    #create new todo in db and return string to replace original 'todo:'
    def substNew(self, _pfx, _view, _region):
        todoId= self.cfgStore(0, False, self.lastCat, self.lastLvl, _view.file_name(), '')

        todoComment= _pfx + 'todo ' +str(todoId) +' (' +self.lastCat +') ' +self.lastLvl +': '
        self.strReplace(_view, _region, todoComment)

        return todoId


    #store to db and, if changed state, remove comment
    def substUpdate(self, _state, _id, _cat, _lvl, _comment, _view, _region):
        if _cat != None:
            self.lastCat= _cat
        if _lvl != None:
            self.lastLvl= _lvl

        _state= _state=='+'
        if _state:
            self.strReplace(_view, _view.full_line(_region), '')
        _id= self.cfgStore(_id, _state, _cat, _lvl or 0, _view.file_name(), _comment)

        return _id


    def strReplace(self, _view, _region, _comment):
        self.undoMutexFree= 0
        edit= _view.begin_edit()
        _view.replace(edit, _region, _comment)
        _view.end_edit(edit)
        self.undoMutexFree= 1


    def cfgStore(self, _id, _state, _cat, _lvl, _fileName, _comment):
        for cfgRoot, projectName in [self.cfgFindRoot(_fileName)]:
            break
        if projectName != '':
            _fileName= os.path.relpath(_fileName, cfgRoot)

        if cfgRoot not in self.cfgA:
            self.cfgA[cfgRoot]= TodoSet(cfgRoot, projectName)

        return self.cfgA[cfgRoot].store(_id, _state, _cat, _lvl, _fileName, _comment)



#   return [rootFolder, projectName] for file
#   where rootFolder is first upstream folder with *.sublime-project file
#   and projectName is * nameof that file

    def cfgFindRoot(self, _fileName):
#todo: make cache and check it first
        folderNext= os.path.dirname(_fileName)
        while True:
            for folderTest in os.listdir(folderNext):
                fileTest= self.reRootFolderFile.match(folderTest)
                if fileTest and fileTest.group(1):
                    return [folderNext, fileTest.group(1)]

            folderUp= os.path.split(folderNext)[0]
            if folderUp == folderNext:
                break
            folderNext= folderUp
        #defaults if not found *.sublime-project
        return [os.path.join(sublime.packages_path(),'user'), '']









class TodoTask():
    #static, defined at creation
    id= 0
    project= ''
    creator= ''
    cStamp= ''

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
        self.id= _id
        self.project= _project
        self.creator= _creator
        self.cStamp= _stamp


    def set(self, _state, _cat, _lvl, _fileName, _comment, _editor, _stamp):
        if _state != '': self.state= _state
        self.cat= _cat
        self.lvl= _lvl
        self.fileName= _fileName
        self.comment= _comment
        self.editor= _editor
        self.stamp= _stamp


    def get(self):
        return




class TodoSet():
    projectRoot= ''
    projectName= ''
    projectCfg= ''

    strUname= '*Anon'

    #db: sql
#    dbAddr= ''
#    dbScheme= 'todos'
#    dbUname= ''
#    dbPass= ''

    #db: file
    maxId= 0
    todoA= None

    def __init__(self, _root, _name):
        self.projectRoot= _root
        self.projectName= _name
        self.projectCfg= os.path.join(self.projectRoot, self.projectName +'.todo')


        if 'USERNAME' in os.environ: self.strUname= os.environ['USERNAME']
#other day, hope it will come
#        if 'TODO_DB_ADDR' in os.environ: self.dbAddr= os.environ['TODO_DB_ADDR']
#        if 'TODO_DB_SCHEME' in os.environ: self.dbScheme= os.environ['TODO_DB_SCHEME']
#        if 'TODO_DB_UNAME' in os.environ: self.dbUname= os.environ['TODO_DB_UNAME']
#        if 'TODO_DB_PASS' in os.environ: self.dbPass= os.environ['TODO_DB_PASS']

        self.todoA= {}

        if os.path.isfile(self.projectCfg):
            self.fetch()


    def fetch(self):
        with open(self.projectCfg, 'r') as f:
#todo: read db settings
            f.readline() #db config be here
            f.readline()

            reTodoParse= re.compile('^([+-])(.*) (\d+): ([+-]\d+) (.+) (\d\d/\d\d/\d\d \d\d:\d\d) \"(.*)\" (.+) (\d\d/\d\d/\d\d \d\d:\d\d)$')
            reCommentParse= re.compile('^\t(.*)$')
            ctxTodo= None
            for ln in f:
                matchParse= reTodoParse.match(ln)
                if matchParse:
                    __id= int(matchParse.group(3))
                    if __id not in self.todoA:
                        self.todoA[__id]= TodoTask(__id, self.projectName, matchParse.group(5), matchParse.group(6))
                    ctxTodo= matchParse

                    self.maxId= max(self.maxId, __id)
                    continue

                if ctxTodo:
                    __state= False
                    if ctxTodo.group(1)=='+': __state= True
                    matchComment= reCommentParse.match(ln)
                    self.todoA[int(ctxTodo.group(3))].set(__state, ctxTodo.group(2), int(ctxTodo.group(4)), ctxTodo.group(7), matchComment.group(1), ctxTodo.group(8), ctxTodo.group(9))
                    ctxTodo= None


    def flush(self):
        with open(self.projectCfg, 'w+') as f:
            f.write("#db: file\n\n")

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
            self.todoA[_id]= TodoTask(_id, self.projectName, self.strUname, strStamp)

        self.todoA[_id].set(_state, _cat, _lvl, _fileName, _comment, self.strUname, strStamp)
        self.flush()

        return _id

