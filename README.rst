typeTodo
=========

Sublime plugin that holds source code TODO comments within database.



.. contents::
..


1. Key features
---------------

1.1.
       TypeTodo stores and updates verbose TODO comments to external per-project database and leaves breef version inlined in the code.
       
1.2.
       Available database modes are **.todo** raw text file and **MySQL**

1.3.
       Most interaction is done by ordinary inline source code commenting,
       without any menus and special shortcuts. Just type and don't look aside.

1.4.
       Each TODO created is assigned ID, unique within project


2. TODO creation and editing
----------------------------

2.1.
       As colon ':' is typed after ``//todo:`` (or ``#todo:`` here and later) comment,
       line is instantly expanded with additional fields in format of:
       ``//todo XXXX [(category)] [+|-N]: ``
       
* detailed fields description found in section 3

2.2.
       and stored within user-specified database.
       Database is _[projectName].todo_ raw text file which is placed right above first folder, included in project.
       OR database is specified within that _[projectName].todo_ file

* database configuration is described in section 4
       
2.3.
       If at a moment there's no project used, then all-in-one _.todo_ file is used as a database.
       (for win7 it's stored in _[user]\AppData\Roaming\Sublime Text 2\Packages\User\_)

2.4.
       Further edition of existing TODO comment will flush it to db as well, using XXXX as id.

2.5.
       Changing ``//todo...`` to ``//+todo...`` (adding '+' sign) changes state to 'done' in db
       and wipes that comment of the code.


3. TODO comment fields
----------------------

3.1.
       TODO is a comment in form of ``//todo XXXX [(category)] [+|-N]: comment`` with following fields used:

* XXXX
       - **mandatory**
       - would be auto-generated sequential number, unique within project
* (category)
       - *optional*
       - default: 'general'
       - category name is used as major tag name.
       - When you rename it, new name will be reused with next new TODO
* +|-N
       - *optional*
       - default: +0
       - importance level. Just signed (always) integer number for addition.
* comment
       - comment is any remaining text till the end of line


4. .todo database and config file
---------------------------------

4.1.
       _[projectName].todo_ file is both configuration and default storage database.

4.2.
       It is placed within the parent of first folder which is included in project.
       That is, if first folder included in project is _/stuff/z-files/sourcesA_, then database/config will be stored at _/stuff/z-files/z-files.todo_ file.
       _[projectName].todo_ is automatically created as project is loaded.

4.3.
       If theres no project in Sublime, then _[sublimePackage]/typeTodo/.todo_ is used.
       
4.4.
       First non-blank lines of _.todo_ file are used to configure database itself.
       The configuration is taken from **last** line within this block that matches supported settings.
       _.todo_ file is checked periodically for database configuration, and it reapplies if changed
      
4.5.
       **.todo** default configuration.
       If no acceptable configuration found, then database is stored within _[projectname].todo_ file itself.
       Each todo have form of

~~~
+|-category XXXX: [+|-N] creatorName creationStamp filename editorName editionStamp
       comment
~~~
using  following fields:

* +|-
       - 'done' state; '-' indicates open task, '+' - closed
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

4.6. *reserved*

4.7.
       **MySQL**.
       If configuration ``mysql [host] [user] [pass] [scheme]`` line is found (without braces), then typetodo uses that specified MySQL server to store tasks.
       [Scheme] specified MUST exist at server.
       Following tables will created:

* projects
* categories
* files
* users
* states
* tasks



5. Meaningful issues
--------------------

5.1.
       As TODO is created or edited, any changes are saved to db instantly, even if current source file is not saved.

5.2.
       If more than ONE cursor present, nothing is saved to db as typed.

5.3.
       NO braces/hyphens checking is performed. So if ``#todo:`` line is a part of multiline string, it WILL expand as typed.
       

6. --> WARNING<--
-------------------------

6.1.
       as NO (no) consistency checking is performed
       between db and source files with ``//todo`` comments,
       any ``//todo`` editing except of that in source files with sublime
       will easily make things inconsistent and unpredictable

6.2.
       All changes to comment are flushed to db instantly and implicitly
       at each keystroke typed. Reload file without save will result in inconsistence.
       This behavior will remain till synchronizing back FROM database will be done

6.3.
       creating ``//todo XXXX:`` by defining XXXX explicitly will overwrite or create that specified XXXX task in database

