from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.config import get_settings

settings = get_settings()
db_url = settings.DATABASE_URL

connect_args = {'check_same_thread': False}

if ':memory:' in db_url:
    engine = create_engine(
        db_url,
        connect_args=connect_args,
        poolclass=StaticPool
    )
else:
    engine = create_engine(
        db_url,
        connect_args=connect_args
    )

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@event.listens_for(engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("PRAGMA busy_timeout=5000;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    if ':memory:' not in db_url:
        cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.close()


def get_engine():
    return engine


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
