# coding= utf-8

'''
    PyMySql is used here under its own license which is included.

    PyMySql version used is 0.6.2 and is unchanged,
    project's page is located at http://www.pymysql.org/
'''

import sys, os

if sys.version < '3':
    sys.path.append('PyMySQL-master')
else:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'PyMySQL-master'))

import pymysql

if sys.version < '3':
    from task import *
    from c import *
else:
    from .task import *
    from .c import *

#todo 95 (store) +0: add more 'context' using SQL

class TodoDbSql():
    name= 'Sql'

    dbTablesSrc= {
        "categories": {
            'fields': [
                "`id` int(10) unsigned NOT NULL AUTO_INCREMENT",
                "`id_project` int(10) unsigned NOT NULL",
                "`name` varchar(45) NOT NULL"
            ],
            'suffix': "\
                PRIMARY KEY (`id`),\
                UNIQUE KEY `Index_2` (`id_project`,`name`) USING BTREE\
            "
        },

        "tag2task": {
            'fields': [
                "`id_task` int(10) unsigned NOT NULL",
                "`id_tag` int(10) unsigned NOT NULL",
                "`version` int(10) unsigned NOT NULL DEFAULT '0'",
                "`order` int(10) unsigned NOT NULL DEFAULT '0'"
            ],
            'suffix': "\
                UNIQUE KEY `Index_2` (`id_task`,`id_tag`,`version`) USING BTREE\
            "
        },

        "files": {
            'fields': [
                "`id` int(10) unsigned NOT NULL AUTO_INCREMENT",
                "`id_project` int(10) unsigned NOT NULL",
                "`name` varchar(255) NOT NULL"
            ],
            'suffix': "\
                PRIMARY KEY (`id`),\
                UNIQUE KEY `Index_2` (`id_project`,`name`) USING BTREE\
            "
        },

        "projects": {
            'fields': [
                "`id` int(10) unsigned NOT NULL AUTO_INCREMENT",
                "`name` varchar(45) NOT NULL"
            ],
            'suffix': "\
                PRIMARY KEY (`id`),\
                UNIQUE KEY `Index_2` (`name`)\
            "
        },

        "users": {
            'fields': [
                "`id` int(10) unsigned NOT NULL AUTO_INCREMENT",
                "`name` varchar(45) NOT NULL"
            ],
            'suffix': "\
                PRIMARY KEY (`id`),\
                UNIQUE KEY `Index_2` (`name`)\
            "
        },

        "states": {
            'fields': [
                "`id` int(10) unsigned NOT NULL AUTO_INCREMENT",
                "`name` varchar(45) NOT NULL"
            ],
            'suffix': "\
                PRIMARY KEY (`id`),\
                UNIQUE KEY `Index_2` (`name`)\
            "
        },

        "tasks": {
            'fields': [
                "`id` int(10) unsigned NOT NULL AUTO_INCREMENT",
                "`version` int(10) unsigned NOT NULL",
                "`id_project` int(10) unsigned NOT NULL",
                "`id_state` int(10) unsigned NOT NULL",
                "`id_category` int(10) unsigned NOT NULL",
                "`priority` int(11) NOT NULL DEFAULT '0'",
                "`id_user` int(10) unsigned NOT NULL",
                "`stamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
                "`id_filename` int(10) unsigned NOT NULL",
                "`version_tag` int(10) unsigned NOT NULL DEFAULT '0'",
                "`comment` text"
            ],
            'suffix': "\
                PRIMARY KEY (`id`,`version`,`id_project`) USING BTREE\
            "
        }
    }

    db_pid= 0
    db_uid= 0

    dbAddr= ''
    dbUname= ''
    dbPass= ''
    dbScheme= ''

    dbConn= None

    parentDB= False

    migrate=False

    def __init__(self, _cfg, _parentDB):
        self.dbAddr= _cfg['addr']
        self.dbUname= _cfg['login']
        self.dbPass= _cfg['passw']
        self.dbScheme= _cfg['base']

        self.parentDB= _parentDB


    def reconnect(self):
        if self.dbConn:
            return True

        try:
            self.dbConn = pymysql.connect(host=self.dbAddr, port=3306, user=self.dbUname, passwd=self.dbPass, db=self.dbScheme, use_unicode=True, charset="utf8")
            self.dbConn.autocommit(True)
        except Exception as e:
#todo 35 (sql) +0: deal with connection errors: host, log, scheme
            self.dbConn= None
            print('TypeTodo: MySQL error, Sql connection cannot be established, check MySQL settings:')
            print(e)
            return False

        #check table
        cur = self.dbConn.cursor()
        for tName in self.dbTablesSrc:
            tableDesc= self.dbTablesSrc[tName]

            #if exists
            flagTableOk= True
            try: #check bad table and insert absent fields
                cur.execute("DESCRIBE " +tName)
                fields= []
                for task in cur.fetchall():
                    fields.append(task[0])

                for testField in tableDesc['fields']:
                    testFieldName= testField.split()[0].strip('`')
                    if not unicode(testFieldName) in fields:
                        self.migrate= True
                        cur.execute("ALTER TABLE " +tName +" ADD COLUMN " +testField)
                        print ('TypeTodo MySQL: added `' +testFieldName +'` field into `' +tName +'` table')
            except:
                self.migrate= True
                flagTableOk= False

            if not flagTableOk:
                try:
                    cur.execute("CREATE TABLE  `" +tName +"` (" +','.join(tableDesc['fields']+[tableDesc['suffix']]) +") DEFAULT CHARSET=utf8 ENGINE=MyISAM DELAY_KEY_WRITE=1")
                    print ('TypeTodo MySQL: created `' +tName +'` table')
                except Exception as e:
                    print('TypeTodo: MySQL error, Table \'' +tName +'\' cannot be created:')
                    print(e)
                    self.dbConn= None
                    return False

        cur.execute(
            "INSERT INTO projects (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
            self.parentDB.projectName
        )
        self.db_pid= self.dbConn._result.insert_id


        cur.execute(
            "INSERT INTO users (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
            self.parentDB.projUser
        )
        self.db_uid= self.dbConn._result.insert_id

        cur.close()

        return True


#public#


    def flush(self, _dbN):
        if not self.reconnect():
            return False
        cur = self.dbConn.cursor()

        if self.migrate:
            print 'TypeTodo Sql: migrating'

        for iT in self.parentDB.todoA:
            curTodo= self.parentDB.todoA[iT]
            if not self.migrate:
                if curTodo.savedA[_dbN]: continue

            cur.execute(
                "INSERT INTO states (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
                STATE_LIST[curTodo.state]
            )
            db_stateId= self.dbConn._result.insert_id

            cur.execute(
                "INSERT INTO files (name,id_project) VALUES (%s,%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
                (curTodo.fileName, self.db_pid)
            )
            db_fileId= self.dbConn._result.insert_id

            db_tagIdA= []
            for tag in curTodo.tagsA: #insert all tags by one, holding 
                cur.execute(
                    "INSERT INTO categories (name,id_project) VALUES (%s,%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
                    (tag, self.db_pid)
                )
                db_tagIdA.append(self.dbConn._result.insert_id)

            newVersion= 1
            newTagVersion= 1
            cur.execute(
                "SELECT max(version),max(version_tag) FROM tasks WHERE id=%s AND id_project=%s",
                (curTodo.id, self.db_pid)
            )
            recentTask= cur.fetchone()
            if recentTask and recentTask[0]:
                newVersion= recentTask[0]+1
                newTagVersion= recentTask[1]+1

            cur.execute(
                "INSERT INTO tasks (id,id_state,id_category,priority,id_user,version,id_filename,id_project,comment,stamp,version_tag) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,FROM_UNIXTIME(%s),%s)",
                (curTodo.id, db_stateId, db_tagIdA[0], curTodo.lvl, self.db_uid, newVersion, db_fileId, self.db_pid, curTodo.comment, curTodo.stamp, newTagVersion)
            )

            tagOrder= 0
            for tagId in db_tagIdA:
                cur.execute(
                    "INSERT INTO tag2task (id_tag,id_task,version,`order`) VALUES (%s,%s,%s,%s)",
                    (tagId, curTodo.id, newTagVersion, tagOrder)
                )
                tagOrder+= 1

            curTodo.setSaved(True, _dbN)

        cur.close()

        self.migrate= False
        return True


    def newId(self):
        if not self.reconnect():
            return False
        cur = self.dbConn.cursor()

        cur.execute(
            "SELECT max(id) max_id FROM tasks WHERE id_project IN (%s)",
            self.db_pid
        )
        _id= cur.fetchone()
        if _id and _id[0]:
            _id= int(_id[0]) +1
        else:
            _id= 1

        cur.execute(
            "INSERT INTO tasks (id,id_state,id_category,priority,id_user,version,id_filename,id_project,comment) VALUES (%s,0,0,0,%s,0,0,%s,'')",
            (_id, self.db_uid, self.db_pid)
        )

        cur.close()
        return _id


    def fetch(self, _id=False):
        if not self.reconnect():
            return False
        cur = self.dbConn.cursor()

        cur.execute(
            "SELECT *, UNIX_TIMESTAMP(stamp) ustamp FROM (\
              SELECT id_project maxp,id maxi,max(version) maxv FROM tasks WHERE id_project=%s GROUP BY id\
            ) maxv INNER JOIN tasks ON id_project=maxp AND id=maxi AND version=maxv AND version>0\
            LEFT JOIN (SELECT id idproject, name nameproject FROM projects) _projects ON idproject=id_project\
            LEFT JOIN (SELECT id idstate, name namestate FROM states) _states ON idstate=id_state\
            LEFT JOIN (SELECT id idcat, name namecat FROM categories) _cats ON idcat=id_category\
            LEFT JOIN (SELECT id iduser, name nameuser FROM users) _users ON iduser=id_user\
            LEFT JOIN (SELECT id idfile, name namefile FROM files) _files ON idfile=id_filename",
            (self.db_pid)
        )

        sqn= {} #get id for field names
        for field in cur.description:
            sqn[field[0]]= len(sqn)

        todoA= {}
        ver_tags= {}
        for task in cur.fetchall():
            __id= int(task[sqn['id']])
            ver_tags[__id]= task[sqn['version_tag']]
#todo 144 (multidb) -1: sql; handle cStamp on fetch
            if __id not in todoA:
                todoA[__id]= TodoTask(__id, task[sqn['nameproject']], task[sqn['nameuser']], int(task[sqn['ustamp']]), self.parentDB)

            fetchedStateName= task[sqn['namestate']]
#subject to remove after state names migration+
            if fetchedStateName=='False':
                self.migrate= True
                fetchedStateName= 'Open'
            if fetchedStateName=='True':
                self.migrate= True
                fetchedStateName= 'Close'
#subject to remove after state names migration-
            stateFound= False
            for stateIdx in STATE_LIST:
                if STATE_LIST[stateIdx]==fetchedStateName:
                    stateFound= True
                    break
            if not stateFound: #defaults to 'opened' todo
                stateIdx= ''

            todoA[__id].set(stateIdx, [task[sqn['namecat']]], task[sqn['priority']], task[sqn['namefile']], task[sqn['comment']], task[sqn['nameuser']], int(task[sqn['ustamp']]) )


        for taskId in todoA: #read multitags over
            multitags= []
            cur.execute(
                "SELECT nametag FROM tag2task \
                LEFT JOIN (SELECT id idtag, name nametag FROM categories) _tags ON idtag=id_tag\
                WHERE id_task=%s AND version=%s ORDER BY `order` ASC",
                (taskId, ver_tags[taskId])
            )
            for tagnRow in cur.fetchall():
                multitags.append(tagnRow[0])

            if len(multitags)>0:
                todoA[taskId].setTags(multitags)

        return todoA
