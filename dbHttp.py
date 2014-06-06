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


flow:

- each http request specifies projects/tasks repository by hash (public)
    OR by username (secured)
- each rep hold number of projects

public rep:
- rep is initialised by requesting name from server (at config)
- repository can be accessed anonymously, both reading and writing.
    *The ONLY protection from intrusion so far is hash complexity (xx-byte?)
- project accessed by specifying rep hash and project name within rep

secured rep:
- rep is initialised by creating on server/requesting while logged
- rep is accessed by owner only (by default)
- rep access can be expanded by owner

either:
- task editor name specified by rather an plain text (anon) or by logged user id

'''

import urllib2, urllib

class TodoDbHttp():
    todoA= None
    projectName= ''
    userName= ''

    httpAddr= ''
    httpUname= ''
    httpPass= ''
    httpScheme= ''

#todo 18 (config) +0: assign default unique rep id at very start

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
        postData['user']= self.userName
#todo 79 (http) +0: turn on unicode
        req = urllib2.Request('http://' +self.httpAddr +'/flush.php?rep=' +self.httpRepository +'&project=' +self.projectName, urllib.urlencode(postData))
        try:
            response = urllib2.urlopen(req).read()
            return True
        except:
            return False

# reserve new db entry
# returned value:
#   int:    new id

    def newId(self):
        postData= {}
        postData['user']= self.userName
        req = urllib2.Request('http://' +self.httpAddr +'/newid.php?rep=' +self.httpRepository +'&project=' +self.projectName, urllib.urlencode(postData))
        try:
            response= urllib2.urlopen(req).read()
        except:
            response= False;
        return response
