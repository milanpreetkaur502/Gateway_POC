function showServerSelect() {
  document.getElementById('showCard').style.display='none';
  document.getElementById('serverSelect').style.display='block';
}

function cancelConfig() {
  document.getElementById('serverSelect').style.display='none';
  document.getElementById('statusSelect').style.display='none';
  document.getElementById('showCard').style.display='block';
}
function showStatusSelect() {
  document.getElementById('showCard').style.display='none';
  document.getElementById('statusSelect').style.display='block'; 
}

function afterServerSelection() {
  let selection=document.getElementById('serverSelectBox');
  selection.disabled=true;
  var a=document.getElementById('cancelContBtnWrap').style.display='none';
  if (selection.value==1){
    document.getElementById('customForm').style.display='block';
  }else{
    document.getElementById('awsForm').style.display='block';
  }
}

function resetConfig(){
  document.getElementById('serverSelectBox').disabled=false;
  document.getElementById('cancelContBtnWrap').style.display='block';
  document.getElementById('customForm').style.display='none';
  document.getElementById('awsForm').style.display='none';
}