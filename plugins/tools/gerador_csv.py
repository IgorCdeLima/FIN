import csv
import random as rd
from plugins.info import Info
from pathlib import Path

class CsvCreater:

    def __init__(self):
        self.file = Info.CSV
        self.gerar_csv_ruim()
    
    def gerar_csv_ruim(self):

        file = Path(self.file / 'dados_brutos.csv')
        with open(file, 'w', newline='', encoding='utf-8') as f:
            colunas = ['day', 'transition_name', 'entry', 'exit', 'description']
            escritor = csv.DictWriter(f, fieldnames=colunas)
            escritor.writeheader()

            for _ in range(0,5001):
                
                dia = rd.randint(1,30)
                mes = rd.randint(1,12)
                ano = rd.choice([2020,2021,2022,2023,2024,2025])
                separador = str(rd.choice(['/', '-', ':', ';'])) 
                day = str(rd.choice(
                    [
                        f"{dia}{separador}{mes}{separador}{ano}",
                        f"{ano}{separador}{mes}{separador}{dia}"
                    ]
                ))

                transition_name = rd.choice([
                    "mercado",
                    "Carro",
                    "MoTO",
                    "Musica",
                    "Faculdade",
                    "RESTAurante",
                    "Freelancer",
                    "Trabalho",
                    "Cartão de crédito",
                    "Pix",
                    "", 
                    None,
                    " "
                ])
                
                valor = f"R$ {rd.randint(1, 5000)},{rd.randint(0, 99):02d}"
                num = rd.randint(1,2)
                match num:
                    case 1:
                        entry = rd.choice([valor])
                        exit =  rd.choice([' ', "R$00,00", "R$"])
                    case 2:
                        entry = rd.choice([' ', "R$00,00", "R$"])
                        exit =  rd.choice([valor])

                
                description = rd.choice(
                    [
                        "nada",
                        "Alguma coisa",
                        "teste",
                        "",
                        " ",
                        None
                    ]
                )

                linha_ruim = {
                    "day": day,
                    "transition_name": transition_name,
                    "entry": entry,
                    "exit": exit,
                    "description": description
                }

                escritor.writerow(linha_ruim)






    