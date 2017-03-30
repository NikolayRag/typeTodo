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



class Setting:
    engine= ''

    fields= []


    def dict(self):
        out= {'engine':self.engine}
        for cField in self.fields:
            out[cField]= vars(self)[cField]

        return out


class SettingFile(Setting):
    file=      ''
    fullName= ''
    engine=    'file'

    fields= ['file']


    def __init__(self, file='', defaultRoot='', defaultName=''):
        self.file= file


        fnA= list( os.path.split(file) )

        if fnA[0]=='':
            fnA[0]= defaultRoot

        if fnA[1]=='':
            fnA[1]= defaultName +'.do'

        self.fullName= os.path.join(*fnA)



class SettingMysql(Setting):
    host=      ''
    scheme=      ''
    login=     ''
    password=     ''
    engine=    'mysql'

    fields= ['host', 'scheme', 'login', 'password']


    def __init__(self, host='', scheme='', login='', password=''):
        self.host= host
        self.scheme= scheme
        self.login= login
        self.password= password


class SettingHttp(Setting):
    host=      ''
    login=     ''
    password=     ''
    repository=      ''
    project=      ''
    fullProject=      ''
    engine=    'http'

    fields= ['host', 'repository', 'login', 'password', 'project']


    def __init__(self, host='', repository='', login='', password='', project='', defaultProject=''):
        self.host= host
        self.repository= repository
        self.project= project
        self.login= login
        self.password= password

        self.fullProject= project if project else defaultProject




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
    globalFileName= ''
    globalLegacyFn= ''

    #defaults to global
    projectRoot= ''
    projectFileName= ''
    projectLegacyFn= ''

    projectName= ''
    projectUser= '**Anon'


    defaultHttpApi= 'typetodo.com'
    settings= None

    
    #Called with blank project folder, makes global config
    def __init__(self, _projectFolder=''):
        self.projectRoot= self.sublimeRoot= os.path.join(sublime.packages_path(), 'User')
        self.projectFileName= self.globalFileName= os.path.join(self.sublimeRoot, '.do.cfg')
        self.projectLegacyFn= self.globalLegacyFn= os.path.join(self.sublimeRoot, '.do')

        if _projectFolder!='':
            self.projectRoot= _projectFolder
            self.projectName= os.path.split(_projectFolder)[1]
            self.projectFileName= os.path.join(self.projectRoot, self.projectName +'.do.cfg')
            self.projectLegacyFn= os.path.join(self.projectRoot, self.projectName +'.do')


        #force check globals at start
        newSettings= self.initGlobalDo()
        #migrate
        if newSettings and not os.path.isfile(self.globalFileName):
            self.writeCfg(self.globalFileName, newSettings)

        self.update()





    '''
    (Re)read config from project-related config, or copy-create it from global
    '''
    def update(self):
        if 'USERNAME' in os.environ: self.projectUser= os.environ['USERNAME']

        newSettings= self.readCfg(self.projectFileName, self.projectLegacyFn) or self.initGlobalDo()
    
        if newSettings:
            if self.cfg2dict(self.settings)!=self.cfg2dict(newSettings):
                self.settings= newSettings

                if not os.path.isfile(self.projectFileName):
                    print('TypeTodo init: Writing project\'s config.')

                    self.writeCfg(self.projectFileName, newSettings)

                return True

            return


        print('TypeTodo error: Config could not be read.')



    def getSettings(self, _name=None):
        if not self.settings:
            return

        cSettingsA= list(self.settings)

        cFile= None
        namedOut= None
        for cSetting in cSettingsA:
            if isinstance(cSetting, SettingFile):
                cFile= cSetting

            if cSetting.engine==_name:
                namedOut= cSetting


        #file is saved anyway
        if not cFile:
            cFile= SettingFile('', self.projectRoot, self.projectName)
            cSettingsA.append(cFile)

            if _name=='file':
                namedOut= cFile


        if namedOut:
            return namedOut

        return cSettingsA

        


########
#PRIVATE
########




    '''
    Read specified config file.
    '''
    def readCfg(self, _cfgFile, _oldCfg):
        cfgA= None
        
        try:
            f= codecs.open(_cfgFile, 'r', 'UTF-8')
            cfgA= json.loads(f.read())
        except:
            None

        if cfgA:
            cSettings= []

            for cCfg in cfgA:
                if 'disabled' in cCfg:
                    continue


                if cCfg['engine']=='file':
                    cSettings.append(
                        SettingFile(
                            (('file' in cCfg) and cCfg['file']) or '',
                            self.projectRoot,
                            self.projectName
                        )
                    )


                if cCfg['engine']=='sql' and ('host' in cCfg) and ('scheme' in cCfg):
                    cSettings.append(
                        SettingMysql(
                            cCfg['host'],
                            cCfg['scheme'],
                            (('login' in cCfg) and cCfg['login']) or '',
                            (('password' in cCfg) and cCfg['password']) or ''
                        )
                    )


                if cCfg['engine']=='http' and ('host' in cCfg) and ('repository' in cCfg):
                    cSettings.append(
                        SettingHttp(
                            cCfg['host'],
                            cCfg['repository'],
                            (('login' in cCfg) and cCfg['login']) or '',
                            (('password' in cCfg) and cCfg['password']) or '',
                            (('project' in cCfg) and cCfg['project']) or '',
                            self.projectName
                        )
                    )

            return cSettings

        self.settings= None


        #migrate
        return self.readLegacy(_oldCfg)



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
                    SettingFile(curCfg['fname'], self.projectRoot, self.projectName)
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
                        curCfg['passwh'],
                        '',
                        self.projectName
                    )
                )


        return cSettings






# -todo 2143 (http, api, config) +0: request id name from server to fill back project name
    def initNewHTTP(self):
        req = urllib2.Request('http://' +self.defaultHttpApi +'/?=new_rep_public')
        try:
            cRep= bytes.decode( urllib2.urlopen(req).read() )
        except:
            sublime.set_timeout(lambda: sublime.error_message('TypeTodo error:\n\n\tcannot init new HTTP repository,\n\tdefault storage mode will be `file`'), 1000)

            return False

        print("New TypeTodo repository: " +cRep)
        sublime.set_timeout(lambda: sublime.status_message('New TypeTodo repository initialized'), 1000)

        cSetting= SettingHttp(self.defaultHttpApi, cRep, defaultProject=self.projectName)
        return cSetting



    def initGlobalDo(self):
        cCfg= self.readCfg(self.globalFileName, self.globalLegacyFn)
        if cCfg:
            return cCfg


        #create new global config
        cSettings= [self.initNewHTTP()]
        if cSettings==[False]:
            cSettings= []

        if not self.writeCfg(self.globalFileName, cSettings):
            sublime.set_timeout(lambda: sublime.error_message('TypeTodo error:\n\n\tglobal config cannot be created'), 1000)
            return


        return cSettings




    def writeCfg(self, _fn, _settings):
        dictA= self.cfg2dict(_settings)

        #add templates
        templates= {'file':SettingFile, 'mysql':SettingMysql, 'http':SettingHttp}
        for cSetting in _settings:
            if cSetting.engine in templates:
                del templates[cSetting.engine]

        for cTemp in templates:
            cSetting= templates[cTemp]().dict()
            cSetting['disabled']= 'remove to enable'
            
            dictA.append(cSetting)


        try:
            with codecs.open(_fn, 'w+', 'UTF-8') as f:
                f.write( json.dumps(dictA, indent=4) )

            return True

        except:
            None



    def cfg2dict(self, _settings):
        cDict= []

        if _settings:
            for cSetting in _settings:
                cDict.append( cSetting.dict() )

        return cDict
