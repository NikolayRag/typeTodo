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


    def __init__(self, _parentDB, _settings):
        self.settings= _settings
        self.parentDB= _parentDB


    def reconnect(self):
        try:
            cConnection= pymysql.connect(host=self.settings.addr, port=3306, user=self.settings.login, passwd=self.settings.passw, db=self.settings.base, use_unicode=True, charset="utf8")
            cConnection.autocommit(True)
        except Exception as e:
#todo 35 (sql, cleanup) +0: deal with connection errors: host, log, scheme
            print('TypeTodo: MySQL error, Sql connection cannot be established, check MySQL settings:')
            print(e)
            return False

        #check table
        cur = cConnection.cursor()
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
                    if not testFieldName in fields:
                        cur.execute("ALTER TABLE " +tName +" ADD COLUMN " +testField)
                        print('TypeTodo MySQL: added `' +testFieldName +'` field into `' +tName +'` table')
            except:
                flagTableOk= False

            if not flagTableOk:
                try:
                    cur.execute("CREATE TABLE  `" +tName +"` (" +','.join(tableDesc['fields']+[tableDesc['suffix']]) +") DEFAULT CHARSET=utf8 ENGINE=MyISAM DELAY_KEY_WRITE=1")
                    print('TypeTodo MySQL: created `' +tName +'` table')
                except Exception as e:
                    print('TypeTodo: MySQL error, Table \'' +tName +'\' cannot be created:')
                    print(e)
                    return False

        cur.execute(
            "INSERT INTO projects (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
            self.parentDB.config.projectName
        )
        cPid= cConnection.insert_id()


        cur.execute(
            "INSERT INTO users (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
            self.parentDB.config.projectUser
        )
        cUid= cConnection.insert_id()

        cur.close()

        return {'db': cConnection, 'pid': cPid, 'uid': cUid}


#public#


    def flush(self, _dbN):
        dbConn= self.reconnect()
        if not dbConn:
            return False
        cur = dbConn['db'].cursor()


        for iT in self.parentDB.todoA:
            curTodo= self.parentDB.todoA[iT]
            if not curTodo.savePending(_dbN):
                continue

            curTodo.setSaved(SAVE_STATES.HOLD, _dbN) #poke out from saving elsewhere

            cur.execute(
                "INSERT INTO states (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
                STATE_LIST[curTodo.state]
            )
            db_stateId= dbConn['db'].insert_id()

            cur.execute(
                "INSERT INTO files (name,id_project) VALUES (%s,%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
                (curTodo.fileName, dbConn['pid'])
            )
            db_fileId= dbConn['db'].insert_id()

            db_tagIdA= []
            for tag in curTodo.tagsA: #insert all tags by one, holding 
                cur.execute(
                    "INSERT INTO categories (name,id_project) VALUES (%s,%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
                    (tag, dbConn['pid'])
                )
                db_tagIdA.append(dbConn['db'].insert_id())

            newVersion= 1
            newTagVersion= 1
            cur.execute(
                "SELECT max(version),max(version_tag) FROM tasks WHERE id=%s AND id_project=%s",
                (curTodo.id, dbConn['pid'])
            )
            recentTask= cur.fetchone()
            if recentTask and recentTask[0]:
                newVersion= recentTask[0]+1
                newTagVersion= recentTask[1]+1

            cur.execute(
                "INSERT INTO tasks (id,id_state,id_category,priority,id_user,version,id_filename,id_project,comment,stamp,version_tag) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,FROM_UNIXTIME(%s),%s)",
                (curTodo.id, db_stateId, db_tagIdA[0], curTodo.lvl, dbConn['uid'], newVersion, db_fileId, dbConn['pid'], curTodo.comment, curTodo.stamp, newTagVersion)
            )

            tagOrder= 0
            for tagId in db_tagIdA:
                cur.execute(
                    "INSERT INTO tag2task (id_tag,id_task,version,`order`,id_project) VALUES (%s,%s,%s,%s,%s)",
                    (tagId, curTodo.id, newTagVersion, tagOrder, dbConn['pid'])
                )
                tagOrder+= 1

            #todo 285 (sql, cleanup) +0: detect sql saving error
            if curTodo.saveProgress(_dbN): #edited-while-save todo will not become idle here
                curTodo.setSaved(SAVE_STATES.IDLE, _dbN)

        cur.close()

        return True


    def newId(self, _wantedId=0):
        if _wantedId==self.lastId:
            return self.lastId

        dbConn= self.reconnect()
        if not dbConn:
            return False
        cur = dbConn['db'].cursor()

        cur.execute(
            "SELECT max(id) max_id FROM tasks WHERE id_project=%s",
            dbConn['pid']
        )
        _id= cur.fetchone()
        if _id and _id[0]:
            _id= int(_id[0]) +1
            if _wantedId>_id:
                _id= _wantedId
        else:
            _id= 1

        cur.execute(
            "INSERT INTO tasks (id,id_state,id_category,priority,id_user,version,id_filename,id_project,comment) VALUES (%s,0,0,0,%s,0,0,%s,'')",
            (_id, dbConn['uid'], dbConn['pid'])
        )

        cur.close()

        self.lastId= _id
        return self.lastId



    def releaseId(self):
        dbConn= self.reconnect()
        if not dbConn:
            return False

        cur = dbConn['db'].cursor()

        cur.execute(
            "SELECT max(id) max_id FROM tasks WHERE id_project=%s",
            dbConn['pid']
        )

        _id= cur.fetchone()
        if not _id:
            return False

        _id= int(_id[0])
        if not _id or _id != self.lastId:
            return False

        cur.execute(
            "SELECT max(version) FROM tasks WHERE id=%s AND id_project=%s",
            (_id, dbConn['pid'])
        )

        recentTask= cur.fetchone()
        if recentTask[0]>0:
            return False

        cur.execute(
            "DELETE FROM tasks WHERE id=%s AND id_project=%s",
            (_id, dbConn['pid'])
        )

        self.lastId= None


    def fetch(self):
        dbConn= self.reconnect()
        if not dbConn:
            return False
        cur = dbConn['db'].cursor()

        cur.execute(
            "SELECT *, UNIX_TIMESTAMP(stamp) ustamp FROM (\
              SELECT id_project maxp,id maxi,max(version) maxv FROM tasks WHERE id_project=%s GROUP BY id\
            ) maxv INNER JOIN tasks ON id_project=maxp AND id=maxi AND version=maxv AND version>0\
            LEFT JOIN (SELECT id idproject, name nameproject FROM projects) _projects ON idproject=id_project\
            LEFT JOIN (SELECT id idstate, name namestate FROM states) _states ON idstate=id_state\
            LEFT JOIN (SELECT id idcat, name namecat FROM categories) _cats ON idcat=id_category\
            LEFT JOIN (SELECT id iduser, name nameuser FROM users) _users ON iduser=id_user\
            LEFT JOIN (SELECT id idfile, name namefile FROM files) _files ON idfile=id_filename",
            (dbConn['pid'])
        )

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

            stateIdx= ''
            for cState in STATE_LIST:
                if STATE_LIST[cState]==fetchedStateName:
                    stateIdx= cState
                    break

            todoA[__id].set(stateIdx, [task[sqn['namecat']]], task[sqn['priority']], task[sqn['namefile']], task[sqn['comment']], task[sqn['nameuser']], int(task[sqn['ustamp']]) )


        for taskId in todoA: #read multitags over
            multitags= []
            cur.execute(
                "SELECT nametag FROM tag2task \
                LEFT JOIN (SELECT id idtag, name nametag FROM categories) _tags ON idtag=id_tag\
                WHERE id_task=%s AND version=%s AND id_project=%s ORDER BY `order` ASC",
                (taskId, ver_tags[taskId], dbConn['pid'])
            )
            for tagnRow in cur.fetchall():
                multitags.append(tagnRow[0])

            if len(multitags)>0:
                todoA[taskId].setTags(multitags)

        return todoA
