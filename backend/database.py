from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase  

DATABASE_URL = "postgresql+psycopg://postgres:master@localhost:5432/youtube_rag"

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

