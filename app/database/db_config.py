import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Carregar variáveis do .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Criando engine assíncrona
engine = create_async_engine(DATABASE_URL)

# Criando fábrica de sessões assíncronas
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# Base para os modelos
Base = declarative_base()

# Dependência do banco de dados para injeção no FastAPI
async def get_db():
    async with SessionLocal() as session:
        yield session