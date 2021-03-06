# coding= utf-8

import re, sublime

class SAVE_STATES:
	INIT= 0
	IDLE= 1
	READY= 2
	FORCE= 3 #same as READY but without shadow compairing
	HOLD= 4

STATE_LIST= [
    [' ', 'Pending'],
    ['-', 'Open'],
    ['=', 'Progress'],
    ['+', 'Close'],
    ['!', 'Cancel'],
    False
]
STATE_DEFAULT= [' ', 'Pending']

re_prefixes= ('<!--', '//', '#', '%', '\'', '!', ';', '--')
RE_TODO_NEW= re.compile('(?P<prefix>.*?(?:' +'|'.join(re_prefixes) +'))\s*todo(?P<trigger>:)?[ \t]*(?P<comment>.*)')
RE_TODO_EXISTING= re.compile('(?P<prefix>.*?)(?:' +'|'.join(re_prefixes) +') ??(?P<state>[ \+\-\=\!]?)todo\s+(?P<id>\d+)(?:\s+\((?P<tags>.*)\))?(?:\s+(?P<priority>[\+\-]\d+))?\s*:(?P<postfix>[ \t]*(?P<comment>.*)[ \t]*)')
RE_TODO_INCONSISTENT= re.compile('(?P<prefix>.*?)(?:' +'|'.join(re_prefixes) +') ??(?P<state>[ \+\-\=\!]?)    \s+(?P<id>\d+)(?:\s+\((?P<tags>.*)\))?(?:\s+(?P<priority>[\+\-]\d+))?\s*:(?P<postfix>[ \t]*(?P<comment>.*)[ \t]*)')
RE_TODO_STORED= re.compile('^ ??(?P<prefix>[ \+\-\!\=]?)(?P<tags>.*) (?P<id>\d+): (?P<priority>[\+\-]\d+) (.+ \d\d/\d\d/\d\d \d\d:\d\d )?\"(?P<context>.*)\" (?P<editor>.+) (?P<editdate>\d\d/\d\d/\d\d) (?P<edittime>\d\d:\d\d)(?P<editsecs>:\d\d)?(?P<comment>)$')
RE_TODO_STORED_COMMENT= re.compile('^\t?(?P<comment>.*)$')
RE_TODO_FILE_MAXID= re.compile('^(?P<prefix>Reserved: )(?P<maxid>\d*)$')


re_mysql_str= "(?P<enginesql>mysql)\s+(?P<addrs>[^\s]+)\s+(?P<logins>[^\s]+)\s+(?P<passws>[^\s]+)\s+(?P<bases>[^\s]+)"
re_http_str= "(?P<enginehttp>http)\s+(?P<addrh>[^\s]+)\s+(?P<baseh>[^\s]+)\s*(?P<loginh>[^\s]*)\s*(?P<passwh>[^\s]*)"
re_file_str= "(?P<enginefile>file)\s+(?P<fname>[^\s]+)"
RE_CFG= re.compile("^\s*(?:" +re_mysql_str +"|" +re_http_str +"|" +re_file_str +")\s*$")

SKIP_SEARCH_DIR= ['tmp', 'temp']
SKIP_SEARCH_FILES= ['*.', '*.sublime-workspace', '*.gz', '*.mov', '*.avi', '*.qt']
SKIP_SEARCH_FILESIZE= 640000 #should be enough for everyone
SKIP_SEARCH_LINESIZE= 1000


constCorrectFlag= False
def constCorrect(_view):
    global constCorrectFlag
    if constCorrectFlag:
        return;
    constCorrectFlag= True


    cSettings= _view.settings()

    SKIP_SEARCH_DIR.extend(cSettings.get('folder_exclude_patterns'))

    SKIP_SEARCH_FILES.extend(cSettings.get('file_exclude_patterns'))
    SKIP_SEARCH_FILES.extend(cSettings.get('binary_file_patterns'))
