# coding= utf-8

'''
scratch of organizing smooth per-project id assigning for (un)registered users at HTTP

unregistered:
1. at .do creation it is assigned unique hash ID from SITE. So it being per-project.
2. any access to SITE using that ID is granted to anon

registered:
0. user can secure his ID's by applying his hash (username+pass) in config
1. same as unregistered.1
2. any access to SITE using that ID is specified by user
'''

#-todo 7 (db) +0: engine: httpdb

import urllib2, urllib

class TodoDbHttp():
    todoA= None
    projectName= ''
    userName= ''

    httpAddr= ''
    httpUname= ''
    httpPass= ''
    httpScheme= ''

#todo 18 (config) +0: assign default unique http id at very start

    #db related


    def __init__(self, _todoA, _uname, _name, _httpAddr, _httpUname, _httpPass, _httpRepository):
        self.todoA= _todoA
        self.userName= _uname
        self.projectName= _name

        self.httpAddr= _httpAddr
        self.httpUname= _httpUname
        self.httpPass= _httpPass
        self.httpRepository= _httpRepository


    def flush(self):
#todo 77 (http) +0: make post request json
        postData= {}
        postList= list()
        for iT in self.todoA:
            curTodo= self.todoA[iT]
            if curTodo.saved: continue

            postList.append(str(curTodo.id))
            postData['state' +str(curTodo.id)]= str(curTodo.state)
            postData['file' +str(curTodo.id)]= curTodo.fileName
            postData['cat' +str(curTodo.id)]= curTodo.cat
            postData['lvl' +str(curTodo.id)]= curTodo.lvl
            postData['comm' +str(curTodo.id)]= curTodo.comment

#todo 78 (http) +0: use actual http result
            curTodo.setSaved()

        postData['ids']= ','.join(postList)
        req = urllib2.Request('http://' +self.httpAddr +'/?flush&user=' +self.userName +'&project=' +self.projectName, urllib.urlencode(postData))
        try:
            response = urllib2.urlopen(req).read()
            print response
            return True
        except:
            return False

    def newId(self):
        req = urllib2.Request('http://' +self.httpAddr +'/?newid&user=' +self.userName +'&project=' +self.projectName)
        response = urllib2.urlopen(req).read()
        return response
