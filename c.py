# coding= utf-8

import re

class SAVE_STATES:
	IDLE= 0
	READY= 1
	HOLD= 2

STATE_LIST= {
    '': 'Open',
    '=': 'Progress',
    '+': 'Close',
    '!': 'Cancel'
}

RE_TODO_NEW= re.compile('(?P<prefix>.*(?://|#)\s*)todo(?P<trigger>:)?\s*(?P<comment>.*)')
RE_TODO_EXISTING= re.compile('(?P<prefix>.*)(?://|#)\s*(?P<state>[\+\=\!]?)todo\s+(?P<id>\d+)(?:\s+\((?P<tags>.*)\))?(?:\s+(?P<priority>[\+\-]\d+))?\s*:\s*(?P<comment>.*)\s*')