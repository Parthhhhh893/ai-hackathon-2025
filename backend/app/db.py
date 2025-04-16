import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch the necessary DB environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")  # Default to 5432 if not set

# Build the SQLAlchemy database URL dynamically
SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{DB_PORT}/{POSTGRES_DB}"

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("SQLALCHEMY_DATABASE_URL is not set in the environment file")

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,  # Increase pool size
    max_overflow=10,  # Allow overflow connections
    pool_timeout=30,  # Timeout after 30 seconds
    pool_recycle=1800,  # Recycle connections every 30 minutes
    pool_pre_ping=True,  # Automatically check if connections are alive before using
    echo=False,  # Disable logging of SQL queries
)



# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for your models
Base = declarative_base()

# Dependency to get the DB session
def get_db():
    """
    Dependency to provide a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
