import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Try to load from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip

# Database setup - use remote database URL from environment variable
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. Please set it to your remote database URL.\n"
        "You can either:\n"
        "1. Set it as an environment variable: export DATABASE_URL='your_database_url'\n"
        "2. Create a .env file with: DATABASE_URL=your_database_url\n"
        "3. Install python-dotenv to automatically load from .env file: pip install python-dotenv"
    )

# For serverless databases like Neon, we need to configure connection pooling
# and handle connection timeouts properly
connect_args = {}

# If using Neon or other serverless PostgreSQL, ensure SSL is enabled
if "neon.tech" in SQLALCHEMY_DATABASE_URL or "postgresql" in SQLALCHEMY_DATABASE_URL:
    # Add SSL mode if not already present
    if "sslmode" not in SQLALCHEMY_DATABASE_URL:
        separator = "&" if "?" in SQLALCHEMY_DATABASE_URL else "?"
        SQLALCHEMY_DATABASE_URL = f"{SQLALCHEMY_DATABASE_URL}{separator}sslmode=require"
    
    # Connection pool settings for serverless databases
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using them
        pool_recycle=300,    # Recycle connections after 5 minutes
        pool_size=5,         # Number of connections to maintain
        max_overflow=10,     # Maximum overflow connections
        connect_args=connect_args
    )
else:
    # For other databases, use standard configuration
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Create tables
def init_db():
    # Import models to ensure they're registered with Base
    from models import User, Settings, Pairing
    Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

