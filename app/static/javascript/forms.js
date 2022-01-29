function validateForm(){
	var x = document.forms["registerform"]["username"].value;

	if(x == null || x == ""){
		alert("El campo usuario debe estar relleno");
		return false;
	}

	x = document.forms["registerform"]["tarjeta"].value;
	if(x == null || x == "" || isNaN(x) || x.length !== 16){
		alert("El numero de tarjeta no es valido");
		return false;
	}
}