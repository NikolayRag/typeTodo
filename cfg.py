# coding= utf-8

import sublime
import sys, re, os, time, codecs

if sys.version < '3':
    import urllib2, urllib
else:
    import urllib.request as urllib2
    import urllib.parse as urllib

if sys.version < '3':
    from c import *
else:
    from .c import *


class Setting:
    engine= ''
    addr=   ''
    login=  ''
    passw=  ''
    base=   ''
    file=   ''
    head=   ''

#check for:
#   first, subsequent window
#   open existing, unexistent
#   local, global, global unexistent
#   

class Config():
    sublimeRoot= ''
    isGlobal= False

    cWnd= None
    defaultHttpApi= 'typetodo.com'

    defaultHeader= "# uncomment and configure. LAST matched line matters:\n"\
        +"# mysql 127.0.0.1 username password scheme\n"\
        +"# http typetodo.com repository [username password]\n"



    projectUser= '**Anon'
    projectRoot= ''
    projectName= ''


    settings= None

    lastProjectFolders= []
    lastProjectHeader= None
    lastCfgFile= None

    
    def __init__(self, _forceGlobal=False):
        self.isGlobal= _forceGlobal

        self.cWnd= sublime.active_window()
        self.sublimeRoot= os.path.join(sublime.packages_path(), 'User')

        self.update()







    def update(self):
        if 'USERNAME' in os.environ: self.projectUser= os.environ['USERNAME']

        self.projectRoot= self.sublimeRoot
        self.projectName= ''

        if not self.isGlobal:
            if self.isWindowExists(): #should skip 'coz secondary window will return [] as it closes
                self.lastProjectFolders= self.cWnd.folders()

            if len(self.lastProjectFolders):
                self.projectRoot= self.lastProjectFolders[0]
                self.projectName= os.path.split(self.lastProjectFolders[0])[1]

        _cfgFile= os.path.join(self.projectRoot, self.projectName +'.do')


        cSettings= None
        cSettings= self.readCfg(_cfgFile)
        if not cSettings:
            cSettings= self.initGlobalDo()



        if cSettings:
            if self.lastCfgFile!=_cfgFile or self.lastProjectHeader!=cSettings.head:
                cSettings.file= _cfgFile
                self.lastCfgFile= cSettings.file
                self.lastProjectHeader= cSettings.head

                self.settings= {}
                self.settings[0]= cSettings

                return True
            return

        print ('TypeTodo error: Config could not be read.')
        self.lastCfgFile= None
        self.lastProjectHeader= None




    def isWindowExists(self):
        if sys.version<'3':
            if self.cWnd.id():
                return True
        else:
            if self.cWnd.project_data():
                return True






#=todo 149 (cfg, feature) +5: make use of more than one (last) cfg string
#=todo 170 (cfg, refactor) +0: build list of cfg's to pass to db.reset()

#=todo 241 (cfg, file, feature) +5: enable to define separate file for TODOs, to split DB settings from file db itself
    def readCfg(self, _cfgFile):
        try:
            f= codecs.open(_cfgFile, 'r', 'UTF-8')
        except:
            f= False
        if not f:
            return


        cSettings= Setting()
        headerCollect= ''

        while True:
            l= f.readline().splitlines()
            if l==[] or l[0]=='' or not l[0]:
                break

            cfgString= l[0]

            headerCollect+= cfgString +"\n"
            #catch last matched config
            cfgFoundTry= RE_CFG.match(cfgString)
            if cfgFoundTry:
                curCfg= cfgFoundTry.groupdict()
                if curCfg['enginesql']:
                    cSettings.engine=   curCfg['enginesql']
                    cSettings.addr=     curCfg['addrs']
                    cSettings.login=    curCfg['logins']
                    cSettings.passw=    curCfg['passws']
                    cSettings.base=     curCfg['bases']
                elif curCfg['enginehttp']:
                    cSettings.engine=   curCfg['enginehttp']
                    cSettings.addr=     curCfg['addrh']
                    cSettings.login=    curCfg['loginh']
                    cSettings.passw=    curCfg['passwh']
                    cSettings.base=     curCfg['baseh']

        cSettings.head= headerCollect

        return cSettings








    def initGlobalDo(self, _force=False):
        _cfgFile= os.path.join(self.sublimeRoot, '.do')

        if not _force:
            cCfg= self.readCfg(_cfgFile)
            if cCfg:
                return cCfg


        cSettings= Setting()
        headerCollect= self.defaultHeader

        httpInitFlag= sublime.ok_cancel_dialog('TypeTodo init:\n\n\tStart with public HTTP base?')

        #request new random public repository
        if httpInitFlag:
            req = urllib2.Request('http://' +self.defaultHttpApi +'/?=newrep')
            try:
                cRep= bytes.decode( urllib2.urlopen(req).read() )

                print("New TypeTodo repository: " +cRep)
                sublime.set_timeout(lambda: sublime.status_message('New TypeTodo repository initialized'), 1000)

                cSettings.engine= 'http'
                cSettings.addr= self.defaultHttpApi
                cSettings.base= cRep

                headerCollect+= cSettings.engine +" " +cSettings.addr +" " +cSettings.base +"\n"


            except:
                sublime.set_timeout(lambda: sublime.error_message('TypeTodo error:\n\tcannot init new HTTP repository,\n\tdefault storage mode will be `file`'), 1000)



        try:
            with codecs.open(_cfgFile, 'w+', 'UTF-8') as f:
                f.write(headerCollect)
        except:
            sublime.set_timeout(lambda: sublime.error_message('TypeTodo error:\n\tglobal config cannot be created'), 1000)
            return



        cSettings.head= headerCollect

        return cSettings


