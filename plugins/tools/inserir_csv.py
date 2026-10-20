import pandas as pd
from pathlib import Path
from plugins.info import Info
from plugins.controller import Controller


class InsertCsv:

    def __init__(self):
        self.file = Path(Info.CSV / 'dados.csv')
        self.insert_csv()
        

    
    def insert_csv(self):
        con = Controller()
        con.realizar_login('root', 'root')

        df = pd.read_csv(self.file)

        date = set()
        lista = df['day'].apply(self.ano_mes)
        for data in lista:
            date.add(data)
        
        for data in date:
            con.create_table(data)
        
        print("Tabelas criadas realizadas")


        for _, line in df.iterrows():
            con.insert_data(line['day'], line['transition_name'], line['value'], line['type_value'], line['description'])
        
        print("Dados Inseridos")

    def ano_mes(self, data: str)->str:

        data = data.split('-')
        data = data[0] + '-' + data[1]

        return data
