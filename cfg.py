# coding= utf-8

import sublime
import sys, re, os, time, codecs, json

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


class SettingFile(Setting):
    file=      ''

    def __init__(self, file=''):
        self.engine=    'file'
        self.file= file


class SettingMysql(Setting):
    addr=      ''
    base=      ''
    login=     ''
    passw=     ''

    def __init__(self, addr='', base='', login='', passw=''):
        self.engine=    'mysql'
        self.addr= addr
        self.base= base
        self.login= login
        self.passw= passw


class SettingHttp(Setting):
    addr=      ''
    login=     ''
    passw=     ''
    base=      ''

    def __init__(self, addr='', base='', login='', passw=''):
        self.engine=    'http'
        self.addr= addr
        self.base= base
        self.login= login
        self.passw= passw




#check for:
#   first, subsequent window
#   open existing, unexistent
#   local, global, global unexistent
#   
'''
Manage config for current project.
'''
class Config():
    sublimeRoot= os.path.join(sublime.packages_path(), 'User')
    globalFileName= os.path.join(sublimeRoot, '.do.cfg')
    globalLegacyFn= os.path.join(sublimeRoot, '.do')


    defaultHttpApi= 'typetodo.com'


    projectUser= '**Anon'
    #defaults to global
    projectRoot= sublimeRoot
    projectName= ''
    projectFileName= globalFileName
    projectLegacyFn= globalLegacyFn


    settings= None

    
    #Called with blank project folder, makes global config
    def __init__(self, _projectFolder=''):
        if _projectFolder!='':
            self.projectRoot= _projectFolder
            self.projectName= os.path.split(_projectFolder)[1]
            self.projectFileName= os.path.join(self.projectRoot, self.projectName +'.do.cfg')
            self.projectLegacyFn= os.path.join(self.projectRoot, self.projectName +'.do')

        #force check globals at start
        newSettings= self.initGlobalDo()
        #migrate
        if not os.path.isfile(self.globalFileName):
            self.writeCfg(self.globalFileName, newSettings)

        self.update()





    '''
    (Re)read config from project-related config, or copy-create it from global
    '''
    def update(self):
        if 'USERNAME' in os.environ: self.projectUser= os.environ['USERNAME']

        newSettings= self.readCfg(self.projectFileName, self.projectLegacyFn) or self.initGlobalDo()

    
        if newSettings and self.settings!=newSettings:
            self.settings= newSettings

            if not os.path.isfile(self.projectFileName):
                print('TypeTodo init: Writing project\'s config.')

                self.writeCfg(self.projectFileName, newSettings)

            return True


        print('TypeTodo error: Config could not be read.')
        self.settings= None



    def getSettings(self, _name=None):
        if not self.settings:
            return

        cSettingsA= list(self.settings)

        cFile= None
        cOut= None
        for cSetting in cSettingsA:
            if isinstance(cSetting, SettingFile):
                cFile= cSetting

            if cSetting.engine==_name:
                cOut= cSetting


        #file is saved anyway
        if not cFile:
            cFile= SettingFile()
            cSettingsA.append(cFile)

            if cSetting.engine=='file':
                cOut= cFile


        fnA= list( os.path.split(cFile.file) )

        if fnA[0]=='':
            fnA[0]= self.projectRoot

        if fnA[1]=='':
            fnA[1]= self.projectName +'.txt'


        if cOut:
            return cOut

        return cSettingsA

        


########
#PRIVATE
########




    '''
    Read specified config file.
    '''
    def readCfg(self, _cfgFile, _oldCfg):
        try:
            f= codecs.open(_cfgFile, 'r', 'UTF-8')
        except:
            f= False
        if not f:
            return

        cSettings= json.loads( f.read() )


        if not cSettings: #legacy fallback
            cSettings= readLegacy(_oldCfg)


        if cSettings:
            return sorted(cSettings)



    #left only for migration purposes
    def readLegacy(self, _cfgFile):
        try:
            f= codecs.open(_cfgFile, 'r', 'UTF-8')
        except:
            f= False
        if not f:
            return


        cSettings= []

        while True:
            cfgString= f.readline()
            if cfgString=='' or cfgString=="\n" or cfgString=="\r\n":
                break
            
            #catch last matched config
            cfgFoundTry= RE_CFG.match(cfgString.rstrip('\n'))


            if not cfgFoundTry:
                continue


            curCfg= cfgFoundTry.groupdict()
            if curCfg['enginefile']:
                cSettings.append(
                    SettingFile(curCfg['fname'])
                )


            if curCfg['enginesql']:
                cSettings.append(
                    SettingMysql(
                        curCfg['addrs'],
                        curCfg['bases'],
                        curCfg['logins'],
                        curCfg['passws']
                    )
                )


            if curCfg['enginehttp']:
                cSettings.append(
                    SettingHttp(
                        curCfg['addrh'],
                        curCfg['baseh'],
                        curCfg['loginh'],
                        curCfg['passwh']
                    )
                )


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

        cSetting= SettingHttp(self.defaultHttpApi, cRep)
        return cSetting



    def initGlobalDo(self):
        cCfg= self.readCfg(self.globalFileName, self.globalLegacyFn)
        if cCfg:
            return cCfg


        #create new global config
        cSettings= []

        cSettings.append(SettingFile())
        cSettings.append(SettingMysql())
        cSettings.append( self.initNewHTTP() or SettingHttp() )


        if not self.writeCfg(self.globalFileName, cSettings):
            sublime.set_timeout(lambda: sublime.error_message('TypeTodo error:\n\n\tglobal config cannot be created'), 1000)
            return


        return cSettings



    def writeCfg(self, _fn, _settings):
        cDict= []

        for cSetting in _settings:
            cDict.append( vars(cSetting) )

        try:
            with codecs.open(_fn, 'w+', 'UTF-8') as f:
                f.write( json.dumps(cDict, indent=4) )

            return True

        except:
            None
