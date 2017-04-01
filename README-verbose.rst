Verbose TypeTodo description
============================

.. contents::
..


1. Todo creation and editing
----------------------------

Start with typing ``//todo:`` comment, or use any other comment prefix according to used language.  

As colon ``:`` is typed, rest of line is instantly substituted with snippet, introducing additional fields: ``//todo XXXX (tag) [+-]N: <comment>``.  

``XXXX`` will be instantly assigned with integer ID, unique within the project.
       
Any futher edition of any of that comment field (doplet) will trigger to flush it to database, using XXXX as ID.

By default database is *[projectName].do* text file which is placed inside the first project's folder **and** repository at *typetodo.com*.

    If at a moment there's no project used, then database is a *.do* file in Sublime's *Packages/User* folder.


Changing doplet to ``// +todo...`` (adding ``'+'`` sign or pressing *<Alt+D>,<Alt+Plus>*) changes state to 'done' in database and wipes that comment of the code.

Full set of states are:

* ``' '`` **<Alt+D>,<Alt+Space>**: 'Pending', at creation

* ``'-'`` **<Alt+D>,<Alt+Minus>**: 'Opened', management state

* ``'='`` **<Alt+D>,<Alt+=>**: 'In Progress', management state

* ``'+'`` **<Alt+D>,<Alt+Plus>**: 'Closed', wiped when set

* ``'!'`` **<Alt+D>,<Alt+Del>**: 'Canceled'; As set, you will be asked for reason of canceling. If specified, that reason replaces doplet's comment in database. Then doplet is wiped.

In addition, shortcuts for raising/lowering priority are:

* **<Alt+D>,<Alt+Up>**: Up 1

* **<Alt+D>,<Alt+Down>**: Down 1


2. Doplet snippet fields
----------------------

Doplet is a comment like ``//todo XXXX (tags) [+-]N: comment`` with following fields used:
       
* XXXX
       - **mandatory**
       - would be auto-generated sequential number, unique within project.
* (tags)
       - comma-separated list
       - default: 'general'
* [+-]N
       - priority level. Signed (always) integer number for addition.
       - default: +0
* comment
       - comment is any remaining text till the *end of line*.


3. Related Commands and keyboard shortcuts
--------------------
       
While using of TypeTodo is completely implicit, there're some support commands and keyboard shortcuts available:

* Set State, **<Alt+D>,<Alt+D>**
       Offer list of states to change the state of doplet under cursor.

* Jump, **<Alt+D>,<Alt+J>**
       Jump from doplet under cursor to **FILE** database and back.

* Find Todo, **<Alt+D>,<Alt+F>**
       Performs searching for doplets:
       - by ID
       - by tags, comma-separated. Regexps allowed.
       - by '*', meaning all doplets,
       - by '', listing doplets in current view only.

       Placing '-' sign before search string finds all BUT specified doplets.

* Update Inconsistence, **<Alt+D>,<Alt+I>**
       For any doplet within view that differs from database, duplicate that doplet by fetching it's actual content from database.

* HTTP Repository, **<Alt+D>,<Alt+H>**
       Used to open current project within HTTP repository in browser. Server and repository to browse are defined in *.do* config.

* Config / Global Config
       Command for opening related *.do* file.


.. _`Configuring TypeTodo`: https://github.com/NikolayRag/typeTodo/blob/master/README-config.rst
`Configuring TypeTodo`_


4. Meaningful issues and behavior
---------------------------------

* As doplet is created or edited, any changes are saved to dbase in background, even if current source file is not saved. If Sublime is closed afterall without save, doplet mismatch between source and dbase can occur.

* If more than ONE cursor present, saving to database is suppressed.

* NO braces/hyphens checking is performed. So if ``#todo:`` line is a part of string, it WILL act as ordinary doplet.

* Doplet string is mostly protected from editing its structure. Only State, Tags, Priority and Comment fields are allowed to be changed. This is implemented mainly to keep ID unchanged, because sudden change of it cause overwrite of other database entry.

* Consistency is checked periodically and doplets that differs from dbase are highlited.



5. WARNING
----------

There're some ways to bring inconsistence between code and dbase, which will result in highlighting problems (**AVOID doing this**):

* Any ``//todo`` comments editing outside ST.

* Reloading file without save, as changes to comments are flushed to database regardless of saving file itself or not.

* Copy-Pasting doplet, so you have more than one entry with same ID. This is not prohibited, so later editing any one of them will make others outdated.

* Creating ``//todo XXXX:`` by defining XXXX explicitly will overwrite or create that specified XXXX task in database. As being used normally, doplet is protected from editing its ID.

* Switching project in window does not have correct Sublime API support so it can end up in Flush error. Restarting Sublime is the solution.
