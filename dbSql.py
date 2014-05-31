# coding= utf-8

'''
    PyMySql is used here under its own license which is included.

    PyMySql version used is 0.6.2 and is unchanged,
    project's page is located at http://www.pymysql.org/
'''

import sublime
import sys, os

if sys.version < '3':
    sys.path.append('PyMySQL-master')
else:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'PyMySQL-master'))

import pymysql
    
class TodoDbSql():

    dbTablesSrc= {
        "categories": "\
          `id` int(10) unsigned NOT NULL AUTO_INCREMENT,\
          `id_project` int(10) unsigned NOT NULL,\
          `name` varchar(45) NOT NULL,\
          PRIMARY KEY (`id`),\
          UNIQUE KEY `Index_2` (`id_project`,`name`) USING BTREE\
        ",

        "files": "\
          `id` int(10) unsigned NOT NULL AUTO_INCREMENT,\
          `id_project` int(10) unsigned NOT NULL,\
          `name` varchar(255) NOT NULL,\
          PRIMARY KEY (`id`),\
          UNIQUE KEY `Index_2` (`id_project`,`name`) USING BTREE\
        ",

        "projects": "\
          `id` int(10) unsigned NOT NULL AUTO_INCREMENT,\
          `name` varchar(45) NOT NULL,\
          PRIMARY KEY (`id`),\
          UNIQUE KEY `Index_2` (`name`)\
        ",

        "users": "\
          `id` int(10) unsigned NOT NULL AUTO_INCREMENT,\
          `name` varchar(45) NOT NULL,\
          PRIMARY KEY (`id`),\
          UNIQUE KEY `Index_2` (`name`)\
        ",

        "states": "\
          `id` int(10) unsigned NOT NULL AUTO_INCREMENT,\
          `name` varchar(45) NOT NULL,\
          PRIMARY KEY (`id`),\
          UNIQUE KEY `Index_2` (`name`)\
        ",

        "tasks": "\
          `id` int(10) unsigned NOT NULL AUTO_INCREMENT,\
          `version` int(10) unsigned NOT NULL,\
          `id_project` int(10) unsigned NOT NULL,\
          `id_state` int(10) unsigned NOT NULL,\
          `id_category` int(10) unsigned NOT NULL,\
          `priority` int(11) NOT NULL DEFAULT '0',\
          `id_user` int(10) unsigned NOT NULL,\
          `stamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,\
          `id_filename` int(10) unsigned NOT NULL,\
          `comment` text,\
          PRIMARY KEY (`id`,`version`,`id_project`) USING BTREE\
        "

    }

    db_pid= 0
    db_uid= 0


    todoA= None
    projectName= ''
    userName= ''

    dbAddr= ''
    dbUname= ''
    dbPass= ''
    dbScheme= ''


    dbConn= None

    def __init__(self, _todoA, _uname, _name, _dbAddr, _dbUname, _dbPass, _dbScheme):
        self.todoA= _todoA
        self.userName= _uname
        self.projectName= _name

        self.dbAddr= _dbAddr
        self.dbUname= _dbUname
        self.dbPass= _dbPass
        self.dbScheme= _dbScheme


    def reconnect(self):
        if self.dbConn:
            return True

        try:
            self.dbConn = pymysql.connect(host=self.dbAddr, port=3306, user=self.dbUname, passwd=self.dbPass, db=self.dbScheme, use_unicode=True, charset="utf8")
            self.dbConn.autocommit(True)
        except:
#todo 35 (sql) +0: deal with connection errors: host, log, scheme
            self.dbConn= None
            sublime.error_message('TypeTodo MySQL error:\n\n\tSql connection cannot be established,\n\tcheck MySQL settings')
            return False

#todo 59 (sql) -10: (not sure) check table over opened connection too

        #check table
        cur = self.dbConn.cursor()
        for tName in self.dbTablesSrc:
            #if exists
            flagTableOk= True
            try:
                cur.execute("DESCRIBE " +tName)

#todo 36 (sql) +0: check bad table and do something with it (upgrade? kill?)
#                flagTableOk= False
            except:
                flagTableOk= False

            if not flagTableOk:
                try:
                    cur.execute("CREATE TABLE  `" +tName +"` (" +self.dbTablesSrc[tName] +") DEFAULT CHARSET=utf8 ENGINE=MyISAM DELAY_KEY_WRITE=1")
                except:
                    sublime.error_message('TypeTodo MySQL error:\n\n\tTable \'' +tName +'\' cannot be created')
                    return False

        cur.execute("INSERT INTO projects (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)", self.projectName)
        self.db_pid= self.dbConn._result.insert_id


        cur.execute("INSERT INTO users (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)", self.userName)
        self.db_uid= self.dbConn._result.insert_id

        cur.close()

        return True


#public#


    def flush(self):
        if not self.reconnect():
            return False
        cur = self.dbConn.cursor()

        for iT in self.todoA:
            curTodo= self.todoA[iT]
            if curTodo.saved: continue

            cur.execute("INSERT INTO states (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)", str(curTodo.state))
            db_stateId= self.dbConn._result.insert_id

            cur.execute("INSERT INTO files (name,id_project) VALUES (%s,%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)", (curTodo.fileName, self.db_pid))
            db_fileId= self.dbConn._result.insert_id

            cur.execute("INSERT INTO categories (name,id_project) VALUES (%s,%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)", (curTodo.cat, self.db_pid))
            db_catId= self.dbConn._result.insert_id


            newVersion= 1
            cur.execute("SELECT max(version) FROM tasks WHERE id=%s AND id_project=%s", (curTodo.id, self.db_pid))
            recentTask= cur.fetchone()
            if recentTask:
                newVersion= recentTask[0]+1

            cur.execute("INSERT INTO tasks (id,id_state,id_category,priority,id_user,version,id_filename,id_project,comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (curTodo.id, db_stateId, db_catId, curTodo.lvl, self.db_uid, newVersion, db_fileId, self.db_pid, curTodo.comment))

#todo 69 (sql) +0: behave at individual save result
            curTodo.setSaved()

        cur.close()

        return True


    def newId(self):
        if not self.reconnect():
            return False
        cur = self.dbConn.cursor()

        cur.execute("SELECT max(id) max_id FROM tasks WHERE id_project IN (%s)", self.db_pid)
        _id= cur.fetchone()
        if _id and _id[0]:
            _id= int(_id[0]) +1
        else:
            _id= 1

        cur.execute("INSERT INTO tasks (id,id_state,id_category,priority,id_user,version,id_filename,id_project,comment) VALUES (%s,0,0,0,%s,0,0,%s,'')", (_id, self.db_uid, self.db_pid))

        cur.close()
        return _id
