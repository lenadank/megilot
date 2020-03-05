const form = document.getElementById('form');
const filesInput = document.getElementById('files');
const letInput = document.getElementById('letters');
const filesWarn = document.getElementById('filesWarn');
const letWarn = document.getElementById('letWarn');

function inValid(input,inputWarn,text, e){
    e.preventDefault();
    inputWarn.innerHTML = "<i class='fas fa-exclamation-triangle'></i>" +"   "+text;
}

//form validation
form.addEventListener('submit', (e)=>{
    const filesList = filesInput.files;
    letWarn.innerText='';
    filesWarn.innerText='';

    //validate letters input field isn't empty
    if(letInput.value === "" || letInput.value == null){
        e.preventDefault();
        inValid(letInput, letWarn, "יש להכניס לפחות אות אחת לחיפוש", e);
    }
    if(filesList.length==0 || filesList==null){
        inValid(filesInput, filesWarn, "יש לבחור לפחות קובץ אחד", e);
    }else{
        let validFileExt = true;
        let validFileName = true;
        for(let i=0; i<filesList.length; i++){  
            let fileNameArr = filesList[i].name.split('.');
            if(fileNameArr[0]===''){
                validFileName = false;
            }

            var fileName = filesList[i].name; 
            if(!(fileName.endsWith(".txt")) && !(fileName.endsWith(".docx"))){
                validFileExt = false;
            }
        }

        let fileNameWarning = [];
        if(!validFileExt){
            fileNameWarning.push("יש לצרף קבצים בעלי סיומת docx או txt בלבד");
        }   
        if(!validFileName){
            fileNameWarning.push("שם אחד הקבצים המצורפים הינו ריק");
        }
        if(!validFileExt || !validFileName){
            let warningText = fileNameWarning.join(', ')
            inValid(filesInput, filesWarn, warningText, e);
        }
        
    }
});

//Make file uploader responsive
updateFilesNum = function() {
    let inputText = document.getElementById('inputText');
    let filesNum = filesInput.files.length;
    if(filesNum==1){
        inputText.innerText= filesInput.files[0].name;
    }else{
        inputText.innerText = filesNum+" files have been selected";
    }
}