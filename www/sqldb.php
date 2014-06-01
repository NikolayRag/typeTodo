<?

$sqlTemplate= array(

	'makeTabCategories'=> "CREATE TABLE `categories` (
          `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
          `id_project` int(10) unsigned NOT NULL,
          `name` varchar(45) NOT NULL,
          PRIMARY KEY (`id`),
          UNIQUE KEY `Index_2` (`id_project`,`name`) USING BTREE
        ) DEFAULT CHARSET=utf8 ENGINE=MyISAM DELAY_KEY_WRITE=1",

        'makeTabFiles'=> "CREATE TABLE  `files` (
          `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
          `id_project` int(10) unsigned NOT NULL,
          `name` varchar(255) NOT NULL,
          PRIMARY KEY (`id`),
          UNIQUE KEY `Index_2` (`id_project`,`name`) USING BTREE
        ) DEFAULT CHARSET=utf8 ENGINE=MyISAM DELAY_KEY_WRITE=1",

        'makeTabReps'=> "CREATE TABLE `reps` (
	  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
	  `name` varchar(45) NOT NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE KEY `Index_2` (`name`)
	) DEFAULT CHARSET=utf8 ENGINE=MyISAM DELAY_KEY_WRITE=1;",

        'makeTabProjects'=> "CREATE TABLE  `projects` (
	  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
	  `name` varchar(45) NOT NULL,
	  `id_rep` int(10) unsigned DEFAULT '0',
	  PRIMARY KEY (`id`),
	  UNIQUE KEY `Index_2` (`name`,`id_rep`) USING BTREE
	) DEFAULT CHARSET=utf8 ENGINE=MyISAM DELAY_KEY_WRITE=1",

        'makeTabUsers'=> "CREATE TABLE  `users` (
          `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
          `name` varchar(45) NOT NULL,
          PRIMARY KEY (`id`),
          UNIQUE KEY `Index_2` (`name`)
        ) DEFAULT CHARSET=utf8 ENGINE=MyISAM DELAY_KEY_WRITE=1",
        
        'makeTabStates'=> "CREATE TABLE  `states` (
          `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
          `name` varchar(45) NOT NULL,
          PRIMARY KEY (`id`),
          UNIQUE KEY `Index_2` (`name`)
        ) DEFAULT CHARSET=utf8 ENGINE=MyISAM DELAY_KEY_WRITE=1",

        'makeTabTasks'=> "CREATE TABLE  `tasks` (
          `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
          `version` int(10) unsigned NOT NULL,
          `id_project` int(10) unsigned NOT NULL,
          `id_state` int(10) unsigned NOT NULL,
          `id_category` int(10) unsigned NOT NULL,
          `priority` int(11) NOT NULL DEFAULT '0',
          `id_user` int(10) unsigned NOT NULL,
          `stamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          `id_filename` int(10) unsigned NOT NULL,
          `comment` text,
          PRIMARY KEY (`id`,`version`,`id_project`) USING BTREE
        ) DEFAULT CHARSET=utf8 ENGINE=MyISAM DELAY_KEY_WRITE=1",



        'getIdRep'=> "
	  SELECT id FROM reps WHERE name=?
	",

        'getIdProj'=> "
	  INSERT INTO projects (id_rep,name) VALUES (?,?) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)
	",

        'getIdUser'=> "
  	  INSERT INTO users (name) VALUES (?) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)
	",


        'getMaxId'=> "
	  SELECT max(id) max_id FROM tasks WHERE id_project IN (?)
	",
	
        'setNewTask'=> "
	  INSERT INTO tasks (id,id_state,id_category,priority,id_user,version,id_filename,id_project,comment) VALUES (?,0,0,0,?,0,0,?,'')
	",


        'getIdStates'=> "
	  INSERT INTO states (name) VALUES (?) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)
	",

        'getIdFiles'=> "
          INSERT INTO files (name,id_project) VALUES (?,?) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)
	",

        'getIdCat'=> "
	  INSERT INTO categories (name,id_project) VALUES (?,?) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)
	",

        'getMaxVer'=> "
          SELECT max(version) FROM tasks WHERE id=? AND id_project=?
	",

        'setUpdTask'=> "
	  INSERT INTO tasks (id,id_state,id_category,priority,id_user,version,id_filename,id_project,comment) VALUES (?,?,?,?,?,?,?,?,?)
	",


	'getTasksOldest'=> "
	  SELECT * FROM (
	    SELECT id_project maxp,id maxi,max(version) maxv FROM tasks WHERE id_project=? GROUP BY id
	  ) maxv INNER JOIN tasks ON id_project=maxp AND id=maxi AND version=maxv AND version>0
	  LEFT JOIN (SELECT id idstate, name namestate FROM states) _states ON idstate=id_state
	  LEFT JOIN (SELECT id idcat, name namecat FROM categories) _cats ON idcat=id_category
	  LEFT JOIN (SELECT id iduser, name nameuser FROM users) _users ON iduser=id_user
	  LEFT JOIN (SELECT id idfile, name namefile FROM files) _files ON idfile=id_filename
	  ORDER BY stamp DESC;
	"
);

?>