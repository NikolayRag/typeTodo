#-todo 6 (db) +0: engine: sql

class TodoDbSql():
    projectName= ''
    userName= ''


    #db related
    dbAddr= ''
    dbScheme= 'todos'
    dbUname= ''
    dbPass= ''


    def __init__(self, _uname, _name):
        self.userNname= _uname
        self.projectName= _name

        if 'TODO_DB_ADDR' in os.environ: self.dbAddr= os.environ['TODO_DB_ADDR']
        if 'TODO_DB_SCHEME' in os.environ: self.dbScheme= os.environ['TODO_DB_SCHEME']
        if 'TODO_DB_UNAME' in os.environ: self.dbUname= os.environ['TODO_DB_UNAME']
        if 'TODO_DB_PASS' in os.environ: self.dbPass= os.environ['TODO_DB_PASS']


    def store(self, _id, _state, _cat, _lvl, _fileName, _comment):
        return 0

