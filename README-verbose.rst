typeTodo
=========

Manage TODO comments, as they're typed anywhere in project code.

Blitz:
- Install TypeTodo,
- Type ``//todo:`` comment right in your code, or use other comment char,
- Type in the snippet appeared,
- Check for *[projectName].do* file created in you project's root
or
- Run Sublime's ``TypeTodo: Browse for project's repository`` <alt+d>, <alt+h>


.. _`public server`: http://www.typetodo.com/

1. Key features
---------------

* TypeTodo stores and synchronizes TODO comments (doplets) into external per-project database.
       
* Most interaction is done by ordinary inline source code commenting. Just type and don't look aside.

* Each doplet is assigned an ID, unique within project.

* Database can be text **File**, **MySQL** or **HTTP**. **HTTP** mode uses `public server`_ as a database.




2. TODO creation and editing
----------------------------

Start with typing ``//todo:`` comment, or use any other comment prefix according to used language.
As colon ``:`` is typed, rest of line is instantly substituted with snippet, introducing additional fields: ``//todo XXXX (tag) [+-]N: <comment>``.
XXXX will be instantly assigned with integer ID, unique within project.
       
Any futher edition of any of that comment field (doplet) will trigger to flush it to database, using XXXX as ID.
Database is specified in *[projectName].do* text file which is placed inside the first project's folder.

* If at a moment there's no project used, then global *.do* file is used as a database.


Changing doplet to ``// +todo...`` (adding ``+`` sign or pressing <Alt+d>,<Alt+Plus>) changes state to 'done' in database and wipes that comment of the code.
Full set of states are:

* ' ' *<Alt+d>,<Alt+Space>* **Pending**, at creation
* '-' *<Alt+d>,<Alt+Minus>* **Opened**, management state
* '=' *<Alt+d>,<Alt+=>* **In Progress**, management state
* '+' *<Alt+d>,<Alt+Plus>* **Closed**, wiped when set
* '!' *<Alt+d>,<Alt+Del>* **Canceled**; As set, you will be asked for reason of canceling. If specified, that reason replaces TODOs comment in database. Then TODO is wiped.



3. Doplet snippet fields
----------------------

Doplet is a comment like ``//todo XXXX (tags) [+-]N: comment`` with following fields used:
       
* XXXX
       - **mandatory**
       - would be auto-generated sequential number, unique within project.
* (tags)
       - comma-separated list
       - default: 'general'
* [+-]N
       - default: +0
       - priority level. Just signed (always) integer number for addition.
* comment
       - comment is any remaining text till the *end of line*.


4. Related Commands and keyboard shortcuts
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
       Used to open current project within HTTP repository in browser. Server and repository to browse are defined in ``.do` config.

* **Reset Global Config**
       Reinitialise global ``.do`` config while keeping it's doplet records. Mainly reinitialisation means gathering of new public HTTP repository, while old one will remain forgotten on web-server.

* **Update Inconsistence**
       For any doplet line that differs from database, duplicate that line by fetching it's actual content from database.



6. Meaningful issues and behavior
---------------------------------

* As TODO is created or edited, any changes are saved to dbase in background, even if current source file is not saved. If Sublime is closed afterall without save, doplet mismatch between source and dbase can occur.

* If more than ONE cursor present, saving to database is suppressed.

* NO braces/hyphens checking is performed. So if ``#todo:`` line is a part of string, it WILL act as ordinary doplet.

* Todo string is mostly protected from editing its structure. Only State, Tags, Priority and Comment fields are allowed to be changed. This is implemented mainly to keep ID unchanged, because sudden change of it cause overwrite of other database entry.

* Consistency is checked periodically and doplets that differs from dbase are highlited. Highlighting occurs only if Colorizing NOT switched off.
       

7. --> WARNING<--
-------------------------

There're some ways to bring inconsistence between code and dbase, which will result in highlighting problems (**avoid acting like this**):

* Any ``//todo`` comments editing outside ST.

* Reloading file without save, because changes to comments are flushed to database regardless of saving source file itself.

* Copy-Pasting doplet, so you have more than one entry with same ID. This is not prohibited, so later editing any one of them will make others outdated.

* Creating ``//todo XXXX:`` by defining XXXX explicitly will overwrite or create that specified XXXX task in database. As being used normally, doplet is protected from editing its ID (see issue 6.5)

* Switching project in window does not have correct Sublime API support so it can end up in Flush error. Restarting Sublime is the solution.
