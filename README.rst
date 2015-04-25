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
       Available database modes are *.do* raw text **File**, **MySQL** or **HTTP**

1.3.
       Most interaction is done by ordinary inline source code commenting,
       without any menus and special shortcuts. Just type and don't look aside.

1.4.
       Each TODO created is assigned ID, unique within project


2. TODO creation and editing
----------------------------

2.1.
       Type ``//todo:`` or ``#todo:`` according to used language.
       As colon ``:`` is typed, line is instantly expanded with snippet, having additional fields:
       ``//todo:`` expands to ``//todo XXXX (category) [+-]N:``
       
* detailed fields description found in section 3

2.2.
       ... and stored within user-specified database.
       Database is specified within *[projectName].do* text file which is placed inside the first folder, included in project.

* database configuration is described in section 4
       
2.3.
       If at a moment there's no project used, then global *.do* file is used as a database.
       (for win7 it's stored in *[user]\\AppData\\Roaming\\Sublime Text 2\\Packages\\User\\*)

2.4.
       Further edition of existing TODO comment will flush it to db as well, using XXXX as id.

2.5.
       Changing ``//todo...`` to ``//+todo...`` (adding '+' sign) changes state to 'done' in db
       and wipes that comment of the code.
       Full set of states are:
       '' - Opened TODO (default)
       '=' - TODO in progress, used for management of TODOs
       '+' - Closed TODO, wiped as set
       '!' - Canceled TODO; As set, you will be asked for reason of canceling. If specified, that reason replaces TODOs comment in database. Then TODO is wiped.


3. TODO comment fields
----------------------

3.1.
       TODO is a comment in form of ``//todo XXXX (tags) [+-]N: comment`` with following fields used:
       
* XXXX
       - **mandatory**
       - would be auto-generated sequential number, unique within project
* (tags)
       - *optional*, comma-separated list
       - default: 'general'
       - When you rename it, new name will be reused with next new TODO
* [+-]N
       - *optional*
       - default: +0
       - priority level. Just signed (always) integer number for addition.
* comment
       - comment is any remaining text till the end of line


4. .do config file and default database
---------------------------------

4.1.
       *[projectName].do* file is used both as configuration and storage database.

4.2.
       It is placed inside the first project's folder.
       That is, if first folder included in project is */project-1*, then */project-1/project-1.do* file will be used as config.
       *[projectName].do* is automatically created if none found, when project is loaded, and it's config is copied from global *.do*.

4.3.
       If there's no current project in Sublime, then *[sublimePackage]/typeTodo/.do* is used as configuration and DB itself.
       
4.4.
       First non-blank lines of *.do* file are used to configure external database.
       The configuration is taken from **last** line within this block, that matches supported settings.
       *.do* file is checked periodically for database configuration, and it reapplies on fly if changed
      
4.5.
       **.do** default configuration is external HTTP DB, using http://typetodo.com as database.

4.6.
       At **FILE** mode todo uses same *.do* file as one for default configuration.
       It is always enabled (from v1.5.0), no matter if external DB is specified or not.
       *.do* file holds tasks using following format:
       
``(+|-|=|!)tags XXXX: [+|-N] creatorName creationStamp filename editorName editionStamp``

``comment``

using  following fields:

* (+|-|=|!)
       - TODO state; ``-`` indicates open task, ``+`` - closed, ``=`` - in-progress, and ``!`` stands for canceled.
* tags
       - comma-separated tag list
* XXXX
       - task integer id, unique within project
* +|-N
       - importance, arbitrary signed integer number
* creatorName
       - name of user which created task, is taken from environment variable
* creationStamp
       - date and time task was created. Using **dd/mm/yy hh:mm** format
* filename
       - file at which task was created. If *.sublime-project* is found, relative path is stored.
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
* categories (tags)
* tag2Task
* files
* users
* states
* tasks

All changes done to TODO comment are accumulated and flushed with incremented version and same ID. So all changes history is saved.

4.8.
       **HTTP** mode is used if ``http [host] [repository]`` or ``http [host] [repository] [user] [pass]`` configuration line is found in *.do* config.
       If ``[user] [pass]`` logon credentials are specified, repository is treated as **personal**, otherwise it is **public**.
       Repository is accessible at http://typetodo.com/[repname]

* public repository
       - Is created at first run or can be recreated using *TypeTodo: Reset Global config* command. It is free to read and write by everyone who knows it's name.
       - Public repository name looks like *~exwvpaytkfs6*
* personal repository
       - Have same name as registered user. It is readable by everyone (yet) but can be written only by providing logon username and pass.
       
All changes done to TODO comment are accumulated and flushed with incremented version and same ID. So all changes history is saved.


5. Related Commands
--------------------
       
       While using of TypeTodo is completely implicit, there're some support commands and keyboard shortcuts available:

5.1.
       **Set State** (keyboard shortcut ``Alt+d``)
       This command offer list of states to change the state of current doplet. As the states count become more than just Open/Close, this command is going to be more useful.

5.2.
       **Find todo** (keyboard shortcut ``Alt+Ctrl+d``)
       Performs searching of current doplet from source in ``.do`` file and visa-versa. If cursor is not placed over doplet, text field is offered, waiting for ID to search.

5.3.
       Open Global/Project config.
       Command for opening related ``.do`` file. While **Find todo** command is presented, there's no big use of opening config too often.

5.4.
       **Browse project's repository**
       Used to open current project within HTTP repository in browser. Server and repository are defined in ``.do` config.

5.5.
       **Reset Global config**
       Reinitialise global ``.do`` config while keeping it's doplet records. Mainly reinitialisation means gathering of new public HTTP repository, while old one will remain forgotten on web-server.

5.6.
       Priority change.
       This is not a dedicated command, but a behavior, which uses ``+`` and ``-`` keys to increment or decrement doplet priority when focused over it.


6. Meaningful issues and behavior
---------------------------------

6.1.
       As TODO is created or edited, any changes are saved to db in background, even if current source file is not saved. If Sublime is closed afterall without save, doplet mismatch between source and dbase can occur. Issue will be removed when Consistency Checking will be implemented.

6.2.
       If more than ONE cursor present, saving to database is suppressed.

6.3.
       NO braces/hyphens checking is performed. So if ``#todo:`` line is a part of string, it WILL act as ordinary TODO.

6.4.
       Todo string is mostly protected from editing its structure. Only Tags, Priority and Comment fields are allowed to be changed. This is mainly implemented to keep ID unchanged, because sudden change of it cause overwrite of other dbase entry.
       

7. --> WARNING<--
-------------------------

7.1.
       As NO (no) consistency checking is performed between db and source files,
       any ``//todo`` comments editing outside ST will easily make things inconsistent.

       Also all changes to comments are flushed to database without saving source file itself.
       Reload file without save will result in inconsistence.
       This behavior will remain till synchronizing back FROM database will be done

7.2.
       Creating ``//todo XXXX:`` by defining XXXX explicitly will overwrite or create that specified XXXX task in database. As being used normally, doplet is protected from editing its ID (see issue 6.4)

   
