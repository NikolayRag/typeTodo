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

    defaultHeader= "# uncomment and configure. ALL matched lines matters:\n"\
        +"# file filename.ext\n"\
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


        cSettings= self.readCfg(_cfgFile) or self.initGlobalDo()

        if cSettings:
            if self.lastCfgFile!=_cfgFile or self.lastProjectHeader!=cSettings[0].head:
                cSettings[0].file= _cfgFile #filename need TO save
                self.lastCfgFile= cSettings[0].file
                self.lastProjectHeader= cSettings[0].head

                self.settings= cSettings


                if not os.path.isfile(_cfgFile):
                    print ('TypeTodo init: Writing project\'s config.')
                    try:
                        with codecs.open(_cfgFile, 'w+', 'UTF-8') as f:
                            f.write(self.lastProjectHeader)
                            f.write("\n")
                    except:
                        None

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








    def readCfg(self, _cfgFile):
        try:
            f= codecs.open(_cfgFile, 'r', 'UTF-8')
        except:
            f= False
        if not f:
            return


        cSettings= []
        doSetting= Setting()
        cSettings.append(doSetting) #[0] will refer to .do itself; engine should be blank if overriden

        headerCollect= ''

        fileSetFound= False
        while True:
            l= f.readline().splitlines()
            if l==[] or l[0]=='' or not l[0]:
                break

            cfgString= l[0]

            headerCollect+= cfgString +"\n"
            #catch last matched config
            cfgFoundTry= RE_CFG.match(cfgString)
            if cfgFoundTry:
                cSetting= Setting()

                curCfg= cfgFoundTry.groupdict()
                if curCfg['enginefile']:
                    fileSetFound= True
                    cSetting.engine=    'file'
                    if os.path.dirname(curCfg['fname'])=='':
                        cSetting.file=  os.path.join(self.projectRoot, curCfg['fname'])
                    else:
                        cSetting.file=  curCfg['fname']
                    cSetting.head=      ''

                    if os.path.normcase(cSetting.file)==os.path.normcase(_cfgFile):
                        cSetting= False #prevent explicit .do as 'file'
                        fileSetFound= False


                if curCfg['enginesql']:
                    cSetting.engine=    'mysql'
                    cSetting.addr=      curCfg['addrs']
                    cSetting.login=     curCfg['logins']
                    cSetting.passw=     curCfg['passws']
                    cSetting.base=      curCfg['bases']


                if curCfg['enginehttp']:
                    cSetting.engine=    'http'
                    cSetting.addr=      curCfg['addrh']
                    cSetting.login=     curCfg['loginh']
                    cSetting.passw=     curCfg['passwh']
                    cSetting.base=      curCfg['baseh']


                if cSetting:
                    cSettings.append(cSetting)



        if not fileSetFound:
            doSetting.engine= 'file'

        doSetting.head= headerCollect
                   

        return cSettings








    def initGlobalDo(self, _force=False):
        _cfgFile= os.path.join(self.sublimeRoot, '.do')

        if not _force:
            cCfg= self.readCfg(_cfgFile)
            if cCfg:
                return cCfg


        cSettings= []
        doSetting= Setting()
        cSettings.append(doSetting) #[0] will refer to .do itself; engine should be blank if overriden
        doSetting.engine= 'file'

        headerCollect= self.defaultHeader

#=todo 1365 (cfg, fix, st3) +0: st3 repeats new http creation several times
        httpInitFlag= sublime.ok_cancel_dialog('TypeTodo init:\n\n\tStart with public HTTP base?')

        #request new random public repository
        if httpInitFlag:
            req = urllib2.Request('http://' +self.defaultHttpApi +'/?=newrep')
            try:
                cRep= bytes.decode( urllib2.urlopen(req).read() )

                print("New TypeTodo repository: " +cRep)
                sublime.set_timeout(lambda: sublime.status_message('New TypeTodo repository initialized'), 1000)

                cSetting= Setting()
                cSettings.append(cSetting)

                cSetting.engine= 'http'
                cSetting.addr= self.defaultHttpApi
                cSetting.base= cRep

                headerCollect+= cSetting.engine +" " +cSetting.addr +" " +cSetting.base +"\n"


            except:
                sublime.set_timeout(lambda: sublime.error_message('TypeTodo error:\n\tcannot init new HTTP repository,\n\tdefault storage mode will be `file`'), 1000)



        try:
            with codecs.open(_cfgFile, 'w+', 'UTF-8') as f:
                f.write(headerCollect)
        except:
            sublime.set_timeout(lambda: sublime.error_message('TypeTodo error:\n\tglobal config cannot be created'), 1000)
            return


        doSetting.head= headerCollect

        return cSettings


