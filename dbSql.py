# coding= utf-8

'''
    PyMySql is used here under its own license which is included.

    PyMySql version used is 0.6.2 and is unchanged,
    project's page is located at http://www.pymysql.org/
'''

import sys, os

if sys.version < '3':
    sys.path.append('PyMySQL')
else:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'PyMySQL'))

import pymysql

if sys.version < '3':
    from task import *
    from c import *
else:
    from .task import *
    from .c import *



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
                "`order` int(10) unsigned NOT NULL DEFAULT '0'",
                "`id_project` int(10) unsigned NOT NULL"
            ],
            'suffix': "\
                UNIQUE KEY `Index_2` (`id_task`,`id_tag`,`version`,`id_project`) USING BTREE\
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

    lastId= None

    settings= None
    parentDB= False
    dbId= None

    cPid= None
    cUid= None

    tablesPassed= False


    def __init__(self, _parentDB, _settings, _dbId):
        self.settings= _settings
        self.parentDB= _parentDB
        self.dbId= _dbId


    def sqExecute(self, _connA, _cur, _stmt, _args=False):
        if not _connA[0]:
            return False

        try:
            if _args:
                _cur.execute(_stmt, _args)
            else:
                _cur.execute(_stmt)
            return True
        except:
            print ('TypeTodo MySQL statement error, skipped')
            _connA[0]= False
            _cur.close()

            return False



    def reconnect(self):
        try:
            cConnection= pymysql.connect(host=self.settings.host, port=3306, user=self.settings.login, passwd=self.settings.passw, db=self.settings.scheme, use_unicode=True, charset="utf8")
            cConnection.autocommit(True)
        except Exception as e:
            print('TypeTodo: MySQL error, Sql connection cannot be established, check MySQL settings:')
            print(e)
            return False

        if not self.checkTables(cConnection):
            return False

        cur= cConnection.cursor()

        if not self.cPid:
            if self.sqExecute([cConnection], cur,
                "INSERT INTO projects (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
                self.parentDB.config.projectName
            ):
                self.cPid= cConnection.insert_id()


        if not self.cUid:
            if self.sqExecute([cConnection], cur,
                "INSERT INTO users (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
                self.parentDB.config.projectUser
            ):
                self.cUid= cConnection.insert_id()

        cur.close()

        if self.cUid!=None and self.cUid!=None:
            return cConnection




    def checkTables(self, _conn):
        if self.tablesPassed:
            return True

        cur= _conn.cursor()

        flagTablesAllOk= True

        for tName in self.dbTablesSrc:
            tableDesc= self.dbTablesSrc[tName]

            flagTableOk= True

            if not self.sqExecute([_conn], cur, "DESCRIBE `%s`" % tName):
                flagTablesAllOk= False
                continue

            fields= []

            for task in cur.fetchall():
                fields.append(task[0])

            for testField in tableDesc['fields']:
                testFieldName= testField.split()[0].strip('`')
                if not testFieldName in fields:
                    if self.sqExecute([_conn], cur, "ALTER TABLE " +tName +" ADD COLUMN " +testField):
                        print('TypeTodo MySQL: added `' +testFieldName +'` field into `' +tName +'` table')
                    else:
                        flagTableOk= False
                        flagTablesAllOk= False


            if not flagTableOk:
                if self.sqExecute([_conn], cur, "CREATE TABLE  `" +tName +"` (" +','.join(tableDesc['fields']+[tableDesc['suffix']]) +") DEFAULT CHARSET=utf8 ENGINE=MyISAM DELAY_KEY_WRITE=1"):
                    print('TypeTodo MySQL: created `' +tName +'` table')
                else:
                    print('TypeTodo: MySQL error, Table \'' +tName +'\' cannot be created')


        if flagTablesAllOk:
            cur.close()
            self.tablesPassed= True

            return True



#public#


    def flush(self):
        dbConn= [self.reconnect()]
        if not dbConn[0]:
            return False
        cur = dbConn[0].cursor()


        for iT in self.parentDB.todoA:
            curTodo= self.parentDB.todoA[iT]
            if not curTodo.savePending(self.dbId):
                continue

            curTodo.setSaved(SAVE_STATES.HOLD, self.dbId) #poke out from saving elsewhere

            for cState in STATE_LIST:
                if cState and cState[0]==curTodo.state:
                    break

            if not self.sqExecute(dbConn, cur,
                "INSERT INTO states (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
                (cState or STATE_DEFAULT)[1]
            ):
                return False
            db_stateId= dbConn[0].insert_id()

            if not self.sqExecute(dbConn, cur,
                "INSERT INTO files (name,id_project) VALUES (%s,%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
                (curTodo.fileName, self.cPid)
            ):
                return False
            db_fileId= dbConn[0].insert_id()

            db_tagIdA= []
            for tag in curTodo.tagsA: #insert all tags by one, holding 
                if not self.sqExecute(dbConn, cur,
                    "INSERT INTO categories (name,id_project) VALUES (%s,%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
                    (tag, self.cPid)
                ):
                    return False
                db_tagIdA.append(dbConn[0].insert_id())

            newVersion= 1
            newTagVersion= 1
            if not self.sqExecute(dbConn, cur,
                "SELECT max(version),max(version_tag) FROM tasks WHERE id=%s AND id_project=%s",
                (curTodo.id, self.cPid)
            ):
                return False
            recentTask= cur.fetchone()
            if recentTask and recentTask[0]:
                newVersion= recentTask[0]+1
                newTagVersion= recentTask[1]+1

            if not self.sqExecute(dbConn, cur,
                "INSERT INTO tasks (id,id_state,id_category,priority,id_user,version,id_filename,id_project,comment,stamp,version_tag) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,FROM_UNIXTIME(%s),%s)",
                (curTodo.id, db_stateId, db_tagIdA[0], curTodo.lvl, self.cUid, newVersion, db_fileId, self.cPid, curTodo.comment, curTodo.stamp, newTagVersion)
            ):
                return False

            tagOrder= 0
            for tagId in db_tagIdA:
                if not self.sqExecute(dbConn, cur,
                    "INSERT INTO tag2task (id_tag,id_task,version,`order`,id_project) VALUES (%s,%s,%s,%s,%s)",
                    (tagId, curTodo.id, newTagVersion, tagOrder, self.cPid)
                ):
                    return False
                tagOrder+= 1


            if curTodo.saveProgress(self.dbId): #edited-while-save todo will not become idle here
                curTodo.setSaved(SAVE_STATES.IDLE, self.dbId)

        cur.close()

        return True


    def newId(self, _wantedId=0):
        if _wantedId==self.lastId:
            return self.lastId

        dbConn= [self.reconnect()]
        if not dbConn[0]:
            return False
        cur = dbConn[0].cursor()

        if not self.sqExecute(dbConn, cur,
            "SELECT max(id) max_id FROM tasks WHERE id_project=%s",
            self.cPid
        ):
            return False
        _id= cur.fetchone()
        if _id and _id[0]:
            _id= int(_id[0]) +1
            if _wantedId>_id:
                _id= _wantedId
        else:
            _id= 1

        if not self.sqExecute(dbConn, cur,
            "INSERT INTO tasks (id,id_state,id_category,priority,id_user,version,id_filename,id_project,comment) VALUES (%s,0,0,0,%s,0,0,%s,'')",
            (_id, self.cUid, self.cPid)
        ):
            return False

        cur.close()

        self.lastId= _id
        return self.lastId



    def releaseId(self, _atExit=False):
        dbConn= [self.reconnect()]
        if not dbConn[0]:
            return False
        cur = dbConn[0].cursor()
        
        if not self.sqExecute(dbConn, cur,
            "SELECT max(id) max_id FROM tasks WHERE id_project=%s",
            self.cPid
        ):
            return False

        _id= cur.fetchone()
        if not _id:
            return False

        _id= int(_id[0])

        if not self.sqExecute(dbConn, cur,
            "SELECT max(version) FROM tasks WHERE id=%s AND id_project=%s",
            (_id, self.cPid)
        ):
            return False

        recentTask= cur.fetchone()
        if recentTask[0]>0: #release only reserved ones
            return False

        if not self.sqExecute(dbConn, cur,
            "DELETE FROM tasks WHERE id=%s AND id_project=%s",
            (_id, self.cPid)
        ):
            return False

#        if _id == self.lastId:
        self.lastId= None

        return True


    def fetch(self):
        dbConn= [self.reconnect()]
        if not dbConn[0]:
            return False
        cur = dbConn[0].cursor()

        if not self.sqExecute(dbConn, cur,
            "SELECT *, UNIX_TIMESTAMP(stamp) ustamp FROM (\
              SELECT id_project maxp,id maxi,max(version) maxv FROM tasks WHERE id_project=%s GROUP BY id\
            ) maxv INNER JOIN tasks ON id_project=maxp AND id=maxi AND version=maxv AND version>0\
            LEFT JOIN (SELECT id idproject, name nameproject FROM projects) _projects ON idproject=id_project\
            LEFT JOIN (SELECT id idstate, name namestate FROM states) _states ON idstate=id_state\
            LEFT JOIN (SELECT id idcat, name namecat FROM categories) _cats ON idcat=id_category\
            LEFT JOIN (SELECT id iduser, name nameuser FROM users) _users ON iduser=id_user\
            LEFT JOIN (SELECT id idfile, name namefile FROM files) _files ON idfile=id_filename",
            (self.cPid)
        ):
            return False

        sqn= {} #get id for field names
        for field in cur.description:
            sqn[field[0]]= len(sqn)

        todoA= {}
        ver_tags= {}
        for task in cur.fetchall():
            __id= int(task[sqn['id']])
            ver_tags[__id]= task[sqn['version_tag']]

            if __id not in todoA:
                todoA[__id]= TodoTask(__id, task[sqn['nameproject']], self.parentDB)

            fetchedStateName= task[sqn['namestate']]

            for cState in STATE_LIST:
                if cState and cState[1]==fetchedStateName:
                    break

            todoA[__id].set((cState or STATE_DEFAULT)[0], [task[sqn['namecat']]], task[sqn['priority']], task[sqn['namefile']], task[sqn['comment']], task[sqn['nameuser']], int(task[sqn['ustamp']]) )


        for taskId in todoA: #read multitags over
            multitags= []
            if not self.sqExecute(dbConn, cur,
                "SELECT nametag FROM tag2task \
                LEFT JOIN (SELECT id idtag, name nametag FROM categories) _tags ON idtag=id_tag\
                WHERE id_task=%s AND version=%s AND id_project=%s ORDER BY `order` ASC",
                (taskId, ver_tags[taskId], self.cPid)
            ):
                return False
            for tagnRow in cur.fetchall():
                multitags.append(tagnRow[0])

            if len(multitags)>0:
                todoA[taskId].setTags(multitags)

        return todoA
