<?
/*
	api lol

	should implement:

	?maxid
		reserve and return new ID

	?flush
		procceed POST setting tasks


*/
include('.php/include/includeAll.php');
include('sqldb.php');


if (!key_exists('project', $_GET))
	exit;

$DB->apply('getIdRep', $_GET['rep']);
$db_rId= $DB->fetch(0);
//if (!$db_rId) {echo 112412; exit;}

$DB->apply('getIdProj', $db_rId, $_GET['project']);
$db_pId= $DB->lastInsertId();

if (key_exists('newid', $_GET)) {
	$DB->apply('getIdUser', $_POST['user']);
	$db_uId= $DB->lastInsertId();

	$DB->apply('getMaxId', $db_pId);

	$newId= $DB->fetch(0);
	if ($newId)
	  $newId= (int)$newId +1;
	else
	  $newId= 1;

	$DB->apply('setNewTask', $newId, $db_uId, $db_pId);

	echo $newId;
	exit;
}

if (key_exists('flush', $_GET)) {
	$DB->apply('getIdUser', $_POST['user']);
	$db_uId= $DB->lastInsertId();
	foreach (explode(',', $_POST['ids']) as $taskId) {
		$DB->apply('getIdStates', $_POST["state$taskId"]);
		$db_sId= $DB->lastInsertId();
		$DB->apply('getIdFiles', $_POST["file$taskId"], $db_pId);
		$db_fId= $DB->lastInsertId();
		$DB->apply('getIdCat', $_POST["cat$taskId"], $db_pId);
		$db_cId= $DB->lastInsertId();

		$newVersion= 1;
		$DB->apply('getMaxVer', $taskId, $db_pId);
		$recentTask= $DB->fetch(0);
		if ($recentTask)
                  $newVersion= (int)$recentTask +1;

		$DB->apply('setUpdTask', $taskId, $db_sId, $db_cId, $_POST["lvl$taskId"], $db_uId, $newVersion, $db_fId, $db_pId, $_POST["comm$taskId"]);
	}

	exit;
}

$DB->apply('getTasksOldest', $db_pId);
?>

<!DOCTYPE html>
<html>
<head>
<style>
table {
 border-collapse:collapse;
}
table, td, th {
 border:1px solid #ccc;
 white-space: nowrap;
}
table tr:nth-child(even) {
 background: #eee;
}
table tr:nth-child(odd) {
 background: #ddd;
}

</style>
</head>
<body>
<table style='width:100%'><tr style='background: #fff;'><td>id</td><td>ver</td><td>state</td><td>cat</td><td>pri</td><td>user</td><td>stamp</td><td>file</td><td style='width:100%; white-space:normal;'>comment</td></tr>

<?
while ($task= $DB->fetch()){
?>
	<tr>
	<td><?=$task['id']?></td>
	<td><?=$task['version']?></td>
	<td><?=$task['namestate']?></td>
	<td><?=$task['namecat']?></td>
	<td><?=$task['priority']?></td>
	<td><?=$task['nameuser']?></td>
	<td><?=$task['stamp']?></td>
	<td><?=$task['namefile']?></td>
	<td><?=$task['comment']?></td>
	</tr>
<?
}
?>

</table>
</body>
</html>
<?

include('.php/include/compact.php');
?>
