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

    forceGlobal= False
    defaultHttpApi= 'typetodo.com',

    defaultHeader= "# uncomment and configure. LAST matched line matters:\n"\
        +"# mysql 127.0.0.1 username password scheme\n"\
        +"# http 127.0.0.1 repository [username password]\n"


    sublimePath= ''
    projectHeader= None

    projectUser= '**Anon'
    projectRoot= ''
    projectName= ''


    settings= None

    isUpdated= True

    #if inited global, would always be it
    def __init__(self, _forceGlobal=False):
        self.forceGlobal= _forceGlobal

        self.sublimePath= os.path.join(sublime.packages_path(), 'User')
        self.settings= {}

        self.update()



    def update(self):
        if 'USERNAME' in os.environ: self.projectUser= os.environ['USERNAME']

        self.projectRoot= self.sublimePath
        self.projectName= ''

        if not self.forceGlobal:
            projFolders= sublime.active_window().folders()
            if len(projFolders):
                self.projectRoot= projFolders[0]
                self.projectName= os.path.split(projFolders[0])[1]

#=todo 860 (cfg) +0: handle error
        doFile= os.path.join(self.projectRoot, self.projectName +'.do')
        if not self.readCfg(doFile):
            if self.initGlobalDo() and not self.forceGlobal and len(projFolders):
#=todo 861 (cfg) +0: save cfg to project
                None

        wasUpdated= self.isUpdated
        self.isUpdated= False
        return wasUpdated



#todo 241 (cfg, file) +5: enable to define separate file for TODOs, to split DB credentials from file db itself
#=todo 334 (cfg) +1: catch cfg errors

    def readCfg(self, _doFile):
        try:
            f= codecs.open(_doFile, 'r', 'UTF-8')
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

        cSettings.file= _doFile
        cSettings.head= headerCollect

        if self.projectHeader != headerCollect:
            self.isUpdated= True

        self.projectHeader= headerCollect
        self.settings[0]= cSettings
        return True

#   'header'
#   'file'

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

            headerCollect= defaultHeader +cSettings.engine +" " +cSettings.addr +" " +cSettings.base +"\n"

            sublime.set_timeout(lambda: sublime.status_message('New TypeTodo repository initialized'), 1000)


        if self.projectHeader != headerCollect:
            self.isUpdated= True

        self.projectHeader= headerCollect
        self.settings[0]= cSettings

        try:
            cfgFile= os.path.join(self.sublimePath, '.do')
            with codecs.open(cfgFile, 'w+', 'UTF-8') as f:
                f.write(self.projectHeader)
        except:
            return False

        return True


