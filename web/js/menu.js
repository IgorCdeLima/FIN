

function menu(){
    const login = document.getElementById("login").value;
    const senha = document.getElementById("senha").value;

    window.pywebview.api.realizar_login(login,senha).then(res =>{
        if (res.ok){
            document.getElementById("msg").innerText = res.msg;
            setTimeout(()=>{window.location.href = res.next_page;}, 200)
        }
        else
        {
            document.getElementById("msg").innerText = res.msg;
        }
    });
}

function register(){
    const login = document.getElementById("login").value;
    const senha = document.getElementById("senha").value;

    window.pywebview.api.register(login,senha).then(res =>{
        document.getElementById("msg").innerText = res.msg;
    });
}


function back(){
    window.location.href = './menu_principal.html'
}

function page_insert_data(){
    window.location.href = "./insert_data.html";
}

function insert_data(){
    const date = document.getElementById('date').value;
    const name_t = document.getElementById('transictions').value;
    const value = ((document.getElementById('value').value)).replace(/\D/g, "") / 100;
    const typel = document.querySelector('input[name=type]:checked');
    const type_value = typel ? typel.value : ""
    const description = document.getElementById('description').value;

    if (!date || !name_t || !type_value) {
        document.getElementById("msg").innerText = "Preencha todos os campos obrigatórios";
        return
    }

    window.pywebview.api.insert_data(date, name_t, value, type_value, description).then(res =>{

        document.getElementById("msg").innerText = res.msg;
    })
    setTimeout(() => {document.getElementById("msg").innerText = '';}, 3000);
    
}

function tool_value(valor){
    valor = String(valor);
    valor = valor.replace(/\D/g, "");
    if (valor == ""){
        document.getElementById('value').value = "";
        return;
    }
    valor = parseInt(valor);
    let centavos = (valor % 100).toString().padStart(2, '0');
    let reais = parseInt( valor / 100);
    let num = [];
    if (reais === 0){
        num.push(0);
    }
    else{
        while(reais > 0){
            num.unshift((reais % 1000).toString().padStart(3, '0'));
            reais = parseInt(reais/1000);
        }
        
        num[0] = parseInt(num[0]);
    }
    let valor_final = 'R$ ' + num.join('.') + ',' + centavos;
    return valor_final;
}

function atualizar_valor(valor){
    let dinheiro =  tool_value(valor) 
    document.getElementById('value').value = dinheiro;
}

function page_print_table(){
    window.location.href = './print_table.html'
}

function print_table(){
    const table_name = document.getElementById('table_name').value;

    window.pywebview.api.print_table(table_name).then(respost=>{
        const res = respost[0];
        let table_list = respost[1];        
        const table = document.getElementById('table');
        table.innerHTML = ''

        if(res.ok){
            document.getElementById('msg').innerText = res.msg;
            setTimeout(() => {document.getElementById("msg").innerText = '';}, 3000);

            table_list.forEach(item => {

                let entry = tool_value((Number(item.entry).toFixed(2)).toString())
                let exit = tool_value((Number(item.exit).toFixed(2)).toString())
                const row = document.createElement('tr');

                [item.day, item.transition_name, entry, exit, item.description ?? ""].forEach(value => {
                    const cell = document.createElement('td');
                    cell.textContent = value;
                    row.appendChild(cell);
                });
                table.appendChild(row)
            });
        }
        else{
            document.getElementById('msg').innerText = res.msg;
            setTimeout(() => {document.getElementById("msg").innerText = '';}, 3000);

        }
    })
}

function insert_csv(){
    if (!confirm("Gerar e inserir 5.001 lançamentos aleatórios para este usuário? Os lançamentos inseridos não podem ser desfeitos pelo aplicativo.")){
        return;
    }
    window.pywebview.api.csv_insert().then(res =>{
        alert(res.msg);
        if (res.ok){
            window.location.reload();
        }
    });
}


