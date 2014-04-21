1
       Sublime plugin for taking care of 'todo' comments
1.1
       Most interaction is done by ordinary inline source code commenting,
       without any menus and special shortcuts
1.2
       When typing '//todo:' (or '#todo:' here and later in text),
       entering colon ':' will instantly expand line with arbitrary fields:
           //todo xxxx [(category)] [{+-}y]:
1.3
       and store in [projectRoot]/[projectName].todo file, used as database
1.4
       if theres no project root found then all-in-one .todo file is used
       (for me it's in [user]\AppData\Roaming\Sublime Text 2\Packages\User\)
1.5
       futher edition of exitsing '//todo xxxx:' comment will flush it to db as well


2
       //todo comment field added and used are:
2.1
       xxxx would be sequental number, unique within project
2.2
       (category) is reused category name, or 'blank' default
2.3
       {+-}y is importance level. Just signed (always) integer number for addition
2.4
       comment is any text till end of line


-3
       db format is defined by first line of .todo file.
       To change format, edit that first line.
       Defaults are taken from from environment, if present

3.1
       line= any except of other defined formats.
       Full file format, holds:
           'done' state
           category
           id
           importance
           creator username
           creation stamp
           source file name where //todo was typed
           editor username
           edition stamp
           comment, at second line
-3.2
       line= '#breef'
       Breef file format, holds:
           'done' state
           category
           id
           comment, on same line
-3.3
       first line= '#sql server scheme username pass'
       connection to sql db with same data


4
       Creation of //todo: and any changes to //todo xxxx: are saved to db instantly
4.1
       parsing not allowed for more than ONE cursor present
4.2
       NO braces/hyphens checking is performed
4.3
       Typing ':' is used as new todo trigger to avoid triggering on undo/redo/paste
4.4
       category and level is reused in subsequent new todo's
4.5
       changing //todo... to //+todo... (adding '+' sign) changes 'done' state in db
       and wipes that comment of the code
-4.6
       todo can be created and edited in the middle of string.


5         --> WARNINGs and issues <--

5.1    as NO (no) consistency checking is performed
       between db and source files with //todo comments,
       any //todo editing except of that in source files with sublime
       will easily make things inconsistent and unpredictable

5.2    All changes to comment are flushed to db instantly and implicitly
       as they typed. Reload file without save will result in inconsistence.
       This behavior will remain till synchronizing FROM db will be done

5.3    creating //todo n: by defining n explicitly will overwrite some other //todo

todo 1: consistency check and both sides editing - db to source
todo 2: normal db storage

ideas:
  make other accepted forms of #todo
