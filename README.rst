typeTodo
=========

Manage TODO comments, as they're typed anywhere in project code.

Blitz:
------
- Install TypeTodo,
- Type ``//todo:`` comment right in your code, or use other comment char,
- Type in the snippet appeared,
- Check for *[projectName].do* file created in you project's root
or
- Run Sublime's ``TypeTodo: Browse for project's repository`` command (*<alt+d>, <alt+h>*)



Key features
------------

* TypeTodo stores and synchronizes TODO comments (doplets) into external per-project database.
       
* Most interaction is done by ordinary inline source code commenting. Just type and don't look aside.

* Each doplet is assigned an ID, unique within project.

* Database can be text **File**, **MySQL** or **HTTP**. **HTTP** mode uses `public server`_ as a database.

      

--> WARNING <--
---------------

There're some ways to bring inconsistence between code and dbase, which will result in highlighting problems (**avoid acting like this**):

* Any ``//todo`` comments editing outside ST.

* Reloading file without save, because changes to comments are flushed to database regardless of saving source file itself.

* Copy-Pasting doplet, so you have more than one entry with same ID. This is not prohibited, so later editing any one of them will make others outdated.

* Creating ``//todo XXXX:`` by defining XXXX explicitly will overwrite or create that specified XXXX task in database. As being used normally, doplet is protected from editing its ID (see issue 6.5)

* Switching project in window does not have correct Sublime API support so it can end up in Flush error. Restarting Sublime is the solution.
