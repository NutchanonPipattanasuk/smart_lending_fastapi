from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DATABASE_URL = "postgresql+psycopg://postgres:Password@localhost:5432/smart_lending"


engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(
    bind=engine
)


class Base(DeclarativeBase):
    pass