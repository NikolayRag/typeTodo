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




    def findTodoInViews(self, _id, _isTag= False):
        resView= WCache().getResultsView(False)

        matches= []
        for cView in sublime.active_window().views():
            if resView and cView.buffer_id()==resView.buffer_id():
                continue
            if cView.name() == 'Find Results':
                continue

            cName= cView.file_name()
            if not cName:
                cName= '"' +cView.name() +'"'

            lNum= 0
            for cLine in cView.lines(sublime.Region(0,cView.size())):
                lNum+= 1
                foundIncode= RE_TODO_EXISTING.match(cView.substr(cLine))
                if foundIncode:
                    if not _isTag:
                        if foundIncode.group('id')==_id:
                            matches.append((cView, lNum-1, foundIncode.end('prefix'), cView.substr(cLine), foundIncode, cName))
                    else:
                        for cTag in foundIncode.group('tags').lower().split(','):
                            tagFound= False
                            for cId in _id.split(','):
                                try:
                                    if re.search(cId.strip(), cTag.strip()):
                                        matches.append((cView, lNum-1, foundIncode.end('prefix'), cView.substr(cLine), foundIncode, cName))
                                        tagFound= True
                                        break
                                except:
                                    None

                            if tagFound:
                                break


        return matches



    def findTodoInFile(self, _fn, _test, _id, _isTag= False):
        matches= []

        foundEntry= None
        lNum= 0
        try:
            with codecs.open(_fn, 'r', 'UTF-8') as f:
                for ln in f:
                    ln= ln.strip()
                    lNum+= 1
                    foundEntry= _test.match(ln)
                    if foundEntry:
                        if not _isTag:
                            if foundEntry.group('id')==_id:
                                matches.append((None, lNum-1, foundEntry.end('prefix'), ln, foundEntry, _fn))
                        else:
                            for cTag in foundEntry.group('tags').lower().split(','):
                                tagFound= False
                                for cId in _id.split(','):
                                    try:
                                        if re.search(cId.strip(), cTag.strip()):
                                            matches.append((None, lNum-1, foundEntry.end('prefix'), ln, foundEntry, _fn))
                                            tagFound= True
                                            break
                                    except:
                                        None
                                
                                if tagFound:
                                    break

 
        except Exception as e:
            None

        return matches



    def isKnownFile(self, _fn, _masksA):
        fName= os.path.basename(_fn)

        for cMask in _masksA:
            if fnmatch.fnmatch(fName, cMask):
                return True


    def findTodoInProject(self, _id, _isTag= False):
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

                    matches.extend(self.findTodoInFile(fn, RE_TODO_EXISTING, _id, _isTag))

        return matches



    jumpList= []

    def jumpFromList (self, _idx):
        self.focusView(self.view, self.jumpList[_idx][1], self.jumpList[_idx][2])


    def currentViewList (self, _matchesView):
        cViewMatches= []
        for cMatch in _matchesView:
            if cMatch[0].buffer_id()==self.view.buffer_id():
                cViewMatches.append(cMatch)

        #one found
        if len(cViewMatches) == 1:
            self.focusView(self.view, cViewMatches[0][1], cViewMatches[0][2])

        #many found, list
        if len(cViewMatches)>1:

            self.jumpList= []
            viewTodoList= []

            for cMatch in cViewMatches:
                self.jumpList.append(cMatch)
                
                cId= ' '*(7-len(cMatch[4].group('id'))) +cMatch[4].group('id')
                cEnding= ''
                if cMatch[4].group('postfix')>65:
                    cEnding= '...'
                viewTodoList.append(cId +':' +cMatch[4].group('postfix')[0:65] +cEnding)
            self.view.window().show_quick_panel(viewTodoList, self.jumpFromList, sublime.MONOSPACE_FONT)


#=todo 1309 (command, feature) +0: allow 'exclude' search by prefixing with '-'
    def findNamed(self, _text= ''):
        if _text=='*':
            _text='.*'

        isTag= not re.match('^\d+$', _text)


        matchesView= self.findTodoInViews(_text.lower(), isTag)
        
        if _text=='':
            self.currentViewList(matchesView)
            return

        matchesFiles= self.findTodoInProject(_text.lower(), isTag)

        #exclude duplicated filenames from file matches
        matches= list(matchesView)
        for cMatch in matchesFiles:
            matchDup= False
            for testMatch in matchesView:
                if testMatch[5] == cMatch[5]:
                    matchDup= True
                    break
            
            if not matchDup:
                matches.append(cMatch)


        if not len(matches):
            markName= '#' +_text
            if isTag: 
                markName= 'tagged "' +_text +'"'
            
            sublime.message_dialog('TypeTodo error:\n\n\tDoplet ' +markName +' was not found in source')


        #one found
        if len(matches) == 1:
            cView= matches[0][0]
            if not cView:
                cView= sublime.active_window().open_file(matches[0][5], sublime.TRANSIENT)
            self.focusView(cView, matches[0][1], matches[0][2])

        #many found
        if len(matches)>1:
            self.listTodos(_text, matches)





    def run(self, _edit):
        todoRegion = self.view.line(self.view.sel()[0])

        #jump by doplet's id - to .d or from Search results
        todoIncode= RE_TODO_EXISTING.match(self.view.substr(todoRegion))
        if todoIncode:

            # jump from Search results
            foundView= WCache().getResultsView(False)
            if foundView and foundView.buffer_id()==self.view.buffer_id():
                self.findNamed(todoIncode.group('id'))
                return

            cDb= WCache().getDB()
            fn= cDb.config.settings[0].file
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
