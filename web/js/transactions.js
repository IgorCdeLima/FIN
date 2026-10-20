window.addEventListener("pywebviewready",()=>{
    get_transiction()
});


function get_transiction(){
    window.pywebview.api.get_transiction().then(datas=>{
        const option_t = document.getElementById("transictions");
        const data = datas.transiction;
        data.forEach(name => {
            const option = document.createElement("option");
            option.value = name;
            option.textContent = name;
            option_t.appendChild(option)
        });
        
    });
}


document.getElementById("insert_t").addEventListener("click",()=>{
    
    const name = document.getElementById("transiction_name").value;
    if(name == ""){
        document.getElementById("msg").innerText = "ⓘ Insira um valor válido"
        return
    }
    insert_transactions(name)
    
})

function insert_transactions(name){
    window.pywebview.api.insert_transictions(name).then(res=>{
    
        if(res.ok){
            const select = document.getElementById('transictions');
            select.innerHTML = '';
            get_transiction()
            select.innerHTML = '<option value="">Transações</option>';

        }
        document.getElementById("msg").innerText = res.msg

    });

}