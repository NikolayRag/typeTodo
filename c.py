import re

STATE_LIST= {
    '!': 'Cancel',
    '=': 'Progress',
    '+': 'Close',
    '': 'Open'
}

RE_TODO_NEW= re.compile('(?P<prefix>.*(?://|#)\s*)todo(?P<trigger>:)?\s*(?P<comment>.*)')
RE_TODO_EXISTING= re.compile('(?P<prefix>.*)(?://|#)\s*(?P<state>[\+\=\!]?)todo\s+(?P<id>\d+)(?:\s+\((?P<tags>.*)\))?(?:\s+(?P<priority>[\+\-]\d+))?\s*:\s*(?P<comment>.*)\s*')