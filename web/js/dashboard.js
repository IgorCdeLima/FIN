let chart = null
let myChart = null
document.addEventListener("DOMContentLoaded",()=>{
    window.addEventListener('pywebviewready', ()=>{

        const grafic = document.getElementById('chart-mensal');
        if(!grafic) {
            alert("Gráfico não carregado")
            }
        chart = echarts.init(grafic);
        const chartDom = document.getElementById("pieChart");
        if(!chartDom){
            alert("pizza não carregada")
        }
        myChart = echarts.init(chartDom);

        window.pywebview.api.today().then(today=>{
            dashboard(today,1, chart);
            pizza_grafic(today,4,myChart);
            get_saldo(today, 4)
            const ano = today.split("-")[0]
            get_year()
            get_month(ano)
        })
    });

})


const yearSelector = document.getElementById('year_selector');
const monthSelector = document.getElementById('month_selector');


// Atualiza o gráfico quando o usuário muda a seleção
yearSelector.addEventListener('change', updateChart);
yearSelector.addEventListener('change', ()=>{
    monthSelector.innerHTML = '<option value="">Mês⏷</option>';
    get_month(yearSelector.value);
})
monthSelector.addEventListener('change', updateChart);

// Click listeners registrados uma vez
document.getElementById("day").addEventListener("click", () => {
    const date = `${yearSelector.value}-${monthSelector.value}`;
    dashboard(date, 1, chart);
    pizza_grafic(date, 1, myChart);
    get_saldo(date, 1);
});
document.getElementById("month").addEventListener("click", () => {
    const date = `${yearSelector.value}-${monthSelector.value}`;
    dashboard(date, 2, chart);
    pizza_grafic(date,2, myChart);
    get_saldo(date, 2);
});
document.getElementById("year").addEventListener("click", () => {
    const date = `${yearSelector.value}-${monthSelector.value}`;
    dashboard(date, 3, chart);
    pizza_grafic(date, 3, myChart);
    get_saldo(date, 3);
});
document.getElementById("total").addEventListener("click",()=>{
    const date = "2020-12";
    pizza_grafic(date, 4, myChart);
    get_saldo(date, 4);
} );

window.addEventListener('resize', () => {
        chart.resize();
        myChart.resize();
});

function updateChart() {
    const selectedYear = yearSelector.value;
    const selectedMonth = monthSelector.value;
    if (selectedYear && selectedMonth) {
        const date = `${selectedYear}-${selectedMonth}`;
        dashboard(date, 1, chart);
        pizza_grafic(date, 1, myChart);
        get_saldo(date, 1);
    }
}

function dashboard(date, tipo, chart){
    
    window.pywebview.api.dashboard(date, tipo).then(respost => { // Lembre-se de passar os parâmetros year e month
        const res = respost[0];
        var data = respost[1];
        
        if (res.ok) {
            // Extrair os dados de "Entrada" e "Saída"
            let labels;
            let titulo;
            if(tipo == 1) {
                labels =  data.map(item => item.day);
                titulo = "Gastos Diários";
            }; // Pegue os dias da tabela
            if(tipo == 2) {
                labels = data.map(item=>item.month);
                titulo = "Gastos Mensais";
            };
            if(tipo == 3) {
                labels = data.map(item=>item.year);
                titulo = "Gastos Anuais";
            };
            const entries = data.map(item => item.entry); // Pegue os valores de "Entrada"
            const exits = data.map(item => item.exit); // Pegue os valores de "Saída"

            const option = {
                backgroundColor: 'transparent',
                
                title: {
                    text: titulo,
                    left: 'center',
                    textStyle: {
                        color: '#e5e7eb',
                        fontSize: 16,
                        fontWeight: 'normal'
                    }
                },

                tooltip: {
                    trigger: 'axis',
                    backgroundColor: '#020617',
                    borderColor: '#1f2937',
                    borderWidth: 1,
                    textStyle: {
                        color: '#e5e7eb'
                    },
                    formatter: (params) => {
                        let texto = `${params[0].axisValue}<br/>`;

                        params.forEach(item => {
                            const isExit = item.seriesName === 'Saída';
                            const sinal = isExit ? '-' : '';
                            const valorFormatado = tool_value(parseFloat(item.value).toFixed(2));

                            texto += `
                                <span style="color:${item.color}">●</span>
                                ${item.seriesName}: ${sinal}${valorFormatado}<br/>
                            `;
                        });

                        return texto;
                    }
                },

                legend: {
                    top: 30,
                    textStyle: {
                        color: '#9ca3af'
                    },
                    data: ['Entrada', 'Saída']
                },

                grid: {
                    left: 50,
                    right: 30,
                    top: 80,
                    bottom: 40,
                    backgroundColor: '#020617',
                    borderColor: '#1f2937',
                    borderWidth: 1
                },

                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: labels, // Usar os dias dinâmicos
                    axisLine: {
                        lineStyle: { color: '#374151' }
                    },
                    axisLabel: {
                        color: '#9ca3af'
                    }
                },

                yAxis: {
                    type: 'value',
                    axisLine: {
                        lineStyle: { color: '#374151' }
                    },
                    splitLine: {
                        lineStyle: { color: '#1f2937' }
                    },
                    axisLabel: {
                        color: '#9ca3af'
                    }
                },

                series: [
                    {
                        name: 'Entrada',
                        type: 'line',
                        smooth: true,
                        data: entries, // Usar os dados de entrada dinâmicos
                        lineStyle: {
                            color: '#3b82f6',
                            width: 3
                        },
                        areaStyle: {
                            color: {
                                type: 'linear',
                                x: 0, y: 0, x2: 0, y2: 1,
                                colorStops: [
                                    { offset: 0, color: 'rgba(59,130,246,0.4)' },
                                    { offset: 1, color: 'rgba(59,130,246,0)' }
                                ]
                            }
                        },
                        symbol: 'circle',
                        symbolSize: 6
                    },
                    {
                        name: 'Saída',
                        type: 'line',
                        smooth: true,
                        data: exits, // Usar os dados de saída dinâmicos
                        lineStyle: {
                            color: '#ef4444',
                            width: 3
                        },
                        areaStyle: {
                            color: {
                                type: 'linear',
                                x: 0, y: 0, x2: 0, y2: 1,
                                colorStops: [
                                    { offset: 0, color: 'rgba(239,68,68,0.4)' },
                                    { offset: 1, color: 'rgba(239,68,68,0)' }
                                ]
                            }
                        },
                        symbol: 'circle',
                        symbolSize: 6
                    }
                ]
            };
            chart.clear();
            chart.setOption(option);

        } else {
            alert(res.msg);
        }

    });

}

function get_year(){
    window.pywebview.api.get_year().then(data =>{
        const years = data.years;
        const year_select = document.getElementById("year_selector");
        years.forEach(year => {
            const option = document.createElement("option");
            option.value = year;
            option.textContent = year;
            year_select.appendChild(option);
        });  
    })
}

function get_month(year){
    window.pywebview.api.get_months(year).then(data =>{
        const months = data.months;
        const month_select = document.getElementById("month_selector");
        months.forEach(month =>{
            const option = document.createElement("option");
            option.value = month;
            option.textContent = month;
            month_select.appendChild(option);
        })
    });
}

function pizza_grafic(date, type, myChart){

    window.pywebview.api.dashboard(date, type).then(respost=>{
        const res = respost[0];
        var data = respost[2];
        if(res.ok){
            let entry;
            let exit;
            
            entry = data.entry;
            exit = data.exit;
            const option = {
                tooltip: {
                    trigger: 'item',
                    formatter: (params)=>{
                        const value = tool_value(parseFloat(params.value).toFixed(2))
                        const isExit = params.name === "Saída";
                        const sinal = isExit ? "-": "";
                        return `${sinal}${value} (${params.percent}%)`
                    }
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    textStyle: {
                            color: '#ffffff', // branco
                            borderColor: '#bee5ff'
                    }

                },
                series: [
                    {
                        name: 'Resumo Financeiro',
                        type: 'pie',
                        radius: ['10%', '50%'], // donut
                        avoidLabelOverlap: false,
                        itemStyle: {
                            borderRadius: 8,
                            borderColor: ' #60c5ffe7',
                            borderWidth: 2
                        },
                        label: {
                            show: false,
                        },
                        emphasis: {
                            label: {
                                show: true,
                                fontSize: 16,
                                fontWeight: 'bold'
                            }
                        },
                        data: [
                            {
                                value: entry,
                                name: 'Entrada',
                                itemStyle: { color: '#3b82f6' } // azul
                            },
                            {
                                value: exit,
                                name: 'Saída',
                                itemStyle: { color: '#ff4d4f' } // vermelho
                            }
                        ]
                    }
                ]
            };
            myChart.clear()
            myChart.setOption(option);
        }
        else{
            alert(res.msg)
        }
    });
}

function tool_value(valor){
    valor = String(valor)
    valor = valor.replace(/\D/g, "");
    if (valor == ""){
        return 'R$ 0,00';
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

function get_saldo(date,type){

    window.pywebview.api.dashboard(date, type).then(saldo =>{
        const card = document.getElementById("card");
        value = parseFloat(saldo[2].card).toFixed(2);

        if (value >=0){
            card.innerText = tool_value(value);
            card.style.color = '#3b82f6';
        }
        else{
            card.innerText = "-"+tool_value(value);
            card.style.color = '#ef4444';
        }
    })
}