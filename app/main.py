from fastapi import FastAPI
from contextlib import asynccontextmanager

from database.db_config import engine, Base
from routers import lutadores, lutas, lutas_futuras
#import scheduler  

@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn))
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(lutadores.router, prefix="/lutadores", tags=["Lutadores"])
app.include_router(lutas.router, prefix="/lutas", tags=["Lutas"])
app.include_router(lutas_futuras.router, prefix="/lutas_futuras", tags=["Lutas Futuras"])