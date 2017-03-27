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





#  todo 2167 (command, find) +0: display find results in dropdown
#  todo 2182 (command, find) +0: dropdown option to display results in view
class TypetodoFindCommand(sublime_plugin.TextCommand):
    def foundViewShow(self, _header):
        resView= WCache().getResultsView()

        textAppend= 'Search doplets for "' +_header +'"\n'

        firstLine= resView.rowcol(resView.size())

        resView.set_read_only(False)
        resView.run_command('typetodo_reg_replace', {'_regStart': resView.size(), '_regEnd': resView.size(), '_replaceWith': textAppend})
        resView.set_read_only(True)

        resView.run_command('typetodo_jump_view', {'_line': firstLine[0]})



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

        textAppend= '\n' +str(_count) +' matches found\n\n\n'

        resView.set_read_only(False)
        resView.run_command('typetodo_reg_replace', {'_regStart': resView.size(), '_regEnd': resView.size(), '_replaceWith': textAppend})
        resView.set_read_only(True)


        resView.run_command('typetodo_jump_view')




#Check if doplet within _reg matches _id
#_id can be:
#   Int for ID
#   String for TAG, ',' separated
#   String with '-' sign for excluded TAG
#
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
        fContent= []
        try:
            with codecs.open(_fn, 'r', 'UTF-8') as f:
                for ln in f:
                    if len(ln)>SKIP_SEARCH_LINESIZE:
                        ln= ''
                    fContent.append(ln.strip('\n\r'))
        except Exception as e:
            return []


        matches= []
        foundRe= None
        lNum= 0

        for ln in fContent:
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

                okFiles= set(cWalk[2])-set(skipF)
                for cFile in okFiles:
                    fn= os.path.join(cWalk[0], cFile)
                        
                    if os.path.getsize(fn)>SKIP_SEARCH_FILESIZE:
                        continue

                    matches= self.findTodoInFile(fn, RE_TODO_EXISTING, _id)
                    if matches:
                        self.matchAdd(_oldMatchA, matches)



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
            self.view.run_command('typetodo_jump_view', {'_line': self.jumpList[_idx]['row'], '_col': self.jumpList[_idx]['col']})

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



    #search by regex query
    #
    def run(self, _edit):
        sublime.active_window().show_input_panel('TypeTodo search for:', '', self.findTimer, None, None)











class TypetodoJumpCommand(sublime_plugin.TextCommand):
    def run(self, _edit):
        todoStr= self.view.substr( self.view.line(self.view.sel()[0]) )

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



        # jump from .do
        todoIndo= RE_TODO_STORED.match(todoStr)
        if todoIndo:
            self.jumpFromDo(todoIndo)




    def jumpFromDo(self, _todoRegexp):
        for cFolder in sublime.active_window().folders():
            break
        fn= os.path.join(cFolder, _todoRegexp.group('context'))

        matches= self.findTodoInFile(fn, RE_TODO_EXISTING, _todoRegexp.group('id'))
        if matches:
            cView= sublime.active_window().open_file(matches[0]['file'])
            cView.run_command('typetodo_jump_view', {'_line': matches[0]['row'], '_col': matches[0]['col']})



    def jumpToDo(self, _todoRegexp):
        cDb= WCache().getDB()
        fn= cDb.config.getSettings('file').file

        if not os.path.isfile(fn):
            sublime.message_dialog('TypeTodo error:\n\n\tCannot find projects .do file')
            return

        matches= self.findTodoInFile(fn, RE_TODO_STORED, _todoRegexp.group('id'))
        if matches:
            cView= sublime.active_window().open_file(matches[0]['file'], sublime.TRANSIENT)
            cView.run_command('typetodo_jump_view', {'_line': matches[0]['row'], '_col': matches[0]['col']})

        else:
            sublime.message_dialog('TypeTodo error:\n\n\tDoplet #' +_todoRegexp.group('id') +' not found in project\'s .do')



    def jumpFromSearch(self, _todoStr):
        #search line number in text
        jumpLine= re.match('\s*(\d+):', _todoStr)
        if not jumpLine:
            return
        jumpLine= int(jumpLine.groups()[0])


        #search filename backwards
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
            cView.run_command('typetodo_jump_view', {'_line': jumpLine-1})






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



    def findTodoInFile(self, _fn, _test, _id):
        fContent= []
        try:
            with codecs.open(_fn, 'r', 'UTF-8') as f:
                for ln in f:
                    if len(ln)>SKIP_SEARCH_LINESIZE:
                        ln= ''
                    fContent.append(ln.strip('\n\r'))
        except Exception as e:
            return []


        matches= []
        foundRe= None
        lNum= 0

        for ln in fContent:
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
 
        return matches
