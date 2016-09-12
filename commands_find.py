# coding= utf-8

import sublime, sublime_plugin
import sys, os, fnmatch

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



#todo 1859 (command, find, fix, uncertain) -1: sometimes 'search' dont show results if view is previously closed
class TypetodoJumpCommand(sublime_plugin.TextCommand):
    def focusView(self, _view, _line, _col):
        sublime.active_window().focus_view(_view)
        sublime.set_timeout(lambda: _view.run_command('typetodo_jump_point', {'_line': _line, '_col': _col}), 100)



    def listTodos(self, _for, _matches):
        resView= WCache().getResultsView()

        textAppend= 'Search doplets for "' +_for +'"\n' +str(len(_matches)) +' matches found:\n\n'

        firstLine= 0
        lastFilename= ''
        for cMatch in _matches:
            fName= ''
            if cMatch[5]:
                fName= cMatch[5]
            if lastFilename != fName:
                lastFilename= fName
                textAppend+= '\n' +fName +'\n'

            if firstLine==0:
                firstLine= resView.rowcol(resView.size())
            lNum= str(cMatch[1]+1)
            textAppend+= ' '*(6-len(lNum)) +lNum +': ' +cMatch[3][len(cMatch[4].group('prefix')):] +'\n'

        resView.set_read_only(False)
        resView.run_command('typetodo_reg_replace', {'_regStart': resView.size(), '_regEnd': resView.size(), '_replaceWith': textAppend +'\n\n'})
        resView.set_read_only(True)

        self.focusView(resView, firstLine[0]+4, 0)




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
                matches.append((_view, lNum-1, foundRe.end('prefix'), ln, foundRe, cName))

        return matches


    def findTodoInViews(self, _id, _view=False):
        if _view:
            return self.findTodoInView(_id, _view)

        matches= []
        for cView in sublime.active_window().views():
            matches+= self.findTodoInView(_id, cView)

        return matches



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
                        matches.append((None, lNum-1, foundRe.end('prefix'), ln, foundRe, _fn))

 
        except Exception as e:
            None

        return matches



    def isKnownFile(self, _fn, _masksA):
        fName= os.path.basename(_fn)

        for cMask in _masksA:
            if fnmatch.fnmatch(fName, cMask):
                return True


    def findTodoInProject(self, _id):
        skipDirs= SKIP_SEARCH_DIR +self.view.settings().get('folder_exclude_patterns')
        skipFiles= (SKIP_SEARCH_FILES
            +self.view.settings().get('file_exclude_patterns')
            +self.view.settings().get('binary_file_patterns')
        )

        matches= []
        for cFolder in sublime.active_window().folders():
            skipFolder= ''
            for cWalk in os.walk(cFolder):
                #skip entire branch
                if skipFolder!='' and os.path.relpath(cWalk[0], skipFolder).split('\\')[0]!='..':
                    continue

                if self.isKnownFile(cWalk[0], skipDirs):
                    skipFolder= cWalk[0]
                    continue

                for cFile in cWalk[2]:
                    if self.isKnownFile(cFile, skipFiles):
                        continue

                    fn= os.path.join(cWalk[0], cFile)

                    if os.path.getsize(fn)>SKIP_SEARCH_SIZE:
                        continue

                    matches.extend(self.findTodoInFile(fn, RE_TODO_EXISTING, _id))

        return matches



    jumpList= []


    def jumpFromList (self, _idx):
        if _idx!=-1:
            self.focusView(self.view, self.jumpList[_idx][1], self.jumpList[_idx][2])


    def currentViewList (self):
        matches= self.findTodoInView('', self.view)

        #one found
        if len(matches) == 1:
            self.focusView(self.view, matches[0][1], matches[0][2])

        #many found, list
        if len(matches)>1:

            self.jumpList= []
            viewTodoList= []

            for cMatch in matches:
                self.jumpList.append(cMatch)
                
                cId= ' '*(7-len(cMatch[4].group('id'))) +cMatch[4].group('id')
                cEnding= ''
                if len(cMatch[4].group('postfix'))>65:
                    cEnding= '...'
                viewTodoList.append(cId +':' +cMatch[4].group('postfix')[0:65] +cEnding)
            self.view.window().show_quick_panel(viewTodoList, self.jumpFromList, sublime.MONOSPACE_FONT)



    def findNamed(self, _text= ''):
        if _text=='*':
            _text='.*'


        if _text=='':
            self.currentViewList()
            return

        matches= self.findTodoInViews(_text.lower())
        
        matchesFiles= self.findTodoInProject(_text.lower())

        #exclude duplicated filenames from file matches
        for cMatch in matchesFiles:
            matchDup= False
            for testMatch in matches:
                if testMatch[5] == cMatch[5]:
                    matchDup= True
                    break
            
            if not matchDup:
                matches.append(cMatch)



        isId= re.match('^\d+$', _text)
        if not len(matches):
            markName= '#' +_text
            if not isId: 
                markName= 'tagged "' +_text +'"'
            
            sublime.message_dialog('TypeTodo error:\n\n\tDoplet ' +markName +' was not found in source')
            return


        #many found or tag search
        if not isId or len(matches)>1:
            self.listTodos(_text, matches)
            return

        #one found, jump instantly
        cView= matches[0][0]
        if not cView:
            cView= sublime.active_window().open_file(matches[0][5], sublime.TRANSIENT)
        self.focusView(cView, matches[0][1], matches[0][2])





    def run(self, _edit):
        todoRegion = self.view.line(self.view.sel()[0])

        #jump by doplet's id - to .do or from Search results
        todoIncode= RE_TODO_EXISTING.match(self.view.substr(todoRegion))
        if todoIncode:

            # jump from Search results
            foundView= WCache().getResultsView(False)
            if foundView and foundView.buffer_id()==self.view.buffer_id():
                jumpLine= re.match('\s*(\d+):', self.view.substr(todoRegion))
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

                cView= sublime.active_window().open_file(jumpFile, sublime.TRANSIENT)
                self.focusView(cView, jumpLine-1, 0)
#todo 1978 (command, find, fix) +0: use explicit view search if no file found
                return

            # jump from code to .do
            cDb= WCache().getDB()
            fn= ''
            for cSetting in cDb.config.settings:
                if cSetting.engine=='file':
                    fn= cSetting.file
                    break

            if not os.path.isfile(fn):
                sublime.message_dialog('TypeTodo error:\n\n\tCannot find projects .do file')
                return

            matches= self.findTodoInFile(fn, RE_TODO_STORED, todoIncode.group('id'))
            if matches:
                cView= sublime.active_window().open_file(matches[0][5], sublime.TRANSIENT)
                self.focusView(cView, matches[0][1], matches[0][2]) #dont want do deal with multi-matches here, use first

            else:
                sublime.message_dialog('TypeTodo error:\n\n\tDoplet #' +todoIncode.group('id') +' not found in project\'s .do')

            return


        #jump from .do to code
        todoIndo= RE_TODO_STORED.match(self.view.substr(todoRegion))
        if todoIndo:
            self.findNamed(todoIndo.group('id'))
            return

        #search by string
        sublime.active_window().show_input_panel('TypeTodo search for:', '', self.findNamed, None, None)
