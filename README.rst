typeTodo
=========

Manage TODO comments, as they're typed anywhere in project code.

Blitz:
------
- Install TypeTodo,
- Type ``//todo:`` comment right in your code, or use other comment prefix,
- Type in the snippet appeared,
- Check for *[projectName].do* file created in you project's root
or
- Run Sublime's ``TypeTodo: Browse for project's repository`` command (*<alt+d>, <alt+h>*)


.. _`Verbose TypeTodo description`: https://github.com/NikolayRag/typeTodo/blob/working/README-verbose.rst
`Verbose TypeTodo description`_

.. _`Configuring TypeTodo`: https://github.com/NikolayRag/typeTodo/blob/working/README-config.rst
`Configuring TypeTodo`_



Key features
------------

* TypeTodo stores and synchronizes todo comments (doplets) into external per-project database.
       
* Most interaction is done by ordinary inline source code commenting. Just type and don't look aside.

* Each doplet is assigned an ID, unique within project.

* Database can be **MySQL**, **HTTP** or text **File** by default.

      

WARNING
-------

There're some ways to bring inconsistence between code and dbase, which will result in highlighting problems (**AVOID doing this**):

* Any ``//todo`` comments editing outside ST.

* Reloading file without save, as changes to comments are flushed to database regardless of saving file itself or not.

* Copy-Pasting doplet, so you have more than one entry with same ID. This is not prohibited, so later editing any one of them will make others outdated.

* Creating ``//todo XXXX:`` by defining XXXX explicitly will overwrite or create that specified XXXX task in database. As being used normally, doplet is protected from editing its ID.

* Switching project in window does not have correct Sublime API support so it can end up in Flush error. Restarting Sublime is the solution.
