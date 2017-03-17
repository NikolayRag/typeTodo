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


#  todo 2142 (http, config) +0: allow to specify project name in http config: {site} {rep} [{log} {pass}] [{proj}]
#  todo 2143 (http, api, config) +0: request id name from server to fill back project name

# =todo 2181 (config, feature, migration) +0: copy config to .do.cfg json file

class Setting:
    engine= ''



#check for:
#   first, subsequent window
#   open existing, unexistent
#   local, global, global unexistent
#   
'''
Manage config for current project.
'''
class Config():
    sublimeRoot= ''

    defaultHttpApi= 'typetodo.com'

    defaultHeader= "# Uncomment and configure.\n"\
        +"# file [absolute_path/]filename.ext\n"\
        +"# mysql 127.0.0.1 username password scheme\n"\
        +"# http typetodo.com repository [username password]\n"



    projectUser= '**Anon'
    projectRoot= ''
    projectName= ''


    settings= None

    globalInited= False

    lastProjectHeader= None
    lastCfgFile= None

    
    def __init__(self, _projectFolder=''):
        self.sublimeRoot= os.path.join(sublime.packages_path(), 'User')

        self.projectRoot= self.sublimeRoot
        self.projectName= ''

        if _projectFolder!='':
            self.projectRoot= _projectFolder
            self.projectName= os.path.split(_projectFolder)[1]

        self.update()





    '''
    (Re)read config from project-related or global config
    '''
    def update(self):
        if 'USERNAME' in os.environ: self.projectUser= os.environ['USERNAME']

        _cfgFile= os.path.join(self.projectRoot, self.projectName +'.do')


# -todo 2150 (config) +0: ask to init projects config with global if none yet
        cSettings= self.readCfg(_cfgFile) or self.initGlobalDo()

        if cSettings:
            if self.lastCfgFile!=_cfgFile or self.lastProjectHeader!=cSettings[0].head:
                cSettings[0].file= _cfgFile #filename need TO save
                self.lastCfgFile= cSettings[0].file
                self.lastProjectHeader= cSettings[0].head

                self.settings= cSettings


                if not os.path.isfile(_cfgFile):
                    print('TypeTodo init: Writing project\'s config.')

                    try:
                        with codecs.open(_cfgFile, 'w+', 'UTF-8') as f:
                            f.write(self.lastProjectHeader)
                            f.write("\n")
                    except:
                        None

                return True
            return

        print('TypeTodo error: Config could not be read.')
        self.lastCfgFile= None
        self.lastProjectHeader= None






########
#PRIVATE
########




    '''
    Read specified config file.
    '''
    def readCfg(self, _cfgFile, _oldCfg=None):
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
            cfgString= f.readline()
            if cfgString=='' or cfgString=="\n" or cfgString=="\r\n":
                break
            
            headerCollect+= cfgString
            #catch last matched config
            cfgFoundTry= RE_CFG.match(cfgString.rstrip('\n'))


            if not cfgFoundTry:
                continue

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

                if not os.path.isfile(cSetting.file):
                    with codecs.open(cSetting.file, 'w+', 'UTF-8') as fNew:
                        fNew.write('')   


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






    def initNewHTTP(self):
        req = urllib2.Request('http://' +self.defaultHttpApi +'/?=new_rep_public')
        try:
            cRep= bytes.decode( urllib2.urlopen(req).read() )
        except:
            sublime.set_timeout(lambda: sublime.error_message('TypeTodo error:\n\n\tcannot init new HTTP repository,\n\tdefault storage mode will be `file`'), 1000)

            return False

        print("New TypeTodo repository: " +cRep)
        sublime.set_timeout(lambda: sublime.status_message('New TypeTodo repository initialized'), 1000)

        cSetting= Setting()
        cSetting.engine= 'http'
        cSetting.addr= self.defaultHttpApi
        cSetting.base= cRep
        cSetting.login= cSetting.passwh= ''

        return cSetting



    def initGlobalDo(self, _force=False):
        _cfgFile= os.path.join(self.sublimeRoot, '.do')

        if not _force:
            cCfg= self.readCfg(_cfgFile)
            if cCfg:
                return cCfg


        self.globalInited= True

        cSettings= []
        doSetting= Setting()
        cSettings.append(doSetting)
        doSetting.engine= 'file'

        headerCollect= self.defaultHeader



        httpCfg= self.initNewHTTP()
        if httpCfg:
            headerCollect+= httpCfg.engine +" " +httpCfg.addr +" " +httpCfg.base +"\n"
            doSetting.head= headerCollect

            cSettings.append(httpCfg)


        try:
            with codecs.open(_cfgFile, 'w+', 'UTF-8') as f:
                f.write(headerCollect)
        except:
            sublime.set_timeout(lambda: sublime.error_message('TypeTodo error:\n\n\tglobal config cannot be created'), 1000)
            return


        return cSettings


