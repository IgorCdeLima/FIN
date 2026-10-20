import webview
from plugins.info import Info
from plugins.data_banking.sqlite import DataBankingSQLite
from datetime import datetime


class Controller:

    DB = None

    def __init__(self):
        # garante diretórios antes da UI
        _ = Info.DB
        _ = Info.CSV

        address = str(Info.MENU_LOGIN)
        name = Info.NAME

        webview.create_window(
            name,
            address,
            js_api=self,
            width=1080,
            height=720,
            min_size=(500, 600)
        )
        webview.start()

    def register(self, user: str, password: str):
        today = datetime.today().strftime("%Y-%m-%d")
        year, month, day = str(today).split("-")
        if user and password:
            connection = DataBankingSQLite().create_db(
                user, password, year, month, day
            )
            return connection
        else:
            return {'ok': False, 'msg': 'ⓘ Problema na criação'}

    def realizar_login(self, user: str, password: str):
        if user and password:
            self.DB = DataBankingSQLite()
            connection = self.DB.connect_db(user, password)
            return connection
        else:
            return {'ok': False, 'msg': 'ⓘ Credenciais inválidas! tente novamente'}

    def insert_data(self, date, name: str, value, type_value: str, description: str):
        try:
            year, month, day = str(date).split("-")
            connection = self.DB.insert_data(
                year, month, day, name, value, type_value, description
            )
            return connection
        except Exception:
            return {"ok": False, "msg": 'ⓘ Verifique os valores'}

    def print_table(self, date):
        try:
            year, month = str(date).split('-')
            connection = self.DB.print_table(year, month)
            return connection
        except Exception:
            return [{'ok': False, 'msg': 'ⓘ Problema com o servidor'}, []]

    def csv_insert(self):
        try:
            return self.DB.insert_csv()
        except Exception:
            return {"ok": False, "msg": "ⓘ Erro ao processar CSV"}

    def dashboard(self, date, tipo):
        try:
            if tipo == 4:
                return self.DB.card_value()

            year, month = str(date).split("-")
            connection = self.DB.dashboard(year, month, int(tipo))
            return connection
        except Exception:
            return [{'ok': False, 'msg': 'ⓘ Problema com a consulta'}, [], {"entry": 0, "exit": 0, "card": 0}]

    def get_year(self):
        return self.DB.get_years()

    def get_months(self, year):
        return self.DB.get_months(year)

    def today(self):
        return datetime.today().strftime("%Y-%m")

    def get_card(self):
        return self.DB.card_value()

    def get_transiction(self):
        return self.DB.get_transactions_name()

    def insert_transictions(self, name):
        name = str(name)
        return self.DB.insert_transiction(name)
