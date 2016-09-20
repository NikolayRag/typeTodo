.. _`public server`: http://typetodo.com/


Configuring TypeTodo
====================

TypeTodo is configured with *[projectName].do* files, which are used both as configuration and default database storage.

    *[projectName].do* is automatically created in the first project's folder if none found:
    if first folder included in project is ``/myProject``, then ``/myProject/myProject.do`` file will be used as config.

    Global *.do* is used as settings template.

    Default *.do* configuration is **HTTP**, using `public server`_ as host and newly created repository with random name like ``~exwvpaytkfs6``.

    Global *.do* is used one for all doplets when there's NO project used at a moment.


Acceptable configurations are **FILE**, **MYSQL** and **HTTP**


.. contents::
..


1. **FILE** mode
----------------

Specified by ``file <path/filename.ext>`` line.
Path can be absolute or relative to *[projectName].do* itself.

If no explicit **FILE** database is defined, then *[projectName].do* is used as database stoprage.


File used for this mode (*[projectName].do* itself or external) holds tasks using following format:
       
    ``[ |-|+|=|!]tags XXXX: [+|-N] filename editorName editionStamp``
    ``comment``

where fields are:

* [ |-|+|=|!]
       TODO state: `` `` indicates pending task, ``-`` - opened, ``+`` - closed, ``=`` - in-progress, and ``!`` - canceled.
* tags
       comma-separated tag list
* XXXX
       task integer ID, unique within project (and within *.do* file)
* +|-N
       priority, arbitrary signed integer number
* filename
       file at which task was created. If ``.sublime-project`` is found, relative path is stored.
* editorName
       name of user which edited task last, it is taken from system environment
* editionStamp
       date and time task was edited last. Using **dd/mm/yy hh:mm** format
* comment, *at second line*
       arbitrary text


2. **HTTP** mode
----------------

Specified by ``http <host> <repository>`` or ``http <host> <repository> <user> <pass>`` line.

If ``<user> <pass>`` logon credentials are specified, repository is treated as **personal**, otherwise it is **public**.

Repository is accessible at `public server`_/<repository>

* public repository
       Is created at first run or can be recreated using *TypeTodo: Reset Global config* command. It is free to read and write by everyone who knows it's name.
       Public repository name looks like ``~exwvpaytkfs6``

* personal repository
       Have same name as user registered at http://typetodo.com. It is readable by everyone (yet) but can be written only by providing logon username and pass. Using site service, you can grant write access for particular project to specified site user.
       
All changes done to TODO comment are accumulated and flushed with incremented version and same ID. So all changes history is saved (not yet displayed on site).


3. **MySQL** mode
-----------------

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
