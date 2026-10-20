import sqlite3
from plugins.info import Info
import hashlib
import hmac
import calendar
import os
from contextlib import closing
from pathlib import Path
import json
import pandas as pd
from plugins.tools.gerador_csv import CsvCreater
from plugins.tools.cleaner_csv import CleanerCSV

class DataBankingSQLite:

    DB = None
    TYPE_VALUES = ("entry", "exit")
    DEFAULT_TRANSACTION = "Sem categoria"

    def __init__(self):
        pass

    def connect_db(self, user:str, password:str):

        try:
            dados = self.carregar_usuario_json(user)

            if not dados:
                return {'ok': False, 'msg': "ⓘ Usuário não encontrado"}

            salt = bytes.fromhex(dados["salt"])
            hash_salvo = bytes.fromhex(dados["hash"])

            # verifica senha
            if not self.verificar_senha(password, salt, hash_salvo):
                return {'ok': False, 'msg': "ⓘ Senha incorreta"}

            pasta = Path(Info.DB / dados["token_path"])
            bd = pasta / dados["token_file"]

            if bd.exists():
                self.DB = str(bd)
                with self._connect() as conn:
                    self._create_tables(conn)
                    conn.commit()
                return {'ok': True, "msg": "ⓘ Conectado ao banco", 'next_page': "./pages/menu_principal.html"}
            else:
                return {'ok': False, 'msg': "ⓘ Banco de dados não encontrado"}

        except Exception as e:
            print(e)
            return {'ok': False, 'msg': "ⓘ Erro ao se conectar no banco de dados"}

    def create_db(self, user:str, password:str, year:str, month:str, day:str):

        try:
            if self.carregar_usuario_json(user):
                return {"ok": False, "msg": "ⓘ Usuário ja existe"}

            salt, hash_s = self.gerar_hash(password)

            word = f"{user}:{salt.hex()}"
            token_path = self.gerar_token(word)

            token_file = f"{password}:{hash_s.hex()}"
            file_db = f"{self.gerar_token(token_file)}.db"

            pasta = Path(Info.DB / token_path)
            pasta.mkdir(exist_ok=False, parents=False, mode=0o700)

            bd = pasta / file_db
            bd.touch(mode=0o600)

            self.DB = str(bd)
            with self._connect() as conn:
                self._create_tables(conn)
                conn.execute(
                    "INSERT OR IGNORE INTO transictions_name(transictions) VALUES (?);",
                    (self.DEFAULT_TRANSACTION,)
                )
                conn.commit()

            # SALVAR NO JSON
            dados = {
                "salt": salt.hex(),
                "hash": hash_s.hex(),
                "token_path": token_path,
                "token_file": file_db
            }

            criou = self.salvar_usuario_json(user, dados)
            if not criou["ok"]:
                return criou

            return {'ok': True, "msg":  "ⓘ Banco de dados criado"}

        except Exception as e:
            print(e)
            return {'ok': False, 'msg': "ⓘ Erro ao criar o banco de dados"}

    def insert_data(self, year,month,day, transition_name, value, type_value, description):
        try:
            if self.DB is None:
                return {"ok": False, "msg": "ⓘ Banco não carregado!"}

            if type_value not in self.TYPE_VALUES:
                return {"ok": False, "msg": "ⓘ Tipo de valor inválido"}

            value = round(float(value), 2)

            with self._connect() as conn:
                self._insert_row(conn, year, month, day, transition_name, value, type_value, description)
                conn.commit()

            return {"ok": True, "msg": "ⓘ Dados inseridos com sucesso"}

        except Exception as e:
            print(e)
            return {"ok": False, "msg": f"ⓘ Erro ao inserir dados"}

    def print_table(self, year, month):
        try:
            with self._connect(row_factory=True) as conn:
                query = """
                    SELECT day, transition_name, entry, exit, description
                    FROM transactions
                    WHERE transactions.year  = ? and transactions.month = ?
                    ORDER BY day ASC;
                """
                rows = conn.execute(query, (year, month)).fetchall()

            clean_table = [dict(row) for row in rows]

            return [{'ok': True, 'msg': 'ⓘ Pesquisa realizada!'}, clean_table]

        except Exception as e:
            print("Erro:", e)
            return [{'ok': False, 'msg': 'ⓘ Problema com o servidor'}, []]

    def insert_csv(self):
        try:
            if self.DB is None:
                return {"ok": False, "msg": "ⓘ Banco não carregado!"}

            CsvCreater()
            CleanerCSV()

            self.file = Path(Info.CSV / "dados.csv")

            if not self.file.exists():
                print("CSV não encontrado")
                return {"ok": False, "msg": "ⓘ CSV não encontrado"}

            with self._connect() as conn:
                df = pd.read_csv(self.file)
                print("Inserindo dados...")

                inserted = 0
                for _, line in df.iterrows():
                    try:
                        name = line.get("transition_name")
                        value = round(float(line.get("value", 0)), 2)
                        type_value = line.get("type_value")
                        desc = line.get("description") if pd.notna(line.get("description")) else ""

                        if type_value not in self.TYPE_VALUES:
                            continue

                        year,month,day = str(line.get("day")).split("-")

                        self._insert_row(conn, year, month, day, name, value, type_value, desc)
                        inserted += 1
                    except Exception as e:
                        print(f"Erro ao inserir linha: {line}\n{e}")

                conn.commit()

            print("Dados inseridos")
            return {"ok": True, "msg": f"ⓘ {inserted} lançamentos aleatórios gerados e inseridos"}

        except Exception as e:
            print(f"Erro geral ao importar CSV: {e}")
            return {"ok": False, "msg": "ⓘ Erro ao processar CSV"}

    def dashboard(self, year, month, type_grafic):
        try:
            with self._connect(row_factory=True) as conn:

                if type_grafic == 1:
                    query = """
                        SELECT day, round(sum(entry),2) as entry, round(sum(exit),2) as exit
                        FROM transactions T
                        WHERE T.year = ? and T.month = ?
                        GROUP BY day
                        ORDER BY day;
                    """
                    rows = conn.execute(query, (year, month)).fetchall()

                elif type_grafic == 2:
                    query = """
                        SELECT month, round(sum(entry),2) as entry, round(sum(exit),2) as exit
                        FROM transactions T
                        WHERE T.year = ?
                        GROUP BY month
                        ORDER BY month;
                    """
                    rows = conn.execute(query, (year,)).fetchall()

                elif type_grafic == 3:
                    query = """
                        SELECT year, round(sum(entry),2) as entry, round(sum(exit),2) as exit
                        FROM transactions T
                        GROUP BY year
                        ORDER BY year;
                    """
                    rows = conn.execute(query).fetchall()

                else:
                    return [{'ok': False, 'msg': 'ⓘ Pesquisa do gráfico não reconhecida'}, self.day_switch(year, month), {"entry":0, "exit": 0, "card": 0}]

            table = [dict(row) for row in rows]
            if type_grafic == 2:
                table = self.month_switch(table)

            if table == []:
                if type_grafic == 3:
                    table = [{"year": year, "entry": 0, "exit": 0}]
                else:
                    table = self.day_switch(year, month)

            values = self.math_pizza(table)

            return [{'ok': True, 'msg': 'ⓘ Pesquisa realizada!'}, table, values]

        except Exception as e:
            print("Erro:", e)
            return [{'ok': False, 'msg': 'ⓘ Problema com o servidor'}, self.day_switch(year, month), {"entry":0, "exit": 0, "card": 0}]

    def get_years(self):
        try:
            with self._connect() as conn:
                years = conn.execute("SELECT DISTINCT year FROM transactions ORDER BY year DESC").fetchall()

            return {"years": [year[0] for year in years]}

        except Exception as e:
            print("Erro:", e)
            return {"years": []}

    def get_months(self, year):
        try:
            with self._connect() as conn:
                months = conn.execute(
                    "SELECT DISTINCT month FROM transactions T WHERE T.year = ? ORDER BY month ASC", (year,)
                ).fetchall()

            return {"months": [month[0] for month in months]}

        except Exception as e:
            print("Erro:", e)
            return {"months": []}

    def get_transactions_name(self):
        try:
            with self._connect() as conn:
                transactions = conn.execute(
                    "SELECT DISTINCT transictions FROM transictions_name ORDER BY transictions DESC"
                ).fetchall()

            return {"transiction": [t[0] for t in transactions]}

        except Exception as e:
            print(e)
            return {"transiction": []}

    def insert_transiction(self, name):
        try:
            with self._connect() as conn:
                cursor = conn.execute("INSERT OR IGNORE INTO transictions_name (transictions) VALUES (?)", (name,))
                conn.commit()
                data = cursor.rowcount

            if data == 0:
                return {"ok": False, "msg": f"{name} ⓘja existe"}
            else:
                return {"ok":True, "msg": "ⓘ Dado inserido"}

        except Exception as e:
            print(e)
            return {"ok":False, "msg":"ⓘ Transição não foi inserida"}

    def card_value(self):
        try:
            with self._connect() as conn:
                entry, exit = conn.execute(
                    "SELECT COALESCE(ROUND(SUM(entry),2), 0), COALESCE(ROUND(SUM(exit),2), 0) FROM transactions;"
                ).fetchone()

            entry = round(float(entry), 2)
            exit = round(float(exit), 2)
            value = round(entry - exit, 2)

            return [{"ok": True, "msg": "ⓘ Consulta realizada"}, {"card": value}, {"entry":entry, "exit": exit, "card": value}]

        except Exception as e:
            print("Erro:", e)
            return [{"ok": False, "msg": "ⓘ Problemas com o servidor"}, {"card": 0}, {"entry":0, "exit": 0, "card": 0}]

   # Tools function. it isn't local this function
    def _connect(self, row_factory=False):
        conn = sqlite3.connect(self.DB)
        if row_factory:
            conn.row_factory = sqlite3.Row
        return closing(conn)

    def _create_tables(self, conn):
        conn.execute(
            """CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year TEXT NOT NULL,
                month TEXT NOT NULL,
                day TEXT NOT NULL,
                transition_name TEXT NOT NULL,
                entry REAL DEFAULT 0,
                exit REAL DEFAULT 0,
                description TEXT DEFAULT NULL
            );
            """
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS transictions_name (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transictions TEXT NOT NULL UNIQUE
            );
            """
        )

    def _insert_row(self, conn, year, month, day, transition_name, value, type_value, description):
        if type_value not in self.TYPE_VALUES:
            raise ValueError(f"Tipo de valor inválido: {type_value}")

        sql = f"""
            INSERT INTO transactions(year,month,day, transition_name, {type_value}, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        conn.execute(sql, (year, month, day, transition_name, value, description))

    def gerar_hash(self, password:str)->tuple[bytes, bytes]:

        salt  = os.urandom(16)
        hash_senha = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100_000
        )
        return salt, hash_senha

    def verificar_senha(self, password:str, salt: bytes, hash_salvo:bytes)->bool:
        novo_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100_000
        )
        return hmac.compare_digest(novo_hash, hash_salvo)

    def gerar_token(self, word:str)->str:

        token = hashlib.sha256(word.encode('utf-8')).hexdigest()
        return token

    def salvar_usuario_json(self, user, dados):
        CONFIG = Path(Info.USERS_JSON )
        config = {}

        # Carrega com segurança
        try:
            if CONFIG.exists():
                config = json.loads(CONFIG.read_text())
        except json.JSONDecodeError:
            config = {}  # arquivo vazio ou corrompido

        if user not in config:
            config[user] = dados
        # Salva com segurança
            CONFIG.write_text(json.dumps(config, indent=4, ensure_ascii=False))
            return {"ok": True}
        else:
            return {"ok": False , "msg": "ⓘ Usuário ja existe"}


    def carregar_usuario_json(self, user):
        CONFIG = Path(Info.USERS_JSON )
        try:
            if CONFIG.exists():
                data = json.loads(CONFIG.read_text())
                return data.get(user)
        except json.JSONDecodeError:
            return None  # json vazio ou quebrado
        return None

    def month_switch(self, data):
        month_names = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                    "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

        new_data = []

        # Converte keys para inteiro e ignora entradas inválidas
        data_dict = {}
        for line in data:
            try:
                m = int(line.get("month"))
                if 1 <= m <= 12:
                    data_dict[m] = line
            except:
                continue  # ignora valores inválidos

        for m in range(1, 13):
            if m in data_dict:
                line = data_dict[m]
                line["month"] = month_names[m - 1]
                new_data.append(line)
            else:
                new_data.append({
                    "month": month_names[m - 1],
                    "entry": 0,
                    "exit": 0
                })

        return new_data

    def day_switch(self, year=None, month=None):

        try:
            days = calendar.monthrange(int(year), int(month))[1]
        except (TypeError, ValueError):
            days = 31

        data = []

        for num in range(1, days + 1):
            data.append({
                "day":num,
                "entry":0,
                "exit":0
            })

        return data

    def math_pizza(self, date):

        entry = 0
        exit = 0
        for  dic in date:
            entry += float(dic["entry"])
            exit += float(dic["exit"])

        total = entry - exit
        total = round(total,2)
        values = {"entry": round(entry, 2), "exit": round(exit, 2), "card": total}
        return values
