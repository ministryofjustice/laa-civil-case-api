from sqlmodel import create_engine, Session
from app.config import Config


db_url = f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"

engine = create_engine(db_url, echo=Config.DB_LOGGING)


def get_session():
    with Session(engine) as session:
        yield session
