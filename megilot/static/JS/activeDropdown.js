const dropDown = document.getElementById('text-length');
const opts = dropDown.options.length;

//select the dropdown element the user chose.
function activateElem(){ 
    for (var i=0; i<opts; i++){
        let dVal = dropDown.options[i].value;
        if (dVal.split("-")[1] === windowRight.toString()){
            dropDown.options[i].selected = true;
            break;
        }
    }
}
window.onload = function() {
    activateElem();
  };