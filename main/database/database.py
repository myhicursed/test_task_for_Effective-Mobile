from sqlalchemy import create_engine
from main.configDB.config import settings
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine(
    url=settings.DATABASE_URL(),
    echo=True
)

session_factory = sessionmaker(bind=engine)

def get_session():
    db = session_factory()
    try:
        yield db
    finally:
        db.close()

class Base(DeclarativeBase):
    pass