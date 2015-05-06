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
    projectUser= ''
    projectRoot= ''
    projectName= ''


class Config():
    sublimeRoot= ''
    cfgFile= ''

    cWnd= None
    forceGlobal= False
    defaultHttpApi= 'typetodo.com'

    defaultHeader= "# uncomment and configure. LAST matched line matters:\n"\
        +"# mysql 127.0.0.1 username password scheme\n"\
        +"# http 127.0.0.1 repository [username password]\n"



    projectUser= '**Anon'
    projectRoot= ''
    projectName= ''


    settings= None

    projectHeader= None
    isUpdated= True

    #if inited global, would always be it
    def __init__(self, _forceGlobal=False):
        self.forceGlobal= _forceGlobal

        self.cWnd= sublime.active_window()
        self.sublimeRoot= os.path.join(sublime.packages_path(), 'User')
        self.settings= {}

        self.updateFName()



    def update(self):
        self.updateFName()
#=todo 860 (cfg) +0: handle error
        print('TT: opening ' +self.cfgFile +' for window ' +str(self.cWnd.id()))
        if not self.readCfg():
            print('TT: error no cfg')
            if self.initGlobalDo() and not self.forceGlobal and self.projectName!='':
#=todo 861 (cfg) +0: save cfg to project
                print('TT: error no global')

        wasUpdated= self.isUpdated
        self.isUpdated= False
        return wasUpdated


    lastProjFolder= ''

    def isWindowExists(self):
        if sys.version<'3':
            if self.cWnd.id():
                return True
        else:
            if self.cWnd.project_data():
                return True

    def updateFName(self):
        if 'USERNAME' in os.environ: self.projectUser= os.environ['USERNAME']

        self.projectRoot= self.sublimeRoot
        self.projectName= ''

        if not self.forceGlobal:
            if self.isWindowExists():
                self.lastProjFolder= self.cWnd.folders() #this is delayed for secondary windows, but works here
                   
            projFolders= self.lastProjFolder
            print ('TTF: ' +str(projFolders))

            if len(projFolders):
                self.projectRoot= projFolders[0]
                self.projectName= os.path.split(projFolders[0])[1]

        self.cfgFile= os.path.join(self.projectRoot, self.projectName +'.do')


#todo 241 (cfg, file) +5: enable to define separate file for TODOs, to split DB credentials from file db itself
#=todo 334 (cfg) +1: catch cfg errors

    def readCfg(self):
        try:
            f= codecs.open(self.cfgFile, 'r', 'UTF-8')
        except:
            f= False
        if not f:
            return False

        cSettings= Setting()
        cSettings.projectUser= self.projectUser
        cSettings.projectRoot= self.projectRoot
        cSettings.projectName= self.projectName

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

        cSettings.file= self.cfgFile
        cSettings.head= headerCollect

        if self.projectHeader != headerCollect:
            self.isUpdated= True

        self.projectHeader= headerCollect
        self.settings[0]= cSettings
        return True


#=todo 351 (cfg) +0: allow skip global configure for HTTP at first start

    def initGlobalDo(self):
        httpInitFlag= True

        #request new radnom public repository
        if httpInitFlag:
            req = urllib2.Request('http://' +self.defaultHttpApi +'/?=newrep')
            try:
                cRep= bytes.decode( urllib2.urlopen(req).read() )
            except:
                httpInitFlag= False


        cSettings= Setting()
        headerCollect= ''

        if not httpInitFlag:
            sublime.set_timeout(lambda: sublime.error_message('TypeTodo error:\n\tcannot init new HTTP repository,\n\tdefault storage mode will be `file`'), 1000)
        else:
            print("New TypeTodo repository: " +cRep)

            cSettings.engine= 'http'
            cSettings.addr= self.defaultHttpApi
            cSettings.base= cRep

            headerCollect= self.defaultHeader +cSettings.engine +" " +cSettings.addr +" " +cSettings.base +"\n"

            sublime.set_timeout(lambda: sublime.status_message('New TypeTodo repository initialized'), 1000)


        if self.projectHeader != headerCollect:
            self.isUpdated= True

        self.projectHeader= headerCollect
        self.settings[0]= cSettings

        try:
            cfgFile= os.path.join(self.sublimeRoot, '.do')
            with codecs.open(cfgFile, 'w+', 'UTF-8') as f:
                f.write(self.projectHeader)
        except:
            return False

        return True


