# coding= utf-8

import sublime, sublime_plugin
import sys, os

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


#todo 566 (command) +0: make jump-to-result in todo search results window
    def listTodos(self, _for, _matches):
        resView= WCache().getResultsView()

        textAppend= 'Search doplets for "' +_for +'":\n\n'

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
                        for cTag in foundIncode.group('tags').split(','):
                            for cId in _id.split(','):
                                try:
                                    if re.search(cId.strip(), cTag.strip()):
                                        matches.append((cView, lNum-1, foundIncode.end('prefix'), cView.substr(cLine), foundIncode, cName))
                                except:
                                    None

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
                            for cTag in foundEntry.group('tags').split(','):
                                for cId in _id.split(','):
                                    try:
                                        if re.search(cId.strip(), cTag.strip()):
                                            matches.append((None, lNum-1, foundEntry.end('prefix'), ln, foundEntry, _fn))
                                    except:
                                        None
 
        except Exception as e:
            None

        return matches



    def isKnownFileExt(self, _fn):
        fName, fExt= os.path.splitext(_fn)
        for cExt in SKIP_SEARCH_FILES:
            if cExt==fExt:
                return True

    def findTodoInProject(self, _id, _isTag= False):
        matches= []
        for cFolder in sublime.active_window().folders():
            for cWalk in os.walk(cFolder):
                for cFile in cWalk[2]:
                    if self.isKnownFileExt(cFile):
                        continue
                    print(cFile)
                    fn= os.path.join(cWalk[0], cFile)
                    matches.extend(self.findTodoInFile(fn, RE_TODO_EXISTING, _id, _isTag))

        return matches



#todo 577 (command) +0: entering blank string for search gives list of view's doplets
    def findNamed(self, _text= ''):
        if _text=='' or _text=='*':
            return

        isTag= not re.match('^\d+$', _text)

        markName= '#' +_text
        if isTag: 
            markName= 'tagged "' +_text +'"'


        matchesView= self.findTodoInViews(_text, isTag)
        matchesFiles= self.findTodoInProject(_text, isTag)

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
            sublime.message_dialog('TypeTodo error:\n\tDoplet ' +markName +' was not found in source')

        if len(matches) == 1:
            cView= matches[0][0]
            if not cView:
                cView= sublime.active_window().open_file(matches[0][5], sublime.TRANSIENT)
            self.focusView(cView, matches[0][1], matches[0][2])

        if len(matches)>1:
            self.listTodos(_text, matches)




    def run(self, _edit):
        todoRegion = self.view.line(self.view.sel()[0])

        #jump to .do file
        todoIncode= RE_TODO_EXISTING.match(self.view.substr(todoRegion))
        if todoIncode:
            cDb= WCache().getDB()
            fn= cDb.config.settings[0].file
            if not os.path.isfile(fn):
                sublime.message_dialog('TypeTodo error:\n\tCannot find projects .do file')
                return

            matches= self.findTodoInFile(fn, RE_TODO_STORED, todoIncode.group('id'))
            if matches:
                cView= sublime.active_window().open_file(matches[0][5], sublime.TRANSIENT)
                self.focusView(cView, matches[0][1], matches[0][2]) #dont want do deal with multi-matches here, use first

            else:
                sublime.message_dialog('TypeTodo error:\n\tDoplet #' +todoIncode.group('id') +' not found in project\'s .do')

            return


        #jump to code
        todoIndo= RE_TODO_STORED.match(self.view.substr(todoRegion))
        if todoIndo:
            self.findNamed(todoIndo.group('id'))
            return

        #search by string
        sublime.active_window().show_input_panel('TypeTodo search for:', '', self.findNamed, None, None)
