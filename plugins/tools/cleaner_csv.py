import pandas as pd
from plugins.info import Info
from pathlib import Path
import re

class CleanerCSV:
    def __init__(self):
        self.dados_brutos = Path(Info.CSV / 'dados_brutos.csv')
        self.dados_limpos = Path(Info.CSV / 'dados.csv')
        self.cleaner()

    def cleaner(self):
        lines = []
        tipo = None
        
        df = pd.read_csv(self.dados_brutos)
        df['day'] = df['day'].apply(self.day_cleaner)
        df['transition_name'] = df['transition_name'].apply(self.str_cleaner, t=1)
        df['entry'] = df['entry'].apply(self.valor_cleaner)
        df['exit'] = df['exit'].apply(self.valor_cleaner)
        df['description'] = df['description'].apply(self.str_cleaner, t=2)

        for _, line in df.iterrows():
            day = line['day']
            transition_name = line['transition_name']
            entry = line['entry']
            exit = line['exit']
            description = line['description']

            if (entry > 0 and exit > 0):
                tipo = 1
            elif (entry == 0 and exit == 0):
                tipo = 2
            else:
                if entry > 0 and exit == 0:
                    tipo = 3
                elif exit > 0 and entry ==0:
                    tipo = 4
                else:
                    continue


            match tipo:
                case 1:
                    continue
                case 2:
                    lines.append(
                        {
                        'day': day,
                        'transition_name': transition_name,
                        'value': entry,
                        "type_value": "entry",
                        'description': description
                    })
                    lines.append({
                        'day': day,
                        'transition_name': transition_name,
                        'value': exit,
                        "type_value": "exit",
                        'description': description
                    })

                case 3:
                    lines.append(
                            {
                            'day': day,
                            'transition_name': transition_name,
                            'value': entry,
                            "type_value": "entry",
                            'description': description
                        })
                case 4:
                    lines.append({
                        'day': day,
                        'transition_name': transition_name,
                        'value': exit,
                        "type_value": "exit",
                        'description': description
                    })

        df_dados = pd.DataFrame(lines)
        df_dados.to_csv(self.dados_limpos, index=False)

                
            


    def day_cleaner(self, day:str)->str:

        day = re.sub(r"[-;:/]", "-",day)
        day = day.split("-")

        day[0] = int(day[0])
        day[1] = int(day[1])
        day[2] = int(day[2])

        if day[2] > 1000:
            ano = day[2]
            mes = day[1]
            dia = day[0]
        else:
            ano = day[0]
            mes = day[1]
            dia = day[2]

        if mes == 2 and dia >= 29:
            dia =  28
        
        data = f"{ano}-{mes:02}-{dia:02}"
        
        return data

    def str_cleaner(self, word:str, t)->str:
        if word is None or pd.isna(word):
            if t==1:
                return "Sem categoria"
            else:
                return ""
         
        if isinstance(word, str):
            word = word.strip()
            if word == "" and t ==1:
                return "Sem categoria"
        
            return word.capitalize()
        


    def valor_cleaner(self, value:str)->float:
        if isinstance(value, str):
            value= re.sub(r"[R$ ]", "", value)
            value = value.strip().replace(",", ".")
            if value == "":
                return 0
            return float(value)
        return 0
