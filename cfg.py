# coding= utf-8

import sublime
import sys, re, os, time, codecs

if sys.version < '3':
    import urllib2, urllib
else:
    import urllib.request as urllib2
    import urllib.parse as urllib


defaultCfg= {
    'path': '',
    'file': '',
    'defaultHttpApi': 'typetodo.com',
    'blankdb': {
        'engine': '',
        'addr': '',
        'login': '',
        'passw': '',
        'base': '',
        'header': "# uncomment and configure. LAST matched line matters:\n"\
            +"# mysql 127.0.0.1 username password scheme\n"\
            +"# http 127.0.0.1 repository [username password]\n"
    }
}

#todo 241 (cfg, file) +5: enable to define separate file for TODOs, to split DB credentials from file db itself
def readCfg(_cfgPath):
    reMysqlStr= "(?P<enginesql>mysql)\s+(?P<addrs>[^\s]+)\s+(?P<logins>[^\s]+)\s+(?P<passws>[^\s]+)\s+(?P<bases>[^\s]+)"
    reHttpStr= "(?P<enginehttp>http)\s+(?P<addrh>[^\s]+)\s+(?P<baseh>[^\s]+)\s*(?P<loginh>[^\s]*)\s*(?P<passwh>[^\s]*)"
    reCfg= re.compile("^\s*(?:" +reMysqlStr +"|" +reHttpStr +")\s*$")

    try:
        f= codecs.open(_cfgPath, 'r', 'UTF-8')
    except:
        f= False
    if not f:
        return False

    foundCfg= defaultCfg['blankdb'].copy()
    headerCollect= ''

    while True:
        l= f.readline().splitlines()
        if l==[] or l[0]=='' or not l[0]:
            break

        cfgString= l[0]

        headerCollect+= cfgString +"\n"
        #catch last matched config
        cfgFoundTry= reCfg.match(cfgString)
        if cfgFoundTry:
            curCfg= cfgFoundTry.groupdict()
            if curCfg['enginesql']:
                foundCfg= {
                    'engine': curCfg['enginesql'],
                    'addr': curCfg['addrs'],
                    'login': curCfg['logins'],
                    'passw': curCfg['passws'],
                    'base': curCfg['bases'],
                }
            elif curCfg['enginehttp']:
                foundCfg= {
                    'engine': curCfg['enginehttp'],
                    'addr': curCfg['addrh'],
                    'login': curCfg['loginh'],
                    'passw': curCfg['passwh'],
                    'base': curCfg['baseh'],
                }

    foundCfg['header']= headerCollect
    foundCfg['file']= _cfgPath
    return foundCfg


def initGlobalDo(_force=False):
    if not _force:
        cfgFoundTry= readCfg(defaultCfg['file'])
        if cfgFoundTry:
            return cfgFoundTry

    cfgFoundTry= defaultCfg['blankdb'].copy()

    httpInitFlag= True

    #request new radnom public repository
    if httpInitFlag:
        req = urllib2.Request('http://' +defaultCfg['defaultHttpApi'] +'/?=newrep')
        try:
            cfgFoundTry['engine']= 'http'
            cfgFoundTry['addr']= defaultCfg['defaultHttpApi']
            cfgFoundTry['base']= bytes.decode( urllib2.urlopen(req).read() )
            cfgFoundTry['header']+= cfgFoundTry['engine'] +" " +cfgFoundTry['addr'] +" " +cfgFoundTry['base'] +"\n"
        except:
            httpInitFlag= False

    if not httpInitFlag:
        cfgFoundTry= defaultCfg['blankdb'].copy()
        sublime.set_timeout(lambda: sublime.error_message('TypeTodo error:\n\tcannot init new HTTP repository,\n\tdefault storage mode will be `file`'), 1000)
    else:
        print("New TypeTodo repository: " +cfgFoundTry['base'])
        sublime.set_timeout(lambda: sublime.status_message('New TypeTodo repository initialized'), 1000)

    try:
        with codecs.open(defaultCfg['file'], 'w+', 'UTF-8') as f:
            f.write(cfgFoundTry['header'])
    except:
        return False

    return cfgFoundTry

def plugin_loaded():
    defaultCfg['path']= os.path.join(sublime.packages_path(), 'User')
    defaultCfg['file']= os.path.join(defaultCfg['path'], '.do')
    initGlobalDo()


if sys.version < '3':
    plugin_loaded()

