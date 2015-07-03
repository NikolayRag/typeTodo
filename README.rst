typeTodo
=========

Manage TODO comments, as they're typed anywhere in project code.



.. contents::
..

.. _`public server`: http://www.typetodo.com/

1. Key features
---------------

* TypeTodo stores and synchronizes TODO comments (doplets) within separate per-project database.
       
* Database can be text **File**, **MySQL** or **HTTP**, any number of them. Free `public server`_ exists to handle **HTTP** mode.

* Each doplet is assigned ID at creation, unique within project.

* Most interaction is done by ordinary inline source code commenting. Just type and don't look aside.

* TypeTodo is intended to be used by multiple contributors over one project at one time without interference.

* Explicit commands and keyboard shortcuts are available and are described in section `5. Related Commands`_.



2. TODO creation and editing
----------------------------

Start with typing ``//todo:`` or ``#todo:`` comment, according to used language.
As colon ``:`` is typed, rest of line is instantly substituted with snippet, introducing additional fields: ``//todo XXXX (tag) [+-]N: <comment>`` where XXXX is assigned unique integer ID.
       
Any futher edition of any of that comment field (doplet) will trigger to flush it to database, using XXXX as ID.
Database is specified in *[projectName].do* text file which is placed inside the first project's folder.

* detailed doplet fields description found in section `3. Doplet comment fields`_
* database configuration is described in section `4. .do config file and default database`_
       
* If at a moment there's no project used, then global *.do* file is used as a database.
* Project's or Global *.do* are accessible with provided command.


Changing ``//todo...`` to ``//+todo...`` (adding ``+`` sign or pressing <Alt>+<Shift>+<Numpad +>) changes state to 'done' in database and wipes that comment of the code.
Full set of states are:

* '' or '-' *(<Alt>+<Shift>+<Numpad ->)*  Opened TODO (default)
* '=' *(<Alt>+<Shift>+<=>)*  TODO in progress, used for management of TODOs
* '+' *(<Alt>+<Shift>+<Numpad +>)*  Closed TODO, wiped when set
* '!' *(<Alt>+<Shift>+<!>)*  Canceled TODO; As set, you will be asked for reason of canceling. If specified, that reason replaces TODOs comment in database. Then TODO is wiped.



3. Doplet comment fields
----------------------

Doplet is a comment in form of ``//todo XXXX (tags) [+-]N: comment`` with following fields used:
       
* XXXX
       - **mandatory**
       - would be auto-generated sequential number, unique within project
* (tags)
       - comma-separated list
       - default: 'general'
       - When you rename it, new name will be reused with next new TODO
* [+-]N
       - default: +0
       - priority level. Just signed (always) integer number for addition.
* comment
       - comment is any remaining text till the end of line


4. .do config file and default database
---------------------------------

*.do* file is used both as configuration and default storage database.
If currently there IS project opened in Sublime, *<projectName>.do* is located inside the first project's folder: so if first folder included in project is */myProject*, then */myProject/myProject.do* file will be used as config.

*<projectName>.do* is automatically created if none found, and it's config is copied from global *.do*, which is also automatically created if there's no one.

Global *.do* is used one for all doplets when there's NO project used at a moment.


4.0.
       All configuration entries found in *.do* counts.
       *.do* file is checked periodically for configuration changes, and they reapplied on fly.
      
       Default *.do* explicit configuration is HTTP, using http://typetodo.com as host and newly created database with random name like ``~exwvpaytkfs6``. Also if no external **FILE** is specified, *.do* file itself is implicitly used as database storage.

       Acceptable configurations are **FILE**, **MYSQL** and **HTTP**


4.1. **FILE** mode
       Specified by ``file <filename.ext>`` line.

       Provided ``<filename.ext>`` is created and used within the same place as *<projectName>.do*. It is available to specify relative or absolute path together with file name.
       If no explicit **FILE** database is defined, then *.do* is implicitly used as database.


       File used for this mode (*.do* itself or external) holds tasks using following format:
       
       ``(+|-|=|!)tags XXXX: [+|-N] filename editorName editionStamp``
       
       ``comment``

       where fields are:

* (+|-|=|!)
       TODO state: ``-`` indicates open task, ``+`` - closed, ``=`` - in-progress, and ``!`` stands for canceled.
* tags
       comma-separated tag list
* XXXX
       task integer ID, unique within project (and within *.do* file)
* +|-N
       priority, arbitrary signed integer number
* filename
       file at which task was created. If *.sublime-project* is found, relative path is stored.
* editorName
       name of user which edited task last, it is taken from system environment
* editionStamp
       date and time task was edited last. Using **dd/mm/yy hh:mm** format
* comment, *at second line*
       arbitrary text


4.2. **MySQL** mode
       Specified by ``mysql <host> <user> <pass> <scheme>`` line.

       *<scheme>* specified MUST exist at server.

       Following tables will be created if not exists:

* projects
* categories (for tags)
* tag2task
* files
* users
* states
* tasks

All changes done to TODO comment are accumulated and flushed with incremented version and same ID. So all changes history is saved.


4.3. **HTTP** mode
       Specified by ``http <host> <repository>`` or ``http <host> <repository> <user> <pass>`` line.

       If ``<user> <pass>`` logon credentials are specified, repository is treated as **personal**, otherwise it is **public**.

       Repository is accessible at http://typetodo.com/<repository>

* public repository
       Is created at first run or can be recreated using *TypeTodo: Reset Global config* command. It is free to read and write by everyone who knows it's name.
       Public repository name looks like ``~exwvpaytkfs6``
* personal repository
       Have same name as user registered at http://typetodo.com. It is readable by everyone (yet) but can be written only by providing logon username and pass. Using site service, you can grant write access for particular project to specified site user.
       
All changes done to TODO comment are accumulated and flushed with incremented version and same ID. So all changes history is saved (not yet displayed within www site).



5. Related Commands
--------------------
       
While using of TypeTodo is completely implicit, there're some support commands and keyboard shortcuts available:

* **Set State** (<Alt>+<d> shortcut)
       This command offers list of states to change the state of current doplet. As the states count will become more varied, this command is going to be more useful.

* **Find Todo** (<Alt>+<Shift>+<d> shortcut)
       Performs searching for doplets:
       Find in *.do* using current doplet's ID (one that cursor stands in);
       Find in source using current *.do* entry ID;
       If not standing over any doplet, then find in source by specifying:
       - ID
       - Tags, comma-separated. All doplets which have at least one tag partially match will count. Regexps allowed.
       - Exclusive tags. Same as tags search, but show all, BUT matched ones.
       - List current view doplets, by searching blank string.

* **Toggle Colorize**
       By default all doplets in code are highlited with three colors: Opened, In-progress and Inconsistent. This can be switched off/on.

* **Open Global/Project Config**
       Command for opening related ``.do`` file. While **Find todo** command is presented, there's no big use of opening config too often.

* **Browse Project's Repository**
       Used to open current project within HTTP repository in browser. Server and repository are defined in ``.do` config.

* **Reset Global Config**
       Reinitialise global ``.do`` config while keeping it's doplet records. Mainly reinitialisation means gathering of new public HTTP repository, while old one will remain forgotten on web-server.

* **Update Inconsistence**
       For any doplet line that differs from database, duplicate that line by fetching it's actual form from database.



6. Meaningful issues and behavior
---------------------------------

* As TODO is created or edited, any changes are saved to dbase in background, even if current source file is not saved. If Sublime is closed afterall without save, doplet mismatch between source and dbase can occur.

* If more than ONE cursor present, saving to database is suppressed.

* NO braces/hyphens checking is performed. So if ``#todo:`` line is a part of string, it WILL act as ordinary doplet.

* Todo string is mostly protected from editing its structure. Only State, Tags, Priority and Comment fields are allowed to be changed. This is mainly implemented to keep ID unchanged, because sudden change of it cause overwrite of other database entry.

* Consistency is checked periodically and doplets that differs from dbase are highlited. Highlighting occurs only if Colorizing NOT switched off.
       

7. --> WARNING<--
-------------------------

There're some ways to bring inconsistence between code and dbase, which will result in highlighting problems:

* Any ``//todo`` comments editing outside ST.

* Reloading file without save, because changes to comments are flushed to database regardless of saving source file itself.

* Copy-Pasting doplet, so you have more than one entry with same ID. This is not prohibited, so later editing any one of them will make others outdated.

* Creating ``//todo XXXX:`` by defining XXXX explicitly will overwrite or create that specified XXXX task in database. As being used normally, doplet is protected from editing its ID (see issue 6.5)

* Switching project in window does not have correct Sublime API support so it can end up in Flush error. Restarting Sublime is the solution.
