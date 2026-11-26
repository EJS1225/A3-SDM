from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database setup

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:140703Ml!@localhost:5432/GovernamentalSimulada"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)