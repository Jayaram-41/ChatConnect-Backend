import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Ensure .env is loaded from the backend directory regardless of cwd
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(base_dir, ".env"))
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

fallback_needed = False
if not DATABASE_URL or "[YOUR-PASSWORD]" in DATABASE_URL or "[PASSWORD]" in DATABASE_URL:
    print("[Database] DATABASE_URL is missing or contains placeholder password '[YOUR-PASSWORD]'. Falling back to SQLite.")
    fallback_needed = True

if not fallback_needed and DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    connect_args = {}
    if DATABASE_URL.startswith("postgresql"):
        connect_args["connect_timeout"] = 5

    try:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args=connect_args
        )
        # Test connection immediately
        with engine.connect() as conn:
            pass
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        print("[Database] Connected to Supabase / PostgreSQL database successfully.")
    except Exception as e:
        print(f"[Database] Failed to connect to PostgreSQL ({e}). Falling back to SQLite.")
        fallback_needed = True

if fallback_needed:
    sqlite_path = os.path.join(base_dir, "chatconnect.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{sqlite_path}"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print(f"[Database] Active database: SQLite ({sqlite_path})")

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()