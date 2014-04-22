typeTodo
========


###1. Key features

1.1.
       Sublime plugin, taking care of TODO comments within source code.

1.2.
       TypeTodo stores and updates TODO within external per-project database.

1.3.
       Most interaction is done by ordinary inline source code commenting,
       without any menus and special shortcuts. Just type and don't look aside.


###2. TODO creation and editing

2.1.
       As colon ':' is typed after ``//todo:`` (or ``#todo:`` here and later) comment,
       line is instantly expanded with additional fields in form of:
       ``//todo XXXX [(category)] [+|-N]: ``

2.2.
       and stored in *[projectRoot]/[projectName].todo* file, used as database by default,
       where [projectRoot] is first upstream folder with * *.sublime-project* found.

2.3.
       If theres no * *.sublime-project* found then all-in-one *.todo* file is used.
       (for win7 it's stored in *[user]\AppData\Roaming\Sublime Text 2\Packages\User\*)

2.4.
       Further edition of existing TODO comment will flush it to db as well, using XXXX as id.

2.5.
       Changing ``//todo...`` to ``//+todo...`` (adding '+' sign) changes 'done' state in db
       and wipes that comment of the code.


###3. TODO comment fields

3.1.
       TODO is a comment in form of ``//todo XXXX [(category)] [+|-N]: comment`` with following fields:

* XXXX
       - **mandatory**
       - would be sequential number, unique within project
* (category)
       - *optional*
       - default: 'blank'
       - category name used as major tag name.
       - When you rename it, new name will be reused with next new TODO
* +|-N
       - *optional*
       - default: +0
       - importance level. Just signed (always) integer number for addition.
       - If changed, new value will be reused with next new TODO 
* comment
       - comment is any remaining text till the end of line


###4. .todo database and config file

4.1.
       *[projectName].todo* file is both configuration and storage database.

4.2.
       It is stored in first upstream folder with * *.sublime-project* found, if searched from current file's path.
       If no project is found, *[sublimePackage]/user* folder us used.

4.3. **in progress**
       ~~First line always configures database itself.~~

4.4. **reserved**
       ~~If configuration omit, defaults are taken from environment variables.~~

4.5. **in progress**
       ~~If nothing else specified,~~ database is stored within [projectname].todo file itself.
       Each todo have form of
~~~
+|-category XXXX: [+|-N] creatorName creationStamp filename editorName editionStamp
       comment
~~~
using  following fields:

* +|-
       - 'done' state. '-' indicates open task, '+' - closed
* category
       - that category tag name from TODO comment format 
* XXXX
       - task integer id, unique within project
* +|-N
       - importance, arbitrary signed integer number
* creatorName
       - name of user which created task, is taken from environment variable
* creationStamp
       - date and time task was created. Using **dd/mm/yy hh:mm** format
* filename
       - file at which task was created. If *.sublime-project is found, relative path is stored.
* editorName
       - name of user which edited task last, is taken from environment variable
* editionStamp
       - date and time task was edited last. Using **dd/mm/yy hh:mm** format
* comment, *at second line*
       - arbitrary text

4.6. *in progress*
       ~~breef .todo format~~

4.7. *in progress*
       ~~external db connection~~


###5. Meaningful issues

5.1.
       As TODO is created or edited, any changes are saved to db instantly.

5.2.
       If more than ONE cursor present, nothing is saved to db as typed.

5.3.
       NO braces/hyphens checking is performed

##6.         --> WARNING<--

6.1.
       as NO (no) consistency checking is performed
       between db and source files with ``//todo`` comments,
       any ``//todo`` editing except of that in source files with sublime
       will easily make things inconsistent and unpredictable

6.2.
       All changes to comment are flushed to db instantly and implicitly
       as they typed. Reload file without save will result in inconsistence.
       This behavior will remain till synchronizing FROM db will be done

6.3.
       creating ``//todo XXXX:`` by defining XXXX explicitly will overwrite some other TODO

