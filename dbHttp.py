#-todo 7 (db) +0: engine: httpdb


class TodoDbHttp():
    projectName= ''
    userName= ''


#todo 18 (config) +0: assign default unique http id at very start

    #db related


    def __init__(self, _uname, _name):
        self.userName= _uname
        self.projectName= _name



    def store(self, _id, _state, _cat, _lvl, _fileName, _comment):
        return 0

