# coding= utf-8

import sublime, sublime_plugin
import sys, os, fnmatch
from threading import Timer

if sys.version < '3':
    from db import *
    from cache import *
    from c import *
else:
    from .db import *
    from .cache import *
    from .c import *




class TypetodoJumpPointCommand(sublime_plugin.TextCommand):
    def run(self, _edit, _line, _col):
        focusBegin= self.view.text_point(_line, _col)
        focusLine= sublime.Region(focusBegin, self.view.line(focusBegin).b)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(focusBegin, focusBegin))
        self.view.show(focusLine)



class TypetodoFindCommand(sublime_plugin.TextCommand):
    def focusView(self, _view, _line=-1, _col=-1):
        sublime.active_window().focus_view(_view)
        if _line!=-1:
            sublime.set_timeout(lambda: _view.run_command('typetodo_jump_point', {'_line': _line, '_col': _col}), 100)



    def foundViewShow(self, _for, _matches=False):
        resView= WCache().getResultsView()

        textAppend= 'Search doplets for "' +_for +'"\n'

        firstLine= resView.rowcol(resView.size())
        self.focusView(resView, firstLine[0], 0)

        resView.set_read_only(False)
        resView.run_command('typetodo_reg_replace', {'_regStart': resView.size(), '_regEnd': resView.size(), '_replaceWith': textAppend})
        resView.set_read_only(True)

        if _matches:
            self.foundViewAdd(_matches)


    def foundViewAdd(self, _matches):
        resView= WCache().getResultsView()

        textAppend= ''

        lastFilename= ''
        for cMatch in _matches:
            fName= ''
            if cMatch['file']:
                fName= cMatch['file']
            if lastFilename != fName:
                lastFilename= fName
                textAppend+= '\n' +fName +'\n'

            lNum= str(cMatch['row']+1)
            textAppend+= ' '*(6-len(lNum)) +lNum +': ' +cMatch['line'][len(cMatch['regexp'].group('prefix')):] +'\n'

        resView.set_read_only(False)
        resView.run_command('typetodo_reg_replace', {'_regStart': resView.size(), '_regEnd': resView.size(), '_replaceWith': textAppend})
        resView.set_read_only(True)


    def foundViewFinish(self, _count):
        resView= WCache().getResultsView()
        self.focusView(resView)

        textAppend= '\n' +str(_count) +' matches found\n\n\n'

        resView.set_read_only(False)
        resView.run_command('typetodo_reg_replace', {'_regStart': resView.size(), '_regEnd': resView.size(), '_replaceWith': textAppend})
        resView.set_read_only(True)




    def findTodoLine(self, _reg, _id):
        isId= re.match('^\d+$', _id)

        isExclude= False

        if len(_id) and _id[0]=='-':
            isExclude= True
            _id= _id[1:]


        if isId:
            if _reg.group('id')==_id:
                return True
        else:
            tagFound= False
            for cTag in _reg.group('tags').lower().split(','):
                for cId in _id.split(','):
                    try:
                        if re.search(cId.strip(), cTag.strip()):
                            tagFound= True
                            break
                    except:
                        None

                if tagFound:
                    break

            if tagFound!=isExclude: #invert result by exclusion
                return True



    def findTodoInView(self, _id, _view):
        resView= WCache().getResultsView(False)

        if resView and _view.buffer_id()==resView.buffer_id():
            return []
        if _view.name() == 'Find Results':
            return []

        cName= _view.file_name()
        if not cName:
            cName= '"' +_view.name() +'"'

        matches= []
        lNum= 0
        for cLine in _view.lines(sublime.Region(0,_view.size())):
            ln= _view.substr(cLine)
            lNum+= 1
            foundRe= RE_TODO_EXISTING.match(ln)
            if foundRe and self.findTodoLine(foundRe, _id):
                matches.append({
                    'row': lNum-1,
                    'col': foundRe.end('prefix'),
                    'line': ln,
                    'regexp': foundRe,
                    'file': cName
                })

        return matches


    def findTodoInViews(self, _id, _oldMatchA):
        sublime.status_message('search in views')

        for cView in sublime.active_window().views():
            self.matchAdd(_oldMatchA, self.findTodoInView(_id, cView))




    def findTodoInFile(self, _fn, _test, _id):
        matches= []

        foundRe= None
        lNum= 0
        try:
            with codecs.open(_fn, 'r', 'UTF-8') as f:
                for ln in f:
                    ln= ln.strip()
                    lNum+= 1
                    foundRe= _test.match(ln)
                    if foundRe and self.findTodoLine(foundRe, _id):
                        matches.append({
                            'row': lNum-1,
                            'col': foundRe.end('prefix'),
                            'line': ln,
                            'regexp': foundRe,
                            'file': _fn
                        })

 
        except Exception as e:
            None

        return matches




    def findTodoInProject(self, _id, _oldMatchA):
        for cFolder in sublime.active_window().folders():
            skipFolder= ''
            for cWalk in os.walk(cFolder):
                #skip dirs
                if set(cWalk[0].split('\\')).intersection(SKIP_SEARCH_DIR)!=set([]):
                    continue

                sublime.status_message('search in '+cWalk[0])


                skipF= []
                for cMask in SKIP_SEARCH_FILES:
                    for cFile in fnmatch.filter(cWalk[2], cMask):
                        skipF.append(cFile)

                for cFile in set(cWalk[2])-set(skipF):

                    fn= os.path.join(cWalk[0], cFile)
                        
                    if os.path.getsize(fn)>SKIP_SEARCH_SIZE:
                        continue

                    self.matchAdd(_oldMatchA, self.findTodoInFile(fn, RE_TODO_EXISTING, _id))


    #exclude add match to existing list
    def matchAdd (self, _oldMatchA, _newMatchA):
        passedMatchs= []

        for cMatch in _newMatchA:
            matchDup= False
            for testMatch in _oldMatchA:
                if (testMatch['file']==cMatch['file']) and (testMatch['row']==cMatch['row']):
                    matchDup= True
                    break
            
            if not matchDup:
                passedMatchs.append(cMatch)

        _oldMatchA.extend(passedMatchs)

        self.foundViewAdd(passedMatchs)



    jumpList= []


    def jumpFromList (self, _idx):
        if _idx!=-1:
            self.focusView(self.view, self.jumpList[_idx]['row'], self.jumpList[_idx]['col'])

    def currentViewList (self):
        matches= self.findTodoInView('', self.view)

        self.jumpList= []
        viewTodoList= []

        for cMatch in matches:
            self.jumpList.append(cMatch)
            
            cId= ' '*(7-len(cMatch['regexp'].group('id'))) +cMatch['regexp'].group('id')
            cEnding= ''
            if len(cMatch['regexp'].group('postfix'))>65:
                cEnding= '...'
            viewTodoList.append(cId +':' +cMatch['regexp'].group('postfix')[0:65] +cEnding)

        try:
            self.view.window().show_quick_panel(viewTodoList, self.jumpFromList, sublime.MONOSPACE_FONT)
        except:
            None


    #search is performed in thread for st3
    searchMutex= False

    def findTimer(self, _text):
        if sys.version < '3':
            self.findNamed(_text)
        else:
            Timer(0, lambda: self.findNamed(_text)).start()


    def findNamed(self, _text= ''):
        if _text=='*':
            _text='.*'

        if _text=='':
            self.currentViewList()
            return


        if self.searchMutex:
            sublime.message_dialog('TypeTodo search is in progress...')
            return
        self.searchMutex= True


        self.foundViewShow(_text)

        matches= []
        self.findTodoInViews(_text.lower(), matches)
        self.findTodoInProject(_text.lower(), matches)

        self.foundViewFinish(len(matches))


        self.searchMutex= False


    def jumpToDo(self, _todoRegexp):
        cDb= WCache().getDB()
        fn= ''
        for cSetting in cDb.config.settings:
            if cSetting.engine=='file':
                fn= cSetting.file
                break

        if not os.path.isfile(fn):
            sublime.message_dialog('TypeTodo error:\n\n\tCannot find projects .do file')
            return

        matches= self.findTodoInFile(fn, RE_TODO_STORED, _todoRegexp.group('id'))
        if matches:
            cView= sublime.active_window().open_file(matches[0]['file'], sublime.TRANSIENT)
            self.focusView(cView, matches[0]['row'], matches[0]['col']) #dont want do deal with multi-matches here, use first

        else:
            sublime.message_dialog('TypeTodo error:\n\n\tDoplet #' +_todoRegexp.group('id') +' not found in project\'s .do')



    def jumpFromSearch(self, _todoStr):
        jumpLine= re.match('\s*(\d+):', _todoStr)
        if not jumpLine:
            return
        jumpLine= int(jumpLine.groups()[0])

        tryLine= self.view.rowcol(self.view.sel()[0].a)[0] -1
        while tryLine>0:
            jumpFile= self.view.substr(self.view.line(self.view.text_point(tryLine, 0)))
            if re.match('[^\s].*[^\s]$', jumpFile):
                break

            tryLine-= 1

        if not tryLine:
            return

        cView= sublime.active_window().open_file(jumpFile)
        if cView:
            self.focusView(cView, jumpLine-1, 0)




    def run(self, _edit, _query=True):
        todoStr= self.view.substr( self.view.line(self.view.sel()[0]) )

        #jump by doplet's id - to .do or from Search results
        todoRegexp= RE_TODO_EXISTING.match(todoStr)
        if todoRegexp:

            # jump directly from Search results
            foundView= WCache().getResultsView(False)
            if foundView and foundView.buffer_id()==self.view.buffer_id():
                self.jumpFromSearch(todoStr)
                return


            # jump from code to .do
            self.jumpToDo(todoRegexp)
            return


        if not _query:
            return


        searchInitial= ''

        #init search with .do id
        todoIndo= RE_TODO_STORED.match(todoStr)
        if todoIndo:
            searchInitial= todoIndo.group('id')

        #search by string
        sublime.active_window().show_input_panel('TypeTodo search for:', searchInitial, self.findTimer, None, None)

