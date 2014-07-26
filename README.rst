typeTodo
=========

Manage TODO comments as tasks, as they're typed anywhere in project.



.. contents::
..


1. Key features
---------------

1.1.
       TypeTodo stores and updates verbose TODO comments to external per-project database and leaves breef version inlined in the code.
       
1.2.
       Available database modes are *.do* raw text **File**, **MySQL** or **HTTP** (new in v1.4.0)

1.3.
       Most interaction is done by ordinary inline source code commenting,
       without any menus and special shortcuts. Just type and don't look aside.

1.4.
       Each TODO created is assigned ID, unique within project


2. TODO creation and editing
----------------------------

2.1.
       As colon ':' is typed after ``//todo:`` (or ``#todo:`` here and later) comment,
       line is instantly expanded with additional fields:
       ``//todo:`` expands to ``//todo XXXX (category) [+-]N:``
       
* detailed fields description found in section 3

2.2.
       and stored within user-specified database.
       Database is specified within *[projectName].do* text file which is placed right above first folder, included in project.

* database configuration is described in section 4
       
2.3.
       If at a moment there's no project used, then all-in-one *.do* file is used as a database.
       (for win7 it's stored in *[user]\\AppData\\Roaming\\Sublime Text 2\\Packages\\User\\*)

2.4.
       Further edition of existing TODO comment will flush it to db as well, using XXXX as id.

2.5.
       Changing ``//todo...`` to ``//+todo...`` (adding '+' sign) changes state to 'done' in db
       and wipes that comment of the code.


3. TODO comment fields
----------------------

3.1.
       TODO is a comment in form of ``//todo XXXX (tag) [+-]N: comment`` with following fields used:

* XXXX
       - **mandatory**
       - would be auto-generated sequential number, unique within project
* (tag)
       - *optional*
       - default: 'general'
       - When you rename it, new name will be reused with next new TODO
* [+-]N
       - *optional*
       - default: +0
       - priority level. Just signed (always) integer number for addition.
* comment
       - comment is any remaining text till the end of line


4. .do database and config file
---------------------------------

4.1.
       *[projectName].do* file is used both as configuration and storage database.

4.2.
       It is placed within the parent of first project's folder.
       That is, if first folder included in project is */stuff/project-1*, then */stuff/project-1.do* file will be used as config.
       *[projectName].do* is automatically created if none as project is loaded.

4.3.
       If there's no project in Sublime, then *[sublimePackage]/typeTodo/.do* is used.
       
4.4.
       First non-blank lines of *.do* file are used to configure database itself.
       The configuration is taken from **last** line within this block that matches supported settings.
       *.do* file is checked periodically for database configuration, and it reapplies if changed
      
4.5.
       **.do** default configuration is HTTP, using http://typetodo.com as database.

4.6.
       **FILE** mode todo uses same *.do* file as default configuration.
       *.do* file holds tasks using following format in that case:
       
``+|-category XXXX: [+|-N] creatorName creationStamp filename editorName editionStamp``

``comment``

using  following fields:

* +|-
       - 'done' state; ``-`` indicates open task, ``+`` - closed
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
       - file at which task was created. If **.sublime-project* is found, relative path is stored.
* editorName
       - name of user which edited task last, is taken from environment variable
* editionStamp
       - date and time task was edited last. Using **dd/mm/yy hh:mm** format
* comment, *at second line*
       - arbitrary text

4.7.
       **MySQL** mode is used if configuration ``mysql [host] [user] [pass] [scheme]`` line is found in *.do* config.
       [Scheme] specified MUST exist at server.
       Following tables will be created:

* projects
* categories
* files
* users
* states
* tasks

All changes done to TODO comment are accumulated and flushed with incremented version and same ID. So all changes history is saved.

4.8.
       **HTTP** mode is used if configuration ``http [host] [repository] [user] [pass]`` line is found in *.do* config.
       Repository can be **public** or **personal**.

* public repository
       - is created new at first run or can be recreated new using *TypeTodo: Reset Global config* Sublime command. It is free to read and write by everyone who knows it's name.
       - public repository is accessible at http://typetodo.com/[repname] where [repname] looks like *~exwvpaytkfs6*
* personal repository
       - have same name as registered user. It is readable by everyone (yet) but can be written only when username/pass is provided.
       
All changes done to TODO comment are accumulated and flushed with incremented version and same ID. So all changes history is saved.


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
       As NO (no) consistency checking is performed between db and source files,
       any ``//todo`` comments editing outside Sublime will easily make things inconsistent and unpredictable.
       Also all changes to comments are flushed to database without saving source file itself.
       Reload file without save will result in inconsistence.
       This behavior will remain till synchronizing back FROM database will be done

6.2.
       creating ``//todo XXXX:`` by defining XXXX explicitly will overwrite or create that specified XXXX task in database

   
