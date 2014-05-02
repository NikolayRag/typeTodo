# coding= utf-8

#-todo 7 (db) +0: engine: httpdb


class TodoDbHttp():
    todoA= None
    projectName= ''
    userName= ''


#todo 18 (config) +0: assign default unique http id at very start

    #db related


    def __init__(self, _todoA, _uname, _name):
        self.todoA= _todoA
        self.userName= _uname
        self.projectName= _name



    def store(self, _id, _state, _cat, _lvl, _fileName, _comment):
        return 0

