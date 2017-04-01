.. _`public server`: http://typetodo.com/


Configuring TypeTodo
====================

TypeTodo is configured using *.do.cfg* JSON file in the first project's folder.

    *.do.cfg* is automatically created if not found.

    Global *.do.cfg* in *Packages/User* folder is used as template and is also created if none.  
    Global config is used when there's no folders added to project at a moment.

    Default configuration is **HTTP**, using `public server`_ as host and newly created repository with random name, like ``~exwvpaytkfs6``.  

    **FILE** database is always used, even if not specified.



Acceptable configurations are **FILE**, **MYSQL** and **HTTP**


.. contents::
..


1. **FILE** mode
----------------

Specified by ``"engine": "file"`` block.  

``"file":`` defines path/file to be used as database.  
Path can be absolute or relative to *[projectName].do* itself.

If no explicit **FILE** database is defined or ``"file":`` value is blank, then *[projectName].do* is used as database storage.


File used for this mode (*[projectName].do* itself or external) holds tasks using following format:
       
    ``[ |-|+|=|!]tags XXXX: [+|-]N filename editorName editionStamp``
    
    ``comment``

where fields are:

* [ \|-\|+\|=\|!]
       TODO state: ``' '`` indicates pending task, ``'-'`` - opened, ``'+'`` - closed, ``'='`` - in-progress, and ``'!'`` - canceled.
* tags
       comma-separated tag list
* XXXX
       task integer ID, unique within project (and within *.do* file)
* [+|-]N
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

Specified by ``"engine": "http"`` block.  
**Personal** repository requires ``"login":`` and ``"password":`` to be specified.

Repository is accessible at `public server`_/<repository>

* public repository
    Is created at first run using name like ``~exwvpaytkfs6``.  
    It is free to read and write by everyone who knows it's name.  

* personal repository
    Have same name as user registered at http://typetodo.com. It is readable by everyone but can be written only if login/password provided. Using site service, write access to particular project can be grant to specified user.
       
All changes done to TODO comment are accumulated and flushed with incremented version and same ID. So all changes history is saved (not yet displayed on site).


3. **MySQL** mode
-----------------

Specified by ``"engine": "mysql"`` block.  

*<scheme>* specified MUST exist at server.

Following tables will be created if not exists:

* projects
* categories (tags)
* tag2task
* files
* users
* states
* tasks

All changes done to TODO comment are accumulated and flushed with incremented version and same ID. So all changes history is saved.
