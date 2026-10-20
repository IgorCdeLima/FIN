import psycopg2
from plugins.info import Info
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from decimal import Decimal
import datetime




class DataBankingPostgre:

    def __init__(self):
        self.dbname = Info.DB_NAME
        self.dbhost = Info.DB_HOST
        self.dbport = Info.DB_PORT

    def connect_db(self, user:str, password:str):

        # Conect to Data Banking

        try:
            conn = psycopg2.connect(
                dbname = self.dbname,
                user = user,
                password = password,
                host = self.dbhost,
                port = self.dbport
            )
            if conn:
                conn.close()
                return {'ok': True, "msg":  "Conectado ao banco de dados", 'next_page': "./pages/menu_principal.html"} 
            
        except Exception:
            return {'ok': False, 'msg': "Erro ao se conectar no banco de dados"}
        
    def create_new_table(self, schema:str, table_nome:str, user:str, password:str):

        try:
            conn = psycopg2.connect(
                dbname = self.dbname,
                user = user,
                password = password,
                host = self.dbhost,
                port = self.dbport
            )

            cursor = conn.cursor()

            # checking existence the table
            query_check = sql.SQL("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = {} AND table_name = {})").format(sql.Literal(str(schema)), sql.Literal(table_nome))
            cursor.execute(query_check)
            exist  = cursor.fetchone()[0]
            if exist:
                return {"ok": False, "msg":"tabela ja existe no banco de dados", "next_page": "./menu_principal.html"}

            # if no exist schema

            query_schema = sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(str(schema)))
            cursor.execute(query_schema)

            # if not exist create table
            query = sql.SQL("""
                CREATE TABLE IF NOT EXISTS {}.{}(
                           id SERIAL PRIMARY KEY,
                           day  DATE NOT NULL,
                           transition_name VARCHAR(15) NOT NULL,
                           entry    NUMERIC(12,2)   DEFAULT 0,
                           exit     NUMERIC(12,2)   DEFAULT 0,
                           description  VARCHAR(30) DEFAULT NULL
                           )
                    """).format(
                        sql.Identifier(str(schema)),
                        sql.Identifier(str(table_nome))
                    )
            print(query)
            
            cursor.execute(query)
            conn.commit()
            conn.close()

            return {'ok':True, 'msg': "Tabela criada no banco de Dados",  "next_page": "./menu_principal.html"}

        except Exception:
            return {'ok': False, 'msg': "Erro ao conectar no banco de dados",  "next_page": "./menu_principal.html"}    

    def insert_data(self, date, transition_name, value, type_value, description, user, password, schema, table_name):

        try:
            conn = psycopg2.connect(
                dbname = self.dbname,
                user = user,
                password = password,
                host = self.dbhost,
                port = self.dbport
            )
            cursor = conn.cursor()

            # Insert data on table

            query = sql.SQL(
                "INSERT INTO {}.{} (day, transition_name, {}, description) VALUES (%s, %s, %s, %s) RETURNING id;"
                ).format(
                    sql.Identifier(str(schema)),
                    sql.Identifier(table_name),
                    sql.Identifier(type_value)
                    )

            cursor.execute(query, (date, transition_name, value, description))
            inserting = cursor.fetchone()
            cursor.close()
            conn.commit()
            conn.close()

            if inserting:
                return {"ok": True, "msg": "Inserção concluida no banco de dados"}
            else:
                return {"ok": False, "msg": "Dado não foi inserido no banco de dados"}

            
        except Exception:
            return {"ok": False, "msg": "Erro ao se conectar no banco de dados"}

    def print_table(self, user, password, schema, table_name):

        try:
            conn = psycopg2.connect(
                dbname = self.dbname,
                user = user,
                password = password,
                host = self.dbhost,
                port = self.dbport
            )
            with conn.cursor(cursor_factory=RealDictCursor ) as cursor:

                query = sql.SQL('SELECT day, transition_name, entry, exit, description FROM {}.{}').format(sql.Identifier(schema), sql.Identifier(table_name))


                cursor.execute(query)
                table = cursor.fetchall()
            
            conn.close()
            clean_table = [
                {key:self.serializable_value(value) for key, value in row.items()} for row in table
            ]
            print(clean_table)

            return  [{'ok': True, 'msg': 'Pesquisa realizada! Imprimindo dados'}, clean_table]

        except Exception:
            return [{'ok': False, 'msg': 'Problema com o servidor'}, []]


        
    def serializable_value(self, value):
        if isinstance(value, datetime.date):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        return value