# coding= utf-8

import sublime, sublime_plugin
import re, os, time, codecs

from dbFile import *
from dbSql import *
from dbHttp import *



#-todo 26 (db) +0: move todo array management to base TodoDb class


#todo 44 (config) +0: handle saving project - existing and blank
#todo 47 (config) +0: define config sequence

#todo 30 (doc) +0: config is taken: 1. project.todo first string, (2. global .todo first string), (3. env variables), (4. hardcoded)
#todo 31 (doc) +0: config string format: mysql [host] [log] [pas] [scheme] [table]


'''
   per-project task set
   Read config and set up db engine
'''

class TodoDb():

    projUser= '*Anon*'
    projRoot= ''
    projName= ''

    cfgA= None

    db= None
    todoA= None

    reCfg= re.compile("^\s*(?:((?P<engine>mysql) (?P<addr>[^\s]+) (?P<login>[^\s]+) (?P<passw>[^\s]+) (?P<scheme>[^\s]+)))\s*$")
#    reCfg= re.compile("^\s*(?:(mysql ([^\s]+) ([^\s]+) ([^\s]+) ([^\s]+))|(http ([^\s]+) ([^\s]+) ([^\s]+)))\s*$")

    def __init__(self, _root, _name):
        self.update(_root, _name)
        self.reset()


    def update(self, _root, _name):
        if 'USERNAME' in os.environ: self.projUser= os.environ['USERNAME']

        self.projRoot= _root
        self.projName= _name


    def reset(self):
        cfgPath= os.path.join(self.projRoot, self.projName +'.todo')

        cfgFound= {'engine': 'file'}
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
                        cfgFound= cfgFoundTry.groupdict()

        except:
            cfgHeaderStrings= "# uncomment and configure. LAST matched line matters:\n"\
              +"# mysql 127.0.0.1 username password scheme\n"

        if cfgFound == self.cfgA:
            return


#todo 55 (config) +5: delayed: flush (existing) before reset db[engine]
        self.cfgA= cfgFound
        self.todoA= {}

        if cfgFound['engine']== 'mysql':
            self.db= TodoDbSql(self.todoA, self.projUser, self.projName, cfgFound['addr'], cfgFound['login'], cfgFound['passw'], cfgFound['scheme'])
#        elif cfgFound['engine']== 'http':
#            return
        else:
            self.db= TodoDbFile(self.todoA, self.projUser, self.projName, cfgPath, cfgHeaderStrings) #throw in sfgString to restore it in file




    def store(self, _id, _state, _cat, _lvl, _fileName, _comment):

#todo 27 (db) +0: handle delayed update
#todo 29 (db) +0: New tasks Id assigning should NOT be delayed. Or yes? 
#todo 28 (db) +0: make cached access: read task from db as its needed
        self.reset()




        if _fileName and self.projRoot:
            _fileName= os.path.relpath(_fileName, self.projRoot)

        return self.db.store(_id, _state, _cat, _lvl, _fileName or '', _comment)



