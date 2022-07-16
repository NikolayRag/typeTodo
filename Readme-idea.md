Typetodo ideas:
==

TypeTodo is an onfly typewriting assistant to manage Todo comments.


Topmost APP
--
Is a text editing tracking agent.

+ Specific text patterns triggers Todo creation,
 forming proper formatted Todo comment

+ Changed Todo fields are stored within per-sublime-project DATASET.

+ On fly assist for:
 + Todo id and format protection, tags suggestion

+ DATASET inconsistency triggers back Todo comment inline update,
 - implicitely changed line is indicated within text.


Todo DATASET
--
Is a ENTRIES database driven by asynchronous agent, suitable for shared access.
+ * Distributed storage is allowed.

+ * At basic, DATASET stored within text file or MySql-compatible database.

+ * Unexistent Todo id to be used is reserved and managed for sudden Todo creation.


Todo ENTRY
--
Is formated comment showing last stored version, represented as DATASET record.

+ Stored history steps are: state, tags, priority and supplied text.

+ Implicitely stored data: Todo id, user identity, timestamp, location if any.

- Full Todo history can be accessed


Tools
--

Todo DB can be viewed for searching globally.

