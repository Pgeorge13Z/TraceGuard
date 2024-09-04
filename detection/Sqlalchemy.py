from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    __table_args__ = (
        Index('ix_user_user_id', 'user_id'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False)
    name = Column(String(64), nullable=False, unique=True)
    email = Column(String(255))


url = 'postgresql+psycopg2://{}:{}@{}:{}/{}'
engine = create_engine('postgresql+psycopg2://postgres:123456@localhost/User')

Base.metadata.create_all(engine)