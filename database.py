from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL (SQLite file)
DATABASE_URL = "sqlite:///./users.db"

# Create database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session (to interact with the database)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class for models
Base = declarative_base()

class User(Base):
    __tablename__ = "users"  # Ensure table name is defined

    id = Column(Integer, primary_key=True, index=True)  # Primary key
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    university = Column(String, nullable=False)
    position = Column(String, nullable=False)

# Create database tables
Base.metadata.create_all(bind=engine)
