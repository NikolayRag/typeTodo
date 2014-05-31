<?

class kiSQL {
	var $db;
	var $lastSucc= 0;
	var $lastRow;
	var $callsCnt= 0;
	var $dbErr= 0;
	var $dbErrText= '';

	function __construct($_host,$_base,$_uname,$_upass){
		try {
			$this->db = new PDO("mysql:host={$_host};dbname={$_base};charset=UTF8", $_uname, $_upass, array(PDO::ATTR_PERSISTENT=>true));
		}
		catch( PDOException $Exception ) {
			$this->dbErr= $Exception->getCode();
			$this->dbErrText= $Exception->getMessage();
		}
	}

	function apply($_tmpl){
		global $sqlTemplate;

		$sqVars= func_get_args();
		foreach ($sqVars as $sqVal)
		  if (!count($sqVal))
		    return false;

		$bindVars= array();
		$searchPos= 1;
		$TSqlA= preg_replace_callback(
			'/\?/',
			function ($_in) use ($sqVars,&$bindVars,&$searchPos) {
				$nextV= $sqVars[$searchPos++];
				if (is_array($nextV))
				  $bindVars= array_merge($bindVars,$nextV);
				else
				  $bindVars[]= $nextV;
				return str_repeat('?,',count($nextV)-1) .'?';
			},
			$sqlTemplate[$_tmpl]
		);

		$this->stmt= $this->db->prepare($TSqlA);
		$this->lastSucc= $this->stmt->execute($bindVars);
		$this->callsCnt+= 1;

		if (!$this->lastSucc)
		  return false;
		return true;
	}

	function fetch($_col=false,$_def=false){
		$this->lastRow= $this->stmt->fetch();
		if ($_col===false)
		  return $this->lastRow;

		return arrGet($this->lastRow,$_col,$_def);
	}

	function lastInsertId(){
		return $this->db->lastInsertId();
	}
}

?>