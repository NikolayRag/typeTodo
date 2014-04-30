'''
    PyMySql is used here under its own license which is included.

    PyMySql version used is 0.6.2 and is unchanged,
    project's page is located at http://www.pymysql.org/
'''

import sys
sys.path.append('PyMySql-master')
import pymysql


#todo 37 (sql) +0: optimize, optimize, opt
class TodoDbSql():
    todoA= None
    projectName= ''
    userName= ''

    db_pid= 0
    db_uid= 0

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
          `id_state` int(10) unsigned NOT NULL,\
          `id_category` int(10) unsigned NOT NULL,\
          `priority` int(11) NOT NULL DEFAULT '0',\
          `id_user` int(10) unsigned NOT NULL,\
          `stamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,\
          `version` int(10) unsigned NOT NULL,\
          `id_filename` int(10) unsigned NOT NULL,\
          `id_project` int(10) unsigned NOT NULL,\
          `comment` text,\
          PRIMARY KEY (`id`,`version`) USING BTREE\
        "

    }


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
            self.dbConn = pymysql.connect(host=self.dbAddr, port=3306, user=self.dbUname, passwd=self.dbPass, db=self.dbScheme)
            self.dbConn.autocommit(True)
        except:
#todo 35 (sql) +0: deal with connection errors: host, log, scheme
            self.dbConn= None
            print 'error: Sql connection'
            return False

        #check table
        cur = self.dbConn.cursor()
        for tName in self.dbTablesSrc:
            #if exists
            flag= True
            try:
                cur.execute("DESCRIBE " +tName)

#todo 36 (db) +0: check bad table and do something with it (upgrade? kill?)
#                flag= False
            except:
                flag= False

            if not flag: #didnt exist or removed
                try:
                    cur.execute("CREATE TABLE  `" +tName +"` (" +self.dbTablesSrc[tName] +") DEFAULT CHARSET=utf8 ENGINE=MyISAM DELAY_KEY_WRITE=1")
                except:
                    print 'error: Sql maintainance'
                    return False

        cur.execute("INSERT INTO projects (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)", self.projectName)
        self.db_pid= self.dbConn._result.insert_id


        cur.execute("INSERT INTO users (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)", self.userName)
        self.db_uid= self.dbConn._result.insert_id

        cur.close()

        return True



#todo 39 (issue) -1: fail if tables deleted on the fly. Should fix ever?
    def store(self, _id, _state, _cat, _lvl, _fileName, _comment):
        if not self.reconnect():
            return False

        cur = self.dbConn.cursor()

        cur.execute("INSERT INTO states (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)", str(_state))
        db_stateId= self.dbConn._result.insert_id

        cur.execute("INSERT INTO files (name,id_project) VALUES (%s,%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)", (_fileName, self.db_pid))
        db_fileId= self.dbConn._result.insert_id

        cur.execute("INSERT INTO categories (name,id_project) VALUES (%s,%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)", (_cat, self.db_pid))
        db_catId= self.dbConn._result.insert_id

#todo 40 (sql) +0: save subsequent versions as delayed save will be implemented
        if _id:
            cur.execute("SELECT id FROM tasks WHERE id=%s", _id)
            db_taskId= cur.fetchone()
            if not db_taskId:
                cur.execute("INSERT INTO tasks (id,id_state,id_category,priority,id_user,version,id_filename,id_project) VALUES (%s,0,0,0,0,1,0,0)", _id)

            cur.execute("UPDATE tasks SET id_state=%s, id_category=%s, priority=%s, id_user=%s, version=version+1, id_filename=%s, id_project=%s, comment=%s WHERE id=%s AND version>0", (db_stateId, db_catId, int(_lvl), self.db_uid, db_fileId, self.db_pid, _comment, _id))

        else:
            cur.execute("INSERT INTO tasks (id_state,id_category,priority,id_user,version,id_filename,id_project,comment) VALUES (%s,%s,%s,%s,0,%s,%s,%s)", (db_stateId, db_catId, int(_lvl), self.db_uid, db_fileId, self.db_pid, _comment))
            cur.execute("INSERT INTO tasks (id,id_state,id_category,priority,id_user,version,id_filename,id_project,comment) VALUES (LAST_INSERT_ID(),%s,%s,%s,%s,1,%s,%s,%s)", (db_stateId, db_catId, int(_lvl), self.db_uid, db_fileId, self.db_pid, _comment))
            _id= self.dbConn._result.insert_id


        cur.close()

        return _id


