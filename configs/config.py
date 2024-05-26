from sqlalchemy import create_engine

# DB_USERNAME = "root"
# DB_PASSWORD = ""
# DB_DATABASE = "db_gethub"
# DB_HOST = "localhost"

DB_USERNAME = "root"
DB_PASSWORD = "MGEIQHGNLQeLRfw"
DB_DATABASE = "db_gethub"
DB_HOST = "34.101.220.106"

SECRET_KEY = "UZJ!y^t*=g@Bj&b?Y5tkF%v!!P8R@Wm$E"

def get_database_engine():
    SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_DATABASE}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    return engine
