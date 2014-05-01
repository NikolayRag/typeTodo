# coding= utf-8

import sublime, sublime_plugin
import re, os, time, codecs

from dbFile import *
from dbSql import *
from dbHttp import *




#-todo 26 (db) +0: move todo array management to base TodoDb class

#todo 27 (db) +0: handle delayed update
#todo 29 (db) +0: New tasks Id assigning should NOT be delayed. Or yes? 
#todo 28 (db) +0: make cached access: read task from db as its needed

#   Project-assigned task set
#   Read config and set up db engine

class TodoDb():

    db= None
    todoA= None

    reCfg= re.compile("^\s*(?:(mysql ([^\s]+) ([^\s]+) ([^\s]+) ([^\s]+)))\s*$")
#    reCfg= re.compile("^\s*(?:(mysql ([^\s]+) ([^\s]+) ([^\s]+) ([^\s]+))|(http ([^\s]+) ([^\s]+) ([^\s]+)))\s*$")

    def __init__(self, _root, _name):
        self.todoA= {}

        uname= '*Anon*'
        if 'USERNAME' in os.environ: uname= os.environ['USERNAME']

        cfgPath= os.path.join(_root, _name +'.todo')

        cfgFound= None
        cfgHeaderStrings= ''

        try:
            with codecs.open(cfgPath, 'r', 'UTF-8') as f:
                while True:
                    cfgString= f.readline().splitlines()[0] #db config be here
                    if cfgString == '' or not cfgString:
                        break

                    cfgHeaderStrings+= cfgString +"\n"
                    #catch last matched config
                    cfgFoundTry= self.reCfg.match(cfgString)
                    if cfgFoundTry:
                        cfgFound= cfgFoundTry

        except:
            cfgHeaderStrings= "# uncomment and configure. LAST matched line matters:\n"\
              +"# mysql 127.0.0.1 username password scheme\n"


#todo 30 (doc) +0: config is taken: 1. project.todo first string, (2. global .todo first string), (3. env variables), (4. hardcoded)
#todo 31 (doc) +0: config string format: 1. '' - full, 2. 'mysql [host] [log] [pas] [scheme] [table]', (3. 'http [host] [repId] [pass]'), (4. 'breef; ...' for duplication)


        if cfgFound and cfgFound.group(1): #db: mysql
            dbAddr= cfgFound.group(2)
            dbUname= cfgFound.group(3)
            dbPass= cfgFound.group(4)
            dbScheme= cfgFound.group(5)

            self.db= TodoDbSql(self.todoA, uname, _name, dbAddr, dbUname, dbPass, dbScheme)

#        elif cfgFound and cfgFound.group(6): #db: http

        else: #db: file
            self.db= TodoDbFile(self.todoA, uname, _name, cfgPath, cfgHeaderStrings) #throw in sfgString to restore it in file



    def store(self, _id, _state, _cat, _lvl, _fileName, _comment):
        return self.db.store(_id, _state, _cat, _lvl, _fileName, _comment)



