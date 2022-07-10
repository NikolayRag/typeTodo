 feature 1: +1 "typeTodo.py" kii 21/07/28 06:37:43
	multiline TODO

+interaction 2: +1 "typeTodo.py" kii 15/05/11 02:28:31
	midline TODO

+interaction 3: +1 "typeTodo.py" kii 15/05/11 02:28:02
	chech at start

+interaction 4: +1 "typeTodo.py" kii 15/05/11 02:28:19
	check as edited

!consistency 5: -10 "" kii 15/04/27 15:04:00
	depricated, db reloading used instead

+db 6: +0 "typeTodo.py" kii 15/01/05 02:45:00
	engine: sql

+db 7: +0 "typeTodo.py" kii 15/01/05 02:47:00
	engine: httpdb

+interaction 8: +0 "typeTodo.py" kii 15/05/13 14:54:38
	tag auto-complete

+interaction 9: -1 "typeTodo.py" kii 15/04/24 20:57:38
	using snippets

+interaction 10: +0 "typeTodo.py" kii 15/04/26 01:21:38
	in-code colorizing

!interaction, unsure 11: +0 "typeTodo.py" kii 16/09/17 01:08:47
	make more TODO formats available (convert from external db's?)

+obsolete 12: +0 "typeTodo.py" kii 15/01/09 03:24:00
	removing TODO from code - dont remove it from db

+interaction 13: +5 "typeTodo.py" kii 15/01/10 02:29:00
	make 'done' state be dedicated '', '-', '!', 'x' add probably others

+org 14: +0 "typeTodo.py" kii 14/12/25 10:00:00
	default .todo save path is [package]

+db 15: +0 "typeTodo.py" kii 14/12/25 10:00:00
	read db settings and use proper db engine

+db 16: +0 "typeTodo.py" kii 14/12/25 10:00:00
	introduce db engine

+double 17: +0 "dbSql.py" kii 14/12/25 10:00:00
	sql engine. NOT READY

+config 18: +0 "dbHttp.py" kii 14/12/25 10:00:00
	assign default unique http id at very start

+general 19: +10 "typeTodo.py" kii 14/12/25 10:00:00
	fix:no project returned for new unsaved sourcefile

+interaction, feature 21: +0 "typeTodo.py" kii 15/06/06 15:35:35
	handle filename change, basically for new unsaved files

+bug 22: +0 "dbFile.py" kii 14/12/25 10:00:00
	error was thrown if writing TODO in new unsaved file for new unsaved project

+command 23: +0 "commands.py" kii 15/04/23 23:56:37
	handle unexistent config file	

+db 24: +0 "юникод.js" kii 14/12/25 10:00:00
	проверка юникода 

+fix 25: +0 "dbFile.py" kii 14/12/25 10:00:00
	support unicode comments

+db 26: +0 "db.py" kii 14/12/25 10:00:00
	move todo array management to base TodoDb class

+db 27: +0 "db.py" kii 14/12/25 10:00:00
	handle delayed update

!obosolete 28: +0 "typeTodo.py" kii 14/12/25 10:01:00
	make cached access: read task from db as its needed

+db 29: +0 "typeTodo.py" kii 14/12/25 10:00:00
	New tasks Id assigning should NOT be delayed.

+doc 30: +0 "db.py" kii 14/12/25 10:01:00
	config is taken: 1. project.todo first string, (2. global .todo first string), (3. env variables), (4. hardcoded)

+doc 31: +0 "db.py" kii 14/12/25 10:00:00
	config string format: mysql [host] [log] [pas] [scheme] [table]

!interaction 33: -10 "typeTodo.py" kii 15/01/12 04:38:00
	remove blank TODO from base if set to +

!sql, cleanup 35: +0 "" kii 15/08/03 04:32:34
	deal with connection errors: host, log, scheme

+sql 36: +0 "dbSql.py" kii 15/01/11 19:25:00
	check bad table and insert absent fields

+sql 37: +0 "dbSql.py" kii 14/12/25 10:00:00
	optimize, optimize, opt

+config 38: +0 "db.py" kii 14/12/25 10:00:00
	reread and reconfig if changed (without db transfer); notice that cfg cache is up if any other Sublime active

+canceled 39: -1 "dbSql.py" kii 14/12/25 10:00:00
	fail if tables deleted on the fly. Should fix ever?

+sql 40: +0 "dbSql.py" kii 14/12/25 10:01:00
	save subsequent versions as delayed save will be implemented 

+xixi 41: +0 "" kii 15/06/17 03:32:41
	unicode supported

+config 42: +1 "db.py" kii 14/12/25 10:01:00
	check and create as project is opened

+errata 43: +0 "typeTodo.py" kii 14/12/25 10:01:00
	.todo file comment corrected 

 config, db, feature, unsolved 44: -1 "db.py" kii 21/07/28 06:23:58
	handle saving project - existing and blank; transfer db for involved files

+obsolete 46: +0 "cache.py" kii 15/01/21 00:14:00
	is .window() a sufficient condition?

+duplicate 47: +0 "db.py" kii 14/12/25 10:01:00
	define config sequence 

+outdated 48: +0 "db.py" kii 14/12/25 10:01:00
	 config string format: 1. '' - full, 2. 'mysql [host] [log] [pas] [scheme]', 3. 'http [host] [repId] [log] [pass]'

+config 49: +5 "db.py" kii 14/12/25 10:01:00
	add config reloading ability; Save all (will matter on delayed save) and load again

+interaction, db 50: +5 "typeTodo.py" kii 15/01/12 03:46:00
	make category into tag list

+simplify 54: +0 "typeTodo.py" kii 14/12/25 10:00:00
	getProject returns cached project or creates one

+config 55: +5 "db.py" kii 14/12/25 10:01:00
	delayed: flush (existing) before reset db[engine]

+code 56: +0 "db.py" kii 14/12/25 10:00:00
	named cfg match

+sql 57: +5 "dbSql.py" kii 14/12/25 10:00:00
	task id should be sequental within project, not db

+duplicate 59: -10 "dbSql.py" kii 15/10/15 11:56:05
	(not sure) check table over opened connection too

+fix 60: +10 "typeTodo.py" kii 14/12/25 10:00:00
	task set to '+' and wiped out flushes undo stack

+errata 61: +0 "typeTodo.py" kii 14/12/25 10:00:00
	default 'blank' category changed to 'general'

+issue 62: +0 "typeTodo.py" kii 14/12/25 10:00:00
	importance level should not be reused

+canceled 63: +0 "dbFile.py" kii 14/12/25 10:00:00
	TodoTask should not be used here

+code 65: -1 "cache.py" kii 15/05/02 03:03:22
	make singletone class for per-window cache

+http 66: +5 "dbHttp.py" kii 15/01/31 03:43:00
	implement instant id delivery; prefetch 1 in advance

+cfg 67: +0 "cfg.py" kii 15/05/04 08:11:04
	move cfg to class

+multidb 69: +0 "dbHttp.py" kii 14/12/25 10:00:00
	behave at individual save results of each dbx

+db, cleanup 71: -1 "db.py" kii 15/05/27 04:20:00
	instantly remove blank new task from cache before saving if set to + or !

!db 74: -1 "" kii 15/05/02 03:16:27
	obsolete

+fix 82: +0 "db.py" kii 15/01/21 00:28:00
	error on creating/flushing todos in the file that is placed NOT under project path

+fix 86: +0 "typeTodo.py" kii 15/01/21 00:05:00
	db init doesn't run if 2nd sublime window opened with other unconfigured project

 db, feature 89: +1 "db.py" kii 17/01/24 20:00:46
	save context (+-2 strings of code) with task

+flush 92: +0 "db.py" kii 15/01/19 05:03:00
	limit flush retries

+command 94: +1 "typeTodo.py" kii 14/12/25 10:00:00
	make command to repair broken HTTP settings (absent rep)

!store, feature 95: +0 "" kii 15/05/31 02:02:00
	duplicate

!store, feature 96: +0 "" kii 15/05/31 02:02:00
	duplicate

+general 97: +0 "typeTodo.py" kii 14/12/25 10:00:00
	add command to reset/open .do configs

+command 98: +1 "typeTodo.py" kii 14/12/25 10:00:00
	make transfer

+assure 99: +0 "db.py" kii 14/12/25 10:00:00
	yes; check if flushing needed at reset()

+config 100: +0 "db.py" kii 14/12/25 10:00:00
	Move config to .sublime-config file

+canceled 101: +0 "db.py" kii 14/12/25 10:00:00
	store 'previous' repository in config when reseting .do

+obsolete 102: +0 "cfg.py" kii 15/01/09 03:19:00
	(wut) handle 'updated' flag to make global update for HTTP

!command 103: +0 "typeTodo.py" kii 14/12/25 10:01:00
	make fallback on transfer1

+cache 104: +0 "typeTodo.py" kii 14/12/25 10:00:00
	make explicit project request for getDB()

+http 105: +0 "dbHttp.py" kii 14/12/25 10:00:00
	make fetch()

+general 106: +0 "typeTodo.py" kii 14/12/25 10:00:00
	sad

+general 107: +0 "typeTodo.py" kii 14/12/25 10:00:00
	

+multidb 108: +0 "db.py" kii 14/12/25 10:00:00
	always use file mode as well

+multidb 109: +5 "db.py" kii 14/12/25 10:00:00
	Make multiple .db connectons for one base.

+db 110: +5 "db.py" kii 14/12/25 10:00:00
	(109) supply blank .todoA

+multidb 111: +0 "db.py" kii 14/12/25 10:00:00
	(109); reset tasks .saved=true here, after flushing all.

!multidb 112: +0 "" kii 15/05/16 04:38:33
	outdated

+duplicate 113: +0 "db.py" kii 14/12/25 10:00:00
	fetch all, compare, and set unsaved for latest

+duplicate 114: +0 "db.py" kii 14/12/25 10:00:00
	respect tasks versions

+multidb 115: +0 "db.py" kii 14/12/25 10:00:00
	get biggest of all db`s

+multidb 116: +0 "db.py" kii 14/12/25 10:00:00
	flush all

+multidb 117: +0 "db.py" kii 14/12/25 10:00:00
	use all db

+obsolete 118: +0 "db.py" kii 14/12/25 10:00:00
	check why only 'file' mode

+canceled 119: +0 "db.py" kii 15/01/08 01:15:00
	check if self.todoA need to be wiped

+general 121: +0 "db.py" kii 14/12/25 10:00:00
	ok one more

+general 122: +0 "db.py" kii 14/12/25 10:00:00
	and again

+sql 123: +1 "dbSql.py" kii 14/12/25 10:00:00
	check time format

+ 124: +0 "db.py" kii 15/01/08 01:14:00
	

+general 125: +0 "dbFile.py" kii 14/12/25 10:00:00
	test

+test 126: +0 "dbFile.py" kii 14/12/25 10:00:00
	ok test

+test 127: +0 "dbFile.py" kii 14/12/25 10:00:00
	sds

+test 128: +0 "dbFile.py" kii 14/12/25 10:00:00
	dd

+general 130: +0 "db.py" kii 14/12/25 10:00:00
	te

+general 131: +0 "db.py" kii 14/12/25 10:00:00
	ok test

+general 132: +0 "dbFile.py" kii 14/12/25 10:00:00
	ttt

+general 133: +0 "dbFile.py" kii 14/12/25 10:00:00
	oko

+ 134: +0 "db.py" kii 15/01/08 01:14:00
	

+general 135: +0 "dbFile.py" kii 14/12/25 10:00:00
	qwe

+general 137: +0 "dbFile.py" kii 14/12/25 10:00:00
	

+general 142: +0 "dbFile.py" kii 14/12/25 10:00:00
	aaaaand......

!multidb, unsure 143: -1 "" kii 15/05/20 01:55:00
	canceled

!multidb, unsure 144: -1 "" kii 15/05/20 01:55:00
	сфтсудув

+cfg 145: +5 "db.py" kii 14/12/25 10:00:00
	repair onfly switching

+multidb 146: +5 "db.py" kii 14/12/25 10:00:00
	check timezone when fetching from distant source

+multidb 147: +10 "db.py" kii 14/12/25 10:00:00
	item should be unsaved for incomplete db;

+general 148: +10 "typeTodo.py" kii 15/01/23 06:05:00
	handle unresponsive servers! Especially http

+cfg, feature 149: +5 "" kii 15/05/19 18:26:00
	make use of more than one (last) cfg string

+general 150: +0 "db.py" kii 14/12/25 10:00:00
	yo

+general 151: +0 "db.py" kii 14/12/25 10:00:00
	ww

+general 152: +0 "db.py" kii 14/12/25 10:00:00
	

+ 153: +0 "db.py" kii 15/01/08 01:13:00
	

+multidb 155: +10 "db.py" kii 14/12/25 10:00:00
	manage saved[] for different db's

!test 156: +10 "db.py" kii 15/05/12 08:37:22
	test

+test 157: +0 "db.py" kii 14/12/25 10:01:00
	testx

+test 158: +0 "db.py" kii 14/12/25 10:00:00
	checkonetwo

+test 159: +0 "db.py" kii 14/12/25 10:00:00
	11

+test 160: +0 "db.py" kii 14/12/25 10:00:00
	22

+test 161: +0 "db.py" kii 14/12/25 10:01:00
	221xx

+canceled 162: +0 "db.py" kii 14/12/25 10:00:00
	do something with seconds strip in .do file; it cause to mark all file's tasks outdated. Not big deal, but need attention

+http 163: +0 "db.py" kii 15/01/08 01:13:00
	noticed -1min stamp assignment

+fix, command 164: +0 "commands.py" kii 15/01/21 00:41:00
	only 'file' mode is saved instantly, additional dbs saved at exit/edit

+general 165: +0 "db.py" kii 14/12/25 10:00:00
	www2

+ 166: +0 "db.py" kii 15/01/08 01:12:00
	

+sql 167: +5 "dbSql.py" kii 14/12/25 10:02:00
	insert with explicit stamps

+http 168: +5 "dbHttp.py" kii 14/12/25 10:01:00
	insert with explicit stamps..

+db 169: +5 "db.py" kii 14/12/25 10:00:00
	use enumerated db list instead of named, to unbind from (potentially) duplicates

+cfg, refactor 170: +0 "cfg.py" kii 15/05/19 03:51:00
	build list of cfg's to pass to db.reset()

+fix 171: +0 "db.py" kii 14/12/25 10:00:00
	synchronising with unexistent http project wipes all

+general 172: +0 "dbHttp.py" kii 14/12/25 04:52:00
	d12112assx

+canceled 173: +10 "db.py" kii 14/12/25 05:21:00
	check scenario when 2nd db's task is little newer than file's, and so differs everytime as file

+multidb 174: +10 "db.py" kii 14/12/25 05:28:00
	must be at least +1 in minutes digit to suppress warnings

+db 175: +0 "typeTodo.py" kii 14/12/27 07:37:00
	flush only at exit instead of every tab change

+general 176: +0 "typeTodo.py" kii 15/01/05 02:55:00
	

+general 177: +0 "typeTodo.py" kii 15/01/05 03:10:00
	

+general 178: +0 "typeTodo.py" kii 15/01/05 16:08:00
	sqw

+general 180: +0 "typeTodo.py" kii 15/01/05 03:27:00
	

+general 181: +0 "typeTodo.py" kii 15/01/05 16:08:00
	

+general 182: +0 "typeTodo.py" kii 15/01/05 16:10:00
	test midline

+general 183: +0 "typeTodo.py" kii 15/01/05 16:58:00
	

+general 184: +0 "typeTodo.py" kii 15/01/05 17:00:00
	ok we need practice 

+general 185: +0 "typeTodo.py" kii 15/01/05 17:03:00
	store to db and, if changed state, remove comment

+general 187: +0 "typeTodo.py" kii 15/01/05 17:09:00
	return todoId

+xxx 188: +0 "db.py" kii 15/01/08 01:12:00
	

+xxx 189: +0 "db.py" kii 15/01/08 01:12:00
	

+xxx 190: +0 "db.py" kii 15/01/08 01:12:00
	

+test 191: +0 "typeTodo.py" kii 15/01/05 18:11:00
	test midline go next1

+obsolete 192: +0 "typeTodo.py" kii 15/01/05 17:23:00
	move todo-detections regex

+general 193: +0 "typeTodo.py" kii 15/01/05 18:08:00
	create new todo in db and return string to replace original 'todo:'

+test 194: +1 "typeTodo.py" kii 15/01/05 18:03:00
	test changes2

!xxx 195: +1 "typeTodo.py" kii 15/04/28 06:30:32
	test2

+xxx 196: +0 "typeTodo.py" kii 15/01/05 18:07:00
	test more

+xxx 197: +0 "typeTodo.py" kii 15/01/05 18:07:00
	and more

+test 198: +0 "typeTodo.py" kii 15/01/05 18:12:00
	test compress

+xxx 199: +0 "typeTodo.py" kii 15/01/05 18:15:00
	test this

+xxx 200: +0 "typeTodo.py" kii 15/01/05 18:59:00
	what else?

+xxx 201: +0 "typeTodo.py" kii 15/01/05 19:00:00
	sseries

+xxx 202: +0 "typeTodo.py" kii 15/01/05 19:00:00
	of http 

+xxx 203: +0 "typeTodo.py" kii 15/01/05 19:00:00
	hang 

+xxx 204: +0 "typeTodo.py" kii 15/01/05 19:00:00
	performance

+general 205: +0 "typeTodo.py" kii 15/01/05 19:01:00
	one two

+general 206: +0 "dbFile.py" kii 15/01/05 19:03:00
	testx

+http 207: +0 "dbHttp.py" kii 15/01/06 02:21:00
	flushing should use json; due to key ammount limitation

+fix 208: +10 "db.py" kii 15/01/07 01:34:00
	'unsaved' tasks could be just 'ok', no need to save them

+db, cleanup 209: -10 "task.py" kii 15/05/26 16:46:00
	make .savedA[] for file treated as for other engines

!db, feature, unsure 210: -5 "" kii 15/06/02 15:43:05
	implement editing of project .do file

+xxx 211: +0 "db.py" kii 15/01/08 02:58:00
	oka

+command 212: +0 "commands.py" kii 15/01/09 22:30:00
	add command to change states; just print in related symbol

+command 213: +0 "commands.py" kii 15/01/09 22:32:00
	filter current state out of command menu

+xxx 214: +0 "db.py" kii 15/01/09 23:01:00
	test command shortcut

+xxx 215: -10 "task.py" kii 15/01/09 23:13:00
	make .savedA[] for file treated as for other engines

+xxx 219: -10 "task.py" kii 15/01/09 23:13:00
	make .savedA[] for file treated as for other engines

+interaction 220: +0 "typeTodo.py" kii 15/01/10 14:20:00
	wipe 'Cancel' todos

!xxx 221: +0 "typeTodo.py" kii 15/01/10 14:20:00
	test cancel

+sql 222: +0 "dbSql.py" kii 15/01/11 18:28:00
	change table definition format

!sql 223: +0 "dbSql.py" kii 15/01/11 18:33:00
	make table correction by inserting absent fields

+sql, multitag 224: +0 "dbSql.py" kii 15/01/11 20:55:00
	fix multitag save order

+interaction 225: +0 "typeTodo.py" kii 15/01/18 21:20:00
	ask the reason for 'Cancel'

+task, db 226: +0 "task.py" kii 15/06/02 15:45:44
	skip task saving if no real difference

+task, db 227: +0 "task.py" kii 15/06/02 15:45:37
	dont store blank comment

+fix 228: +1 "commands.py" kii 15/01/17 16:12:00
	setState for st3

!ux 229: +0 "" kii 15/05/13 12:01:28
	outdated

!command 230: +0 "commands.py" kii 15/04/23 23:57:22
	duplicate

!general 231: +0 "typeTodo.py" kii 15/04/24 23:16:25
	duplicate, done

=feature 232: +1 "typeTodo.py" kii 17/04/02 04:41:29
	introduce sub-todo's that are part of other, //todo /yyy: becomes xxx/yyy

+fix 233: +0 "typeTodo.py" kii 15/01/20 21:10:00
	un/re-doing text entering doesnt trigger typetodo saving

+db, delayed 234: +0 "typeTodo.py" kii 15/01/20 02:19:00
	save stuff on view deactivated; increase saving delay

+general, fix 235: +0 "typeTodo.py" kii 15/01/19 15:53:00
	remove event multi-defining

!db, config 236: +0 "" kii 15/05/12 08:38:28
	already done

!xxx 237: +0 "D:\pdx\ssss" kii 15/01/21 00:27:00
	xxx

+db 238: +0 "db.py" kii 15/01/22 18:30:00
	flush by calling single delayed function

+db, init 239: +0 "typeTodo.py" kii 15/01/22 18:29:00
	depricate on_activated

+db, flush, cleanup 240: +0 "db.py" kii 15/05/26 18:16:00
	hadn't to save, needed for file mode;  should be reviewed

+cfg, file, feature 241: +5 "cfg.py" kii 15/05/19 03:52:00
	enable to define separate file for TODOs, to split DB settings from file db itself

!http, api 242: +5 "dbHttp.py" kii 15/04/23 18:08:16
	point at project using URL

!general 253: +0 "dbHttp.py" kii 15/01/29 03:18:00
	server issue, canceled

! 254: +0 "" kii 15/04/24 16:19:55
	WWW test

!test 255: +0 "dbHttp.py" kii 15/01/27 18:09:00
	

!general, xxx 256: +10 "dbHttp.py" kii 15/01/27 23:07:00
	multi

+http, cleanup 257: +0 "dbHttp.py" kii 15/05/20 03:21:00
	remove True and False states after migration

+db, cleanup 258: +5 "db.py" kii 15/07/15 04:35:28
	release prefetched id at exit

!xxx 261: +0 "dbHttp.py" kii 15/01/31 03:43:00
	test

!xxx 262: +0 "dbHttp.py" kii 15/01/31 03:43:00
	test

!xxx 263: +0 "dbHttp.py" kii 15/01/31 03:43:00
	xxx

!xxx 264: +0 "dbHttp.py" kii 15/04/24 16:21:03
	

+http, cleanup 270: +0 "dbHttp.py" kii 15/08/03 03:45:00
	implement http timeout

+http, fix 273: +0 "dbHttp.py" kii 15/02/03 06:00:00
	fix todos that are set saved while waiting for next flush

+xxx 274: +0 "dbHttp.py" kii 15/02/02 02:34:00
	test

!xxx 275: +0 "dbHttp.py" kii 15/02/02 04:13:00
	test

+minor 278: +0 "task.py" kii 15/02/03 04:03:00
	introduce save states: idle/ready/hold 

!check 279: +0 "" kii 15/07/28 03:56:00
	should be not an issue

+db, flush, cleanup 280: +0 "db.py" kii 15/05/26 18:16:00
	.dirty used only to display message; should be removed at all

!db, flush, cleanup 281: +0 "" kii 15/08/18 19:39:44
	compare with postList

+test 284: +0 "dbHttp.py" kii 15/02/03 05:28:00
	test for concurrent saves

+sql, cleanup 285: +0 "dbSql.py" kii 15/08/02 04:25:00
	detect sql errors

+test 286: +0 "dbHttp.py" kii 15/02/03 06:00:00
	test ok

!db 292: +5 "db.py" kii 15/05/02 05:29:53
	not only pick biggest id, but also reserve picked within all DBs

+command, ux 301: +0 "commands.py" kii 15/02/23 02:39:00
	set default states for setState according of current state (open > inprogress > closed)

+db 305: +10 "db.py" kii 15/05/12 07:52:50
	make .newId take in respect all db's at once

!http, cleanup, unsure 307: +0 "" kii 15/08/18 19:31:00
	related to http api, unchanged atm

+http, encoding, fix 310: +0 "dbHttp.py" kii 15/03/03 05:55:00
	sometimes give 'idna' encoding error

!xxx 319: +0 "commands.py" kii 15/04/15 04:22:00
	tezt

!xxx 321: +11 "commands.py" kii 15/04/15 05:25:00
	one more

!xxx 323: +0 "commands.py" kii 15/04/16 04:36:41
	local db

!xxx 325: +0 "commands.py" kii 15/05/11 04:38:56
	test nginx

!xxx 327: +0 "commands.py" kii 15/05/11 04:38:49
	test

+cfg 333: +0 "db.py" kii 15/05/11 02:20:25
	make .do read-save cycle more crisp and time-compact

+cfg 334: +1 "cfg.py" kii 15/05/11 23:06:28
	catch cfg read errors

+command 341: +0 "commands_find.py" kii 15/04/28 05:50:54
	jump: deal with multiple matches

+command 348: +0 "commands.py" kii 15/04/25 15:52:02
	Find Todo: fix focusing on file open

+cfg, feature 351: +0 "cfg.py" kii 15/05/18 17:09:40
	allow skip global configure for HTTP at first start

!general 359: +0 "typeTodo.py" kii 15/04/24 20:11:18
	

!general 363: +0 "typeTodo.py" kii 15/04/24 20:09:04
	

!xxx 364: +0 "typeTodo.py" kii 15/04/24 20:10:34
	

!xxx 365: +0 "typeTodo.py" kii 15/04/24 20:11:39
	test44

!general 366: +0 "typeTodo.py" kii 15/04/24 20:13:47
	tototot

!general 367: +0 "typeTodo.py" kii 15/04/24 20:20:25
	(self, _txt=False):

!general 368: +0 "typeTodo.py" kii 15/04/24 20:22:01
	store to db and, if changed state, remove comment

!xxx 369: +0 "typeTodo.py" kii 15/04/24 20:22:49
	tetete

!xxx 370: +0 "typeTodo.py" kii 15/04/24 20:23:55
	

!xxx 371: +0 "typeTodo.py" kii 15/04/24 20:24:40
	

+interaction 372: +0 "typeTodo.py" kii 15/04/24 23:02:51
	restrict doplet editing if sel() range is other than Tags, Priority and Comment blocks

!xxx 373: +0 "typeTodo.py" kii 15/04/24 23:04:32
	opser

!xxx 374: +0 "typeTodo.py" kii 15/04/24 23:06:40
	tst

!xxx 375: +0 "typeTodo.py" kii 15/04/25 01:22:12
	ok

!xxx 376: +0 "typeTodo.py" kii 15/04/25 01:22:24
	ok

+interaction 377: +0 "typeTodo.py" kii 15/04/25 06:57:34
	Add +/- shortcut to change priority

!xxx 378: +0 "typeTodo.py" kii 15/04/25 05:31:49
	test

!xxx 411: +3 "typeTodo.py" kii 15/04/25 05:38:16
	okay

!xxx 414: +0 "typeTodo.py" kii 15/04/25 05:50:15
	

!xxx 415: +0 "typeTodo.py" kii 15/04/25 05:55:58
	oka

!xxx 417: +0 "typeTodo.py" kii 15/04/25 06:01:14
	ok

!xxx 438: +0 "typeTodo.py" kii 15/04/25 06:56:54
	oka? yes

!xxx 444: +0 "typeTodo.py" kii 15/04/25 07:19:01
	wut

!db 446: +0 "typeTodo.py" kii 15/04/25 08:55:50
	

!xxx 447: +0 "typeTodo.py" kii 15/04/25 07:33:18
	yehoo

+fix 449: -1 "typeTodo.py" kii 15/05/13 00:48:00
	too much code duplicated from matchTodo(), review

!xxx 452: +0 "typeTodo.py" kii 15/04/25 14:10:13
	

!xxx 454: +0 "commands_maintain.py" kii 15/04/26 03:10:55
	test

!xxx 455: +0 "commands_maintain.py" kii 15/04/26 03:10:33
	test2d

!xxx 456: +0 "commands_maintain.py" kii 15/04/26 03:10:45
	tes t3  sd

!xxx 479: +0 "typeTodo.py" kii 15/04/25 22:32:19
	testasd aa

!xxx 480: +0 "typeTodo.py" kii 15/04/25 22:33:19
	

!xxx 481: +0 "typeTodo.py" kii 15/04/25 22:33:49
	

!xxx 482: +0 "typeTodo.py" kii 15/04/25 22:36:34
	

!xxx 483: +0 "typeTodo.py" kii 15/04/25 22:40:41
	s

!xxx 484: +0 "typeTodo.py" kii 15/04/25 22:41:08
	d

!xxx 485: +0 "typeTodo.py" kii 15/04/25 22:41:38
	e

!xxx 487: +0 "commands_maintain.py" kii 15/04/25 22:41:59
	d

!xxx 488: +0 "commands_maintain.py" kii 15/04/25 22:49:05
	

!xxx 489: +0 "typeTodo.py" kii 15/04/25 23:07:45
	

!xxx 490: +0 "typeTodo.py" kii 15/04/25 23:08:44
	x

!xxx 491: +0 "commands_maintain.py" kii 15/04/26 01:21:09
	

!command, cleanup 492: -5 "" kii 15/06/02 15:46:20
	should use specified region to speedup at editing

!xxx 493: +0 "commands_maintain.py" kii 15/04/26 01:21:07
	test

!xxx 495: +0 "typeTodo.py" kii 15/04/26 01:59:47
	test

!xxx 496: +0 "typeTodo.py" kii 15/04/26 02:01:00
	

+fix 497: +10 "typeTodo.py" kii 15/04/27 02:05:21
	canceling with substitution fails

!xxx 521: +0 "commands_maintain.py" kii 15/04/28 06:30:15
	texttetxt

!xxx 523: +0 "typeTodo.py" kii 15/04/27 00:50:09
	twest

!xxx 530: +0 "typeTodo.py" kii 15/04/26 23:46:41
	ok

!xxx 532: +0 "typeTodo.py" kii 15/04/28 06:29:58
	ok

!xxx 534: +0 "typeTodo.py" kii 15/04/26 23:47:39
	ok

!xxx 536: +0 "typeTodo.py" kii 15/04/28 06:30:09
	xxx

!xxx 548: +0 "" kii 15/04/27 02:05:02
	test24sas

!xxx 554: +0 "typeTodo.py" kii 15/04/27 01:47:06
	

!xxx 560: +0 "" kii 15/04/27 02:15:38
	tets

+keyboard 561: +0 "typeTodo.py" kii 15/04/27 02:55:05
	restrict shortcuts to doplet

+command 562: +0 "commands_find.py" kii 15/04/28 02:49:27
	find todo by tag (using mask)

+interaction 563: -1 "typeTodo.py" kii 15/05/13 02:16:26
	allow to change doplet state by pressing corresponding key (-/+/=/!) everywhere in protected doplet; same for up/down for priority

+command 564: +0 "commands_find.py" kii 15/04/28 20:22:26
	todo search results window should be normally formatted

!command 565: +0 "" kii 15/04/28 04:16:36
	fix todo search while in results window

+command, feature 566: +0 "commands_find.py" kii 15/05/18 01:46:19
	make jump-to-result in todo search results window

!opa 567: +0 "" kii 15/04/28 04:27:43
	ye

!opa 568: +0 "" kii 15/04/28 04:28:26
	oy

!xxx 569: +0 "" kii 15/04/28 05:51:23
	test

+command, feature 570: +0 "commands_maintain.py" kii 15/05/31 01:55:00
	make tool for viewing inconsistent differences

+colorize 571: +0 "commands_maintain.py" kii 15/04/28 06:09:00
	change in-progress color, coz it slow down

+command 572: +0 "commands_find.py" kii 15/04/28 19:20:47
	Find should handle both views then files

!colorize 573: +0 "" kii 15/04/28 06:13:34
	

+command, feature 577: +0 "commands_find.py" kii 15/05/18 03:10:20
	entering blank string for search gives list of view's doplets

+command 578: +0 "commands_find.py" kii 15/04/29 02:40:43
	prohibit editing doplets within search results; fix inconsistence

+check, fix 690: +0 "typeTodo.py" kii 15/06/03 05:33:50
	since updVals passed delayed, there can be inconsistence

+db 701: +0 "cache.py" kii 15/05/02 05:30:58
	change cache key to window.id()

!xxx 783: +0 "" kii 15/05/02 03:29:48
	test

+consistency 820: +0 "typeTodo.py" kii 15/05/02 16:21:32
	db maintainance callback should be moved somewhere out

!cfg, cache 827: +0 "" kii 15/05/12 08:37:34
	store cfg in cache

+cfg, fix 844: +0 "commands.py" kii 15/05/05 05:06:00
	fix after config-to-class

+fix 845: +0 "commands_maintain.py" kii 15/05/16 04:16:25
	compare tags more properly

+fix 846: +0 "commands.py" kii 15/05/04 07:25:42
	fix after config-to-class

+cfg, fix 852: +0 "cfg.py" kii 15/05/03 18:27:45
	update config

+cfg 860: +0 "cfg.py" kii 15/05/11 02:19:53
	handle error

+cfg 861: +0 "cfg.py" kii 15/05/11 02:19:17
	save cfg to project

!xxx 946: +0 "" kii 15/05/04 07:31:21
	sss

!db, sql, refactor 956: +0 "" kii 15/05/31 02:05:00
	unused

!db, http, refactor 957: +0 "" kii 15/05/31 02:05:00
	unused

!xxx 959: +0 "" kii 15/05/11 04:38:27
	???

!xxx 990: +0 "" kii 15/05/11 04:38:20
	wat

! 991: +0 "" kii 15/05/12 08:37:10
	

!xxx 999: +0 "commands.py" kii 15/05/11 04:38:24
	dfghj

!xxx 1004: +0 "" kii 15/05/05 06:26:43
	dkjhsdfjsd

!xxx 1005: +0 "" kii 15/05/05 06:26:44
	dfsdfsdf

!yeye 1013: +0 "" kii 15/05/05 06:51:50
	yeye

!xxx 1019: +0 "" kii 15/05/06 05:04:23
	test

!xxx 1020: +0 "" kii 15/05/06 05:04:26
	hgsfdsg

!xxx 1021: +0 "" kii 15/05/06 05:04:27
	sdkhfdsv

!hehe 1058: +0 "" kii 15/05/06 06:06:48
	111

!hehe 1059: +0 "" kii 15/05/06 06:06:47
	dd

!opa 1060: +0 "" kii 15/05/06 06:06:46
	

!check 1067: +0 "" kii 15/05/11 03:28:35
	not an issue

+db, file 1079: +0 "dbFile.py" kii 15/05/11 04:40:56
	sort doplets by id at flush

+db, file 1087: +0 "dbFile.py" kii 15/05/12 07:52:58
	make newId() accept desired id

+db, sql 1088: +0 "dbSql.py" kii 15/05/12 07:52:59
	make newId() accept desired id

+db, http 1089: +0 "dbHttp.py" kii 15/05/12 07:53:01
	make newId() accept desired id

+db 1094: +0 "db.py" kii 15/05/12 07:52:54
	make all-at-once newId() prefetch into db class

!xxx 1096: +0 "" kii 15/05/12 05:24:41
	test

!xxx 1097: +0 "" kii 15/05/12 05:24:43
	test2

!xxx 1099: +0 "" kii 15/05/12 05:26:47
	test

!xxx 1100: +0 "" kii 15/05/12 05:26:45
	

!xxx 1102: +0 "" kii 15/05/12 05:31:54
	ok

!xxx 1105: +0 "" kii 15/05/12 05:32:50
	ok

!xxx 1106: +0 "" kii 15/05/12 05:32:52
	okkk

!xxx 1107: +0 "" kii 15/05/12 05:33:27
	ok

!xxx 1157: +0 "" kii 15/05/12 05:33:00
	ok

!xxx 1167: +0 "" kii 15/05/12 05:33:00
	ok

!xxx 1175: +0 "" kii 15/05/12 05:33:00
	ok

!xxx 1180: +0 "" kii 15/05/12 05:33:00
	ok

!xxx 1185: +0 "" kii 15/05/12 05:33:00
	ok

!xxx 1190: +0 "" kii 15/05/12 05:33:00
	ok

!xxx 1195: +0 "" kii 15/05/12 05:33:00
	ok

!xxx 1197: +0 "" kii 15/05/12 07:47:00
	test

!xxx 1198: +0 "" kii 15/05/12 07:47:01
	ok

!xxx 1199: +0 "" kii 15/05/12 07:54:10
	test

!xxx 1204: +0 "" kii 15/05/12 09:17:04
	ok

!xxx 1207: +0 "" kii 15/05/13 00:56:17
	test

!xxx 1209: +0 "" kii 15/05/13 02:41:38
	ok

!xxx 1211: +0 "" kii 15/05/13 02:43:45
	ok

+command, fix 1216: +5 "commands_find.py" kii 15/05/13 17:55:20
	search with .* or * duplicates some results

!xxx 1219: +0 "" kii 15/05/13 12:03:06
	s

!xxx 1220: +0 "" kii 15/05/13 12:09:07
	11

!refactor 1225: -10 "typeTodo.py" kii 15/06/02 15:46:41
	should find better place

!xxx 1227: +0 "" kii 15/05/13 14:43:47
	ee

!general 1228: +0 "typeTodo.py" kii 15/05/13 14:44:06
	

!xxx 1230: +0 "" kii 15/05/13 14:52:56
	oo

!weirdtag 1231: +0 "" kii 15/05/13 14:53:56
	ok

!xxx 1232: +0 "" kii 15/05/13 14:53:54
	

!xxx 1234: +0 "" kii 15/05/13 14:54:25
	

!xxx 1237: +0 "" kii 15/05/13 16:21:01
	xxx 

!xxx 1238: +0 "" kii 15/05/13 16:27:44
	ytq

 interaction, unsolved, issue 1239: +0 "typeTodo.py" kii 17/04/02 04:38:49
	get rid of snippets for tags autocomplete

!xxx 1248: +0 "" kii 15/05/15 05:48:18
	check

+db, consistency, feature 1250: +0 "db.py" kii 15/05/30 04:38:00
	fetch db periodically

+command, fix 1252: +0 "commands_find.py" kii 15/05/17 19:18:28
	skip search in ordinary 'Find' results

+command, fix 1253: +0 "commands.py" kii 15/05/17 19:06:11
	prevent 'Set State' command in 'Search todo' results

!unsure 1254: +0 "" kii 15/05/20 01:56:00
	duplicate

!test for multiword tag 1255: +0 "" kii 15/05/16 05:35:46
	ok

!test for multiword tag, xxx 1256: +0 "" kii 15/05/16 05:36:01
	kkk

!xxx, test for multiword tag 1257: +0 "" kii 15/05/16 05:36:04
	ok

+command, feature 1258: +0 "commands_find.py" kii 15/05/17 19:01:41
	'Search todo' jump from own window to doplet in code

!code, command, fix 1264: +0 "" kii 15/05/17 18:57:22
	unneccessary

+command, fix 1267: +0 "commands_maintain.py" kii 15/05/17 23:09:11
	cursor currupts when different colorized doplet on one view

!xxx 1268: +0 "commands_maintain.py" kii 15/05/17 23:09:00
	wat

!xxx 1293: +0 "commands_maintain.py" kii 15/05/17 23:09:49
	

!xxx 1295: +0 "commands_maintain.py" kii 15/05/17 23:13:20
	ok

!xxx 1297: +0 "commands_maintain.py" kii 15/05/17 23:13:21
	

!xxx 1299: +0 "commands_maintain.py" kii 15/05/17 23:15:02
	

!xxx 1301: +0 "commands_maintain.py" kii 15/05/17 23:16:40
	ok

!xxx 1302: +0 "commands_maintain.py" kii 15/05/17 23:16:41
	ok

!xxx 1304: +0 "commands_maintain.py" kii 15/05/17 23:16:46
	

!xxx 1305: +0 "commands_maintain.py" kii 15/05/17 23:17:03
	test

!xxx 1306: +0 "" kii 15/05/17 23:26:07
	ok

!xxx 1307: +0 "" kii 15/05/17 23:26:09
	kk

+command, feature 1309: +0 "commands_find.py" kii 15/05/30 07:00:00
	allow 'exclude' search by prefixing with '-'

+command, feature 1310: +0 "commands_find.py" kii 15/05/24 22:46:00
	'Search todo' should skip files listed in sublime config

!test 1321: +0 "" kii 15/05/19 02:11:12
	xxx

!xxx 1323: +0 "" kii 15/05/19 02:12:00
	oka&

!xxx 1339: +0 "" kii 15/05/19 02:43:00
	okaokaoka

!xxx 1344: +0 "" kii 15/05/19 02:57:00
	ok&&&&!

!db, cfg 1347: +0 "dbBlank.py" kii 15/05/19 03:04:00
	add dbBlank to save overrided default.do

+cfg 1348: +0 "cfg.py" kii 15/05/19 03:54:00
	prevent 'file' to be explicitely specified to .do itself

+cfg 1359: +0 "cfg.py" kii 15/05/19 03:53:00
	save unexistent .do config

+cfg, fix, st3 1365: +0 "cfg.py" kii 15/05/19 14:40:00
	st3 repeats new http creation several times

+fix, cfg, st3 1368: +0 "commands.py" kii 15/05/19 18:13:00
	'Reset' command executed twice if first with no .do

+task, cleanup 1374: +0 "task.py" kii 15/05/20 03:12:00
	remove creator and creation stamp, it should remain only in true databases as sql, http

!xxx 1402: +0 "" kii 15/05/20 03:26:00
	

!fix 1407: +0 "" kii 15/05/20 03:43:00
	unconfirmed

+command, fix 1431: +0 "commands_find.py" kii 15/05/20 04:12:00
	search doplets by tags should ignore case

!xxx 1434: +0 "" kii 15/05/20 04:03:00
	

!xxx 1435: +0 "" kii 15/05/20 04:03:00
	ok?

+command 1460: +0 "typeTodo.py" kii 15/05/21 05:14:00
	futher protect 'Search todo' results window from changes

+command, fix 1468: +0 "commands_find.py" kii 15/05/24 23:30:00
	'Search todo' dont jump to external 'file'

!xxx 1482: +0 "" kii 15/05/26 12:51:00
	

+flush, feature, fix 1485: +0 "" kii 15/06/02 15:40:43
	check actual changes in task to trigger it unsaved

!xxx 1487: +0 "" kii 15/05/26 17:40:00
	

!xxx 1490: +0 "" kii 15/05/26 20:22:00
	

!xxx 1492: +0 "" kii 15/05/27 03:52:00
	

!xxx 1497: +0 "" kii 15/05/26 20:34:00
	

+flush, feature 1498: +0 "dbFile.py" kii 15/05/27 01:43:00
	save 'file' only if any of doplets are actually changed

!check, db 1499: -5 "" kii 15/07/15 18:17:40
	obsolete

!db, cleanup 1500: +0 "" kii 15/05/27 04:14:00
	

+db, cleanup 1501: +0 "db.py" kii 15/05/27 04:15:00
	

!xxx 1505: +0 "" kii 15/05/27 04:17:00
	

!xxx 1509: +0 "" kii 15/05/27 04:20:00
	

!xxx 1510: +0 "" kii 15/05/27 04:22:00
	test

+command, fix 1511: +0 "commands_find.py" kii 15/05/27 04:32:00
	when 'Search todo' with blank input (for view), dont jump on cancel

+command, fix 1512: +0 "commands_find.py" kii 15/05/27 04:37:00
	'Search todo' with blank input was stripping long comments wrong

+command, feature 1538: +0 "commands_find.py" kii 15/05/30 05:32:00
	jump from search results by doubleclick

+fix 1546: +0 "typeTodo.py" kii 15/05/30 15:29:00
	autocompletion is wasted after doplet

!xxx 1553: +0 "commands_maintain.py" kii 15/05/31 01:47:00
	test

!command, fix 1554: +0 "" kii 16/09/15 23:58:36
	reconsidered

+fix 1560: +0 "commands.py" kii 15/06/02 14:08:00
	'browse' command dont work

+command, change 1561: +0 "commands_find.py" kii 15/06/02 14:20:43
	'find' with tag should show results view for one match

!xxx 1563: +0 "" kii 15/06/02 15:38:50
	test

!xxx 1564: +0 "commands_maintain.py" kii 15/06/02 15:41:57
	test

!xxx 1565: +0 "commands_find.py" kii 15/06/02 15:47:29
	ok

+fix 1568: +0 "commands_find.py" kii 15/06/02 16:24:53
	'search' with blank field (in-view) fails

!xxx 1569: +0 "" kii 15/06/02 20:34:58
	112124

!xxx 1571: +0 "" kii 15/06/02 20:37:27
	+

!xxx 1574: +0 "" kii 15/06/02 20:37:19
	ok

!xxx 1575: +0 "" kii 15/06/02 20:42:32
	ok

!xxx 1576: +0 "" kii 15/06/02 20:43:54
	

!xxx 1578: +0 "" kii 15/06/02 20:52:04
	wwwwwww

!xxx 1579: +0 "typeTodo.py" kii 15/06/02 20:55:04
	test

!xxx 1580: +0 "typeTodo.py" kii 15/06/02 20:58:26
	testtt

!xxx 1582: +0 "" kii 15/06/03 01:48:10
	more test

+fix 1634: +0 "db.py" kii 15/06/03 17:25:31
	hanging detected since v1.7.1

!xxx 1640: +0 "" kii 15/06/03 06:28:59
	test

!xxx 1641: +0 "db.py" kii 15/06/03 06:28:55
	x

!xxx 1643: +0 "" kii 15/06/03 06:30:35
	okokok

!xxx 1644: +0 "" kii 15/06/03 06:30:31
	okokok

!xxx 1645: +0 "" kii 15/06/03 06:30:27
	

!check, db 1662: +0 "" kii 15/08/07 02:19:10
	uncertain

!xxx 1674: +0 "" kii 15/06/05 04:36:43
	test111222

!xxx 1687: +0 "" kii 15/06/06 04:27:16
	blank

!xxx 1689: +0 "" kii 15/06/06 04:27:13
	

!xxx 1690: +0 "bbbb" kii 15/06/06 15:33:24
	test uu

!xxx 1692: +0 "aaa" kii 15/06/06 15:33:44
	test 1

!xxx, test 1696: +0 "aaaa" kii 15/06/06 16:55:04
	ok?

+fix, sql 1707: +1 "" kii 15/07/08 04:54:00
	sql interfere if newId and fetch/flush run at once. Probably transaction issue

+command 1728: +0 "c.py" kii 15/06/16 20:48:56
	'search' skips TEMP folder

+db, fix 1731: +10 "cache.py" kii 15/06/17 02:39:12
	switching project in window mixes database

!xxx 1734: +0 "cache.py" kii 15/06/17 02:43:29
	test ttd

!xxx 1736: +0 "" kii 15/06/17 02:45:11
	test

+db, fix 1739: +0 "" kii 15/07/08 04:53:20
	switching project in window results in mixed database

!command 1740: +1 "" kii 15/07/08 04:54:09
	st3 search from 'search results' not working

+db, fix 1753: +0 "dbFile.py" kii 15/06/23 20:36:20
	return proper file maxid prior to first fetch

+fix, file 1759: +1 "dbFile.py" kii 15/06/26 00:50:45
	fetching at file newId() results in crash in ST2

+config, fix 1774: +0 "cfg.py" kii 15/07/01 03:00:27
	pin project folder at Config() creation

!xxx 1781: +0 "typeTodo.py" kii 15/07/03 06:24:05
	

 cleanup, uncertain, issue 1783: -1 "typeTodo.py" kii 17/04/02 04:38:55
	switching project in window not clearly fixed, need review

!xxx 1786: +0 "commands_maintain.py" kii 15/07/03 06:33:58
	

!xxx 1789: +0 "commands_maintain.py" kii 15/07/03 06:37:29
	

!xxx 1790: +0 "commands_maintain.py" kii 15/07/03 06:39:02
	okaaaaa

+db, flush 1795: +0 "db.py" kii 15/07/08 04:29:24
	make flush retries endless with error messaging less annoying

+db, cleanup 1797: +0 "db.py" kii 15/08/04 04:55:44
	React on newId() errors correctly

+interaction 1798: +0 "typeTodo.py" kii 15/07/06 04:14:47
	make autocompletion list in form of "tag: ..."

!xxx 1803: +0 "typeTodo.py" kii 15/07/06 04:14:29
	

!xxx 1804: +0 "typeTodo.py" kii 15/07/06 04:14:36
	

!xxx 1805: +0 "typeTodo.py" kii 15/07/06 04:14:38
	

!check, db 1814: +0 "" kii 15/07/08 04:36:35
	outdated

!xxx 1815: +0 "typeTodo.py" kii 15/07/06 04:37:04
	

 db 1818: +0 "db.py" kii 17/04/02 04:40:05
	make compairing inconsistencies by versions where they available (not file atm)

+db, flush, fix 1833: +5 "db.py" kii 15/07/08 04:19:52
	flushing with error resets tasks 'saved' flag

!db, flush, fix 1834: +0 "" kii 15/07/08 04:19:44
	duplicate

!command, find, fix, uncertain 1859: -1 "" kii 16/09/13 14:32:43
	not confirmed

!xxx 1861: +0 "typeTodo.py" kii 15/07/12 05:31:52
	)

!xxx 1862: +0 "typeTodo.py" kii 15/07/13 03:19:16
	

!db, feature 1869: +0 "" kii 15/07/15 03:53:42
	duplicate

!db, fix 1870: +0 "" kii 15/07/15 18:04:29
	not issue

+db, cleanup 1875: +0 "db.py" kii 15/07/19 05:46:25
	no synchronisation for new added DB

!db, feature 1876: +0 "" kii 15/08/04 04:29:09
	dont fit into design

!db, check 1877: +0 "" kii 15/07/17 05:25:56
	not issue

+file, db, fix 1878: +5 "typeTodo.py" kii 15/07/17 05:20:27
	remove on_save resaving at all: unprofitable

!xxx, test 1884: +0 "typeTodo.py" kii 15/07/17 05:19:29
	ok123ok

!xxx 1890: +0 "db.py" kii 15/07/17 05:37:12
	test1

!xxx 1892: +0 "db.py" kii 15/07/17 05:39:00
	test1

!xxx 1893: +0 "db.py" kii 15/07/17 05:39:00
	test2

!xxx 1895: +0 "db.py" kii 15/07/17 05:41:23
	texs

!xxx 1896: +0 "db.py" kii 15/07/17 05:41:58
	okokok

!xxx 1897: +0 "db.py" kii 15/07/17 05:41:57
	ye

+fix 1898: +1 "db.py" kii 15/07/30 01:01:45
	new todo just right after Sublime start is not delayed to save

+command, fix, find 1899: +1 "commands_find.py" kii 15/07/30 03:40:09
	trying to jump from search result for duplicated doplets starts new search

+db, cleanup 1900: +0 "db.py" kii 15/07/19 05:04:23
	flushing could stop at db with problem

+db, fix 1902: +0 "db.py" kii 15/07/24 04:28:53
	still wrong definition of current/saved task, should compare other 

+db, fix 1905: +0 "db.py" kii 15/07/28 03:55:00
	unexistent task is not checked against existing second time fetch() is called

+xxx 1906: +0 "db.py" kii 15/07/24 04:51:31
	tezt

!xxx 1907: +0 "" kii 15/07/24 05:14:46
	opsa

!xxx 1908: +0 "" kii 15/07/26 04:50:13
	xx1

+db, feature 1909: +0 "" kii 15/07/30 16:42:09
	release id for immediately canceled task

+feature 1910: +0 "typeTodo.py" kii 16/09/12 05:54:36
	right mouseclick context actions

+check, db 1911: +0 "db.py" kii 15/07/28 03:55:00
	what if other states are not IDLE

!xxx 1912: +0 "db.py" kii 15/07/28 03:40:11
	ok1

+db, fix 1915: +1 "db.py" kii 15/07/29 01:42:39
	respect current db max ID when completely switching database

+cfg, fix 1916: +1 "" kii 15/07/29 03:29:51
	newly defined 'file' is not created

!xxx 1918: +0 "db.py" kii 15/07/28 05:24:56
	tetete

!xxx 1919: +0 "" kii 15/07/28 05:48:35
	aaa

!xxx 1920: +0 "db.py" kii 15/07/28 05:50:27
	xxx

!xxx 1921: +0 "db.py" kii 15/07/28 17:18:00
	ok

!xxx 1922: +0 "db.py" kii 15/07/28 17:18:00
	ok

!xxx 1923: +0 "db.py" kii 15/07/28 17:21:00
	

!xxx 1924: +0 "db.py" kii 15/07/28 17:21:00
	

!xxx 1925: +0 "db.py" kii 15/07/28 17:23:00
	

!xxx 1926: +0 "db.py" kii 15/07/28 20:27:13
	

!xxx 1927: +0 "db.py" kii 15/07/28 20:27:44
	

!xxx 1928: +0 "db.py" kii 15/07/28 20:28:49
	

!xxx 1929: +0 "db.py" kii 15/07/28 20:31:24
	

!xxx 1930: +0 "dbSql.py" kii 15/07/28 20:36:47
	

!xxx 1931: +0 "dbSql.py" kii 15/07/28 20:37:36
	

!xxx 1932: +0 "db.py" kii 15/07/29 01:11:22
	

!xxx 1933: +0 "db.py" kii 15/07/29 01:11:36
	ok

!xxx 1934: +0 "db.py" kii 15/07/29 01:18:20
	ok1

!xxx 1935: +0 "db.py" kii 15/07/29 01:18:25
	testtt

!xxx 1936: +0 "" kii 15/07/29 01:18:29
	

!xxx 1938: +0 "dbSql.py" kii 15/07/29 01:34:28
	test1

!xxx 1939: +0 "dbSql.py" kii 15/07/29 01:34:26
	test2

!xxx 1940: +0 "dbSql.py" kii 15/07/29 01:34:25
	oe

+cleanup 1941: +5 "dbHttp.py" kii 15/07/30 01:06:21
	clean away after st3 test

+file, cleanup 1942: +1 "" kii 15/08/22 03:45:09
	make reservation for 'file', storing maxId in file itself

!xxx 1943: +0 "db.py" kii 15/07/29 15:49:35
	ok

+xxx 1944: +0 "db.py" kii 15/07/29 15:47:56
	

!xxx 1945: +0 "" kii 15/07/29 15:48:44
	

!xxx 1946: +0 "" kii 15/07/29 15:49:09
	

!xxx 1947: +0 "" kii 15/07/29 15:49:17
	

!xxx 1948: +0 "" kii 15/07/29 15:52:56
	

!general 1950: +0 "" kii 15/07/29 16:01:35
	

!general 1951: +0 "db.py" kii 15/07/29 16:02:25
	

!xxx 1952: +0 "db.py" kii 15/07/29 16:03:10
	

!xxx 1953: +0 "" kii 15/07/29 16:03:21
	

!xxx 1954: +0 "" kii 15/07/29 16:03:35
	

!xxx 1955: +0 "" kii 15/07/29 16:03:39
	

!xxx 1956: +0 "" kii 15/07/29 16:03:43
	

!command, fix, find 1962: +0 "commands_find.py" kii 15/07/30 03:51:13
	

!command, fix, find 1963: +0 "commands_find.py" kii 15/07/30 03:51:29
	

!db, feature, uncertain 1965: +1 "db.py" kii 16/09/12 04:34:52
	add redmine engine

!db, cleanup 1974: +0 "" kii 15/08/04 02:46:29
	overwork

+http 1976: +0 "dbHttp.py" kii 15/08/04 04:52:13
	refactor http error messaging

!xxx 1977: +0 "" kii 15/08/04 04:52:43
	yyy

!command, find, fix 1978: +0 "" kii 16/09/13 02:09:13
	wut

! 1979: +0 "README.rst" kii 15/08/07 02:17:18
	" right in your code

! 1980: +0 "README.rst" kii 15/08/07 02:17:12
	`` comment right in your code,

+change, file 1982: +0 "dbFile.py" kii 15/08/18 20:43:55
	store seconds in file

 db, issue, fix 1984: +0 "db.py" kii 17/01/24 20:01:02
	some db's are skipped at exit if *some* dbs configured (tested 3 other than File)

!xxx 1988: +0 "dbFile.py" kii 15/08/19 02:41:48
	

!xxx 1989: +0 "dbFile.py" kii 15/08/19 02:37:57
	

!xxx 1990: +0 "dbFile.py" kii 15/08/19 02:37:54
	

!xxx 1991: +0 "dbFile.py" kii 15/08/19 02:41:45
	1

!xxx 1992: +0 "dbFile.py" kii 15/08/19 02:41:42
	

!xxx 1994: +0 "dbFile.py" kii 15/08/19 02:39:52
	

!xxx 1996: +0 "dbFile.py" kii 15/08/19 02:39:51
	

!xxx 2000: +0 "db.py" kii 15/08/21 23:58:44
	

!xxx 2001: +0 "dbFile.py" kii 15/08/21 23:57:42
	

!xxx 2002: +0 "dbFile.py" kii 15/08/21 23:57:41
	

!xxx 2003: +0 "db.py" kii 15/08/21 23:58:44
	

!xxx 2004: +0 "dbFile.py" kii 15/08/21 23:57:40
	

!xxx 2006: +0 "db.py" kii 15/08/21 23:58:43
	

!xxx 2008: +0 "db.py" kii 15/08/21 23:58:42
	

!xxx 2009: +0 "dbFile.py" kii 15/08/21 23:58:38
	

!xxx 2012: +0 "dbFile.py" kii 15/08/22 02:26:00
	

!xxx 2014: +0 "dbFile.py" kii 15/08/22 02:25:21
	

!xxx 2015: +0 "dbFile.py" kii 15/08/22 02:25:20
	

!xxx 2016: +0 "dbFile.py" kii 15/08/22 02:25:59
	

!xxx 2017: +0 "dbFile.py" kii 15/08/22 02:25:59
	

!xxx 2018: +0 "dbFile.py" kii 15/08/22 02:25:58
	

!xxx 2019: +0 "dbFile.py" kii 15/08/22 02:25:18
	

!xxx 2020: +0 "dbFile.py" kii 15/08/22 02:25:57
	

+file, db 2027: +0 "dbFile.py" kii 15/08/22 03:25:51
	flushing stores old header

+cleanup, sql 2039: +0 "dbSql.py" kii 15/09/23 14:48:18
	PyMySql folder changed

!issue 2042: +0 "" kii 15/09/28 15:30:46
	fghfgh

 db, issue, fix 2045: +0 "db.py" kii 17/01/24 20:00:50
	New Id sync warning when having 2 http noticed

+interaction 2053: +0 "typeTodo.py" kii 15/11/08 22:11:11
	make more comment prefixes

!xxx 2054: +0 "typeTodo.py" kii 15/11/08 18:50:02
	yesy

!xxx 2055: +0 "c.py" kii 16/03/01 20:03:55
	test todo1

!xxx 2056: +0 "c.py" kii 16/03/01 20:03:51
	test2

!xxx 2057: +0 "c.py" kii 15/11/08 19:29:08
	!

!xxx 2058: +0 "c.py" kii 15/11/08 19:29:25
	

!xxx 2059: +0 "c.py" kii 15/11/08 19:29:33
	

!xxx 2060: +0 "c.py" kii 15/11/08 19:30:15
	

!xxx 2061: +0 "c.py" kii 15/11/08 19:30:22
	

!xxx 2062: +0 "c.py" kii 15/11/08 22:07:05
	t1

!xxx 2063: +0 "" kii 15/11/08 22:07:07
	t2

!xxx 2064: +0 "c.py" kii 15/11/08 22:07:08
	t3

!xxx 2065: +0 "c.py" kii 15/11/08 22:07:09
	t4'

!xxx 2066: +0 "c.py" kii 15/11/08 22:07:11
	t5

!xxx 2067: +0 "c.py" kii 15/11/08 22:07:12
	t6

!xxx 2068: +0 "c.py" kii 15/11/08 22:07:13
	t7

!xxx 2069: +0 "c.py" kii 15/11/08 23:12:11
	

!xxx 2070: +0 "typeTodo.py" kii 15/11/08 23:15:30
	

!xxx 2071: +0 "c.py" kii 15/11/08 23:16:27
	sql test

!interaction, db 2072: +0 "commands_find.py" kii 16/09/17 01:06:57
	save db prior to jumping to File

+fix, consistency 2073: +0 "commands_maintain.py" kii 16/09/12 05:54:46
	unneeded colorize in ordinary search

+feature, interaction, ux 2074: +0 "c.py" kii 16/09/18 18:53:52
	split Open state to Pending('') and Open('-')

+interaction, ui 2080: +0 "commands_maintain.py" kii 16/09/16 05:09:46
	re-enable old inconsistent doplets hilited

+find 2081: +0 "commands_find.py" kii 16/09/13 00:37:00
	speed up

! 2082: +0 "messages\install.txt" kii 16/09/12 18:04:24
	

!general 2083: +0 "README.rst" kii 16/09/12 21:25:45
	`` or ``#todo:`` comment right in your code,

!general 2084: +0 "README.rst" kii 16/09/12 21:08:56
	

!xxx 2088: +0 "" kii 16/09/13 02:13:51
	ok

!xxx 2089: +0 "changelog.txt" kii 16/09/13 02:14:18
	test

!xxx 2090: +0 "changelog.txt" kii 16/09/13 02:14:29
	test

!xxx 2091: +0 "" kii 16/09/13 02:14:51
	ok

!fix 2092: +0 "" kii 16/09/19 05:10:17
	its ok

! 2093: +0 "" kii 16/09/18 17:31:22
	add project name to http config

+feature, command 2095: +0 "commands_find.py" kii 16/09/14 04:01:23
	jump from .do

!spike 2096: +0 "dbFile.py" kii 16/09/16 05:43:10
	ignore inconsistency for '' to '-' conversion	

+cleanup, spike 2097: +0 "" kii 16/09/18 17:33:01
	remove '-' to '' convert after while

!feature, consistency 2098: +0 "" kii 16/09/17 03:50:49
	check only one doplet if cursor stands on it

!ux 2099: +0 "" kii 16/09/18 17:29:06
	ask for reason BEFORE set

!xxx 2101: +0 "c.py" kii 16/09/16 04:57:48
	test

+fix 2106: +0 "commands_maintain.py" kii 16/09/17 01:19:50
	limit line lenghts prior to finditer(), here and everywhere

+fix 2107: +0 "commands_find.py" kii 16/09/16 17:37:31
	limit lines and try finditer(), same as 2106

!xxx 2109: +0 "commands_maintain.py" kii 16/09/17 03:21:26
	tets

!xxx 2110: +0 "commands_maintain.py" kii 16/09/17 03:49:29
	test

!xxx 2111: +0 "typeTodo.py" kii 16/09/17 20:02:52
	ok

 command, api 2112: +0 "" kii 17/04/02 04:42:12
	allow changing one line, inline; use in substRestore()

!xxx 2113: +0 "typeTodo.py" kii 16/09/17 20:04:45
	test

!xxx 2114: +0 "c.py" kii 16/09/18 17:44:25
	

!xxx 2115: +0 "c.py" kii 16/09/18 17:50:12
	

!xxx 2117: +0 "c.py" kii 16/09/18 17:51:31
	test

!xxx 2118: +0 "c.py" kii 16/09/18 18:40:33
	test

!xxx 2119: +0 "" kii 16/09/18 18:41:50
	test

!xxx 2121: +0 "c.py" kii 16/09/20 04:02:05
	

!xxx 2122: +0 "c.py" kii 16/09/20 04:02:10
	

!xxx 2123: +0 "c.py" kii 16/09/20 04:02:17
	

!xxx 2124: +0 "c.py" kii 16/09/20 04:02:22
	

!xxx 2125: +0 "" kii 16/09/20 04:54:02
	test

!bug 2127: +0 "" kii 17/02/13 03:42:27
	bug: 1. add task, 2. add task on http, 3. change task on http; wrong file Reserved ID

=general, ux 2128: +0 "typeTodo.py" kii 17/04/02 04:41:21
	allow '//todo xxx:' expanding into existing xxx

+file 2129: +0 "dbFile.py" kii 17/02/13 04:38:59
	store file's maxID in separate .do.id file

+cleanup 2130: +0 "typeTodo.py" kii 17/01/15 19:35:31
	make no-network console messages less annoying

 interaction, feature, unsure 2131: +0 "typeTodo.py" kii 17/04/02 04:27:54
	popup todo history

!cleanup 2132: +0 "typeTodo.py" kii 17/01/10 04:55:34
	

!feature, config 2133: +0 "" kii 17/01/13 03:30:41
	redundant

+config, feature 2135: +0 "cfg.py" kii 17/02/13 05:05:30
	move global and all local configs to package config menu

!config, feature 2136: +0 "" kii 17/03/09 03:42:20
	cancel

!config, feature 2137: +0 "" kii 17/03/09 03:44:57
	exceed

!config, feature 2138: +0 "" kii 17/02/13 06:50:19
	not needed

+cleanup 2140: +0 "commands.py" kii 17/01/19 04:17:29
	remove "Reset" command, make http's 'New Public Rep'

=feature 2141: +0 "..\..\..\Sublime Text 3\Packages\TypeTodo\typeTodo.py" kii 21/07/28 06:24:26
	232, create sub-todo's with inherited state and priority

+http, config 2142: +0 "cfg.py" kii 17/03/30 13:38:27
	allow to specify project name in http config: "project": ""

-http, api, config 2143: +0 "cfg.py" kii 17/04/02 04:33:03
	request id name from server to fill back project name

!config, feature 2144: +0 "" kii 17/03/09 03:46:29
	cancel

!config, feature 2145: +0 "" kii 17/03/09 03:47:22
	cancel

!feature ux, config 2146: +0 "" kii 17/01/19 23:04:40
	cancel

!config, feature, cleanup 2148: +0 "dbFile.py" kii 17/01/23 16:25:16
	remove in future version

!clean, config, migration 2149: +0 "cfg.py" kii 17/03/09 03:25:03
	remove after config migration

!config 2150: +0 "" kii 17/03/17 06:42:48
	canceled

+config, clean 2151: +0 "commands.py" kii 17/03/17 06:40:57
	make command relevant

 command, find 2167: +0 "commands_find.py" kii 17/02/13 06:58:40
	display find results in dropdown

!xxx 2173: +0 "task.py" kii 17/02/07 10:48:51
	test

+config, feature, cleanup, file 2175: +0 "" kii 17/03/30 13:42:21
	switch to .id files; at .newId() and .releaseId()

!xxx 2178: +0 "dbFile.py" kii 17/02/13 05:06:33
	test

! 2180: +0 "" kii 17/02/13 03:42:05
	test

+config, feature, migration 2181: +0 "cfg.py" kii 17/03/27 18:12:21
	copy config to .do.cfg json file

 command, find 2182: +0 "commands_find.py" kii 17/02/13 06:59:14
	dropdown option to display results in view

+config 2267: +0 "cfg.py" kii 17/03/30 13:41:08
	fill missing template entries

+config, fix 2269: +0 "cfg.py" kii 17/03/28 16:54:40
	recreate killed config file

!xxx 2303: +0 "" kii 17/03/30 13:37:52
	test

+org, config 2306: +0 "cfg.py" kii 17/04/01 19:13:14
	establish config and 'file' names

! 2310: +0 "" kii 18/01/26 19:15:58
	Dyhjds

 tag 2318: +0 "..\..\..\Sublime Text 3\Packages\TypeTodo\typeTodo.py" kii 21/07/28 06:26:10
	sort tags by use

 site 2319: +0 "..\..\..\Sublime Text 3\Packages\TypeTodo\typeTodo.py" kii 21/07/28 06:26:38
	add notification

=ux, feature 2320: +0 "..\..\..\Sublime Text 3\Packages\TypeTodo\typeTodo.py" kii 21/07/28 06:28:01
	allow 'dd' type

=site 2321: +1 "..\..\..\Sublime Text 3\Packages\TypeTodo\typeTodo.py" kii 21/07/28 06:28:49
	use sequrity key instead of log-pass

=feature, ux, keyboard 2322: +0 "..\..\..\Sublime Text 3\Packages\TypeTodo\typeTodo.py" kii 21/07/28 06:30:09
	allow alt-d-d for all commands even on ordinary rows

=feature, ux, keyboard 2323: +0 "..\..\..\Sublime Text 3\Packages\TypeTodo\typeTodo.py" kii 21/07/28 06:33:04
	Create New from within alt-d-d

 feature, ux, keyboard 2324: +0 "..\..\..\Sublime Text 3\Packages\TypeTodo\typeTodo.py" kii 21/07/28 06:33:28
	Create New Child with altdd over exicsting

 feature, ux, keyboard 2325: +0 "..\..\..\Sublime Text 3\Packages\TypeTodo\typeTodo.py" kii 21/07/28 06:34:52
	Create Parent with altdd over existing

 feature, ux, keyboard 2326: +0 "..\..\..\Sublime Text 3\Packages\TypeTodo\typeTodo.py" kii 21/07/28 06:34:58
	Create Parent for selected with altdd

 feature, ux, keyboard, unsure 2327: +0 "..\..\..\Sublime Text 3\Packages\TypeTodo\typeTodo.py" kii 21/07/28 06:36:11
	Set Parent for current todo

=general 2328: +10 "..\..\..\Sublime Text 3\Packages\TypeTodo\typeTodo.py" kii 21/07/28 06:37:26
	Split Sublime 2 version out of maintainance 

