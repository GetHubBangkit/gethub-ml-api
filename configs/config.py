from sqlalchemy import create_engine

DB_USERNAME = "root"
DB_PASSWORD = ""
DB_DATABASE = "db_gethub"
DB_HOST = "localhost"
DB_PORT = 12469
SECRET_KEY = ""

def get_database_engine():
    SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    return engine