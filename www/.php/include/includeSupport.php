<?

function arrGet($_arr, $_field, $_default=false){
	if ($_arr==0 || $_arr==1)
	  return $_default;
	return (array_key_exists($_field, $_arr)? $_arr[$_field]: $_default);
}

function encode64($_val){
 	$_val= base64_encode($_val); 
 	return str_replace(array('+','='), array('-','_'), $_val);
}

function decode64($_val){
 	$_val= str_replace(array('-','_'), array('+','='), $_val); 
 	return base64_decode($_val);
}

class Collect{
	var $collection= array();
	function add($_id,$_itemIn,$_force=false) {
		if ($_force || !array_key_exists($_id,$this->collection))
		  $this->collection[$_id]= $_itemIn;
	}
	function get($_id,$_def=false) {
		if (!array_key_exists($_id,$this->collection))
		  return $_def;
		return $this->collection[$_id];
	}
	function count() {
		return count($this->collection);
	}
	function all(){
		return $this->collection;
	}
}

?>