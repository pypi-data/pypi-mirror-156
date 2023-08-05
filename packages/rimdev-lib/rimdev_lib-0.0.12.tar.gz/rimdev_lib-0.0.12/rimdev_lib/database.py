import os

import pandas as pd

from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.base import Engine
from sqlalchemy  import create_engine, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text as sa_text
from dotenv import load_dotenv

from .decoradores import trying

class RIMDB():
    driver: str
    usr_db: str
    pass_db: str
    host_db: str
    database: str
    port: str
    engine: Engine

    @trying
    def __init__(self, usr_db: str = None, pass_db: str = None, host_db: str= None, database: str = None, driver: str = 'mysql', base: str = 'DB', port: str = None) -> None:
        load_dotenv()
        self.usr_db = os.getenv(f"{base}_USER") if usr_db is None else usr_db
        self.pass_db = os.getenv(f"{base}_PASSWORD") if pass_db is None else pass_db
        self.host_db = os.getenv(f"{base}_HOSTNAME") if host_db is None else host_db
        self.database = os.getenv(f"{base}_DATABASE") if database is None else database
        self.driver = os.getenv(f"{base}_DRIVER") if driver is None else driver
        self.port = os.getenv(f"{base}_PORT") if port is None else port
        if driver == 'mssql':
            self.driver = 'mssql+pymssql'
        elif driver == 'mysql':
            self.driver = 'mysql+pymysql'
        elif driver == 'postgresql':
            self.driver = 'postgresql+psycopg2'
        self.engine = self.connect_db()
        self.engine.connect()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = SessionLocal()

    @trying
    def connect_db(self) -> Engine:
        string_connection = f'{self.driver}://{self.usr_db}:{self.pass_db}@{self.host_db}/{self.database}'
        if (self.port):
            string_connection = f'{self.driver}://{self.usr_db}:{self.pass_db}@{self.host_db}:{self.port}/{self.database}'
        self.engine = create_engine(string_connection)
        return self.engine

    @trying
    def read_db(self, query: str) -> pd.DataFrame:
        data = pd.read_sql(query, self.engine)
        return data

    @trying
    def write_db(self, query: str) -> None:
        self.engine.execute(query)
        return

    @trying
    def read_db_to_file(self, query: str, path: str) -> None:
        data = pd.read_sql(query, self.engine)
        data.to_csv(path)
        return

    @trying
    def write_db_from_dataframe(self, dataframe: pd.DataFrame, table: str, option: str = 'replace', exists: bool = False) -> None:
        dataframe.to_sql(table, self.engine, if_exists=option, index=exists)
        return

    @trying
    def write_db_from_dataframe_to_file(self, dataframe: pd.DataFrame, path: str, option: str = 'replace', exists: bool = False) -> None:
        dataframe.to_csv(path, index=exists)
        return

    @trying
    def init_table(self, table: str) -> None:
        self.engine.execute(sa_text(f'''TRUNCATE TABLE {table}''').execution_options(autocommit=True))
        return

    @trying
    def drop_table(self, table: str) -> None:
        self.engine.execute(f'DROP TABLE IF EXISTS {table}')
        return

    @trying
    def leer_modelo(self, modelo) -> pd.DataFrame:
        clase = modelo.__class__
        query = self.session.query(clase)
        ret = pd.read_sql(query.statement, self.engine)
        return ret

    def grabar_modelo(self, modelo) -> bool:
        try:
            clase = modelo.__class__
            query = self.session.query(clase).filter(clase.llave == modelo.llave)
            if query.first() is None:
                self.session.add(modelo)
            else:
                upd = modelo.__dict__
                del upd['_sa_instance_state']
                query.update(upd)
            self.session.commit()
            return True
        except IntegrityError as e:
            orig = str(e.orig).split(' ')[-1].split('.')[0]
            if (str(e.code) == 'gkpj'): # and (orig == documento.__tablename__):
                #print('El documento ya existe en la base de datos...', documento.id)
                print('-', end='', flush=True)
                #print(e)
                self.session.rollback()
                return False
            print('Error al grabar el modelo...', orig, modelo.__tablename__, e.code)
            raise(e)
            return False
        except Exception as e:
            print('Error al grabar el modelo...', modelo.__tablename__)
            raise(e)
            self.session.rollback()
            return False
