### infra/database/connection.py
"""
Conexão com o banco de dados MySQL via SQLAlchemy + PyMySQL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session():
    """Gerador de sessão do banco de dados (context manager manual).

    Yields:
        Sessão SQLAlchemy ativa. Deve ser fechada pelo consumidor.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
