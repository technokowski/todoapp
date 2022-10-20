import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# For SQLite
# SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"

# For PostgreSQL
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    # For SQLite
    # SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}

    # For PostgreSQL
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
