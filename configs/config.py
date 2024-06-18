from sqlalchemy import create_engine

# DB_USERNAME = "root"
# DB_PASSWORD = ""
# DB_DATABASE = "db_gethub"
# DB_HOST = "localhost"
# DB_PORT = 12469
# SECRET_KEY = ""

DB_USERNAME = "avnadmin"
DB_PASSWORD = "AVNS_cI7SxM7BMBa3H8flayO"
DB_DATABASE = "db_gethub"
DB_HOST = "gethub-mysql-gethub.g.aivencloud.com"
DB_PORT = 12469
SECRET_KEY = "UZJ!y^t*=g@Bj&b?Y5tkF%v!!P8R@Wm$E"

def get_database_engine():
    SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    return engine