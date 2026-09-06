from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import my_database_url as DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=True
)

sessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

class Base(DeclarativeBase):
    pass

def get_db():
    db = sessionLocal()

    try:
        yield db
    finally:
        db.close()

