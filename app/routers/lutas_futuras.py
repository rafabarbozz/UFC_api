from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import date

from database.db_config import get_db
from database.models.LutaFutura import LutaFutura
from database.models.Lutador import Lutador
from database.schemas.LutaFuturaSchema import LutaFuturaSchema

router = APIRouter()

@router.get("/", response_model=List[LutaFuturaSchema])
async def listar_lutas_futuras(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    categoria_luta: Optional[str] = Query(None, description="Filtrar por categoria de luta"),
    data_luta: Optional[date] = Query(None, description="Filtrar por data da luta (YYYY-MM-DD)"),
    disputa_cinturao: Optional[bool] = Query(None, description="Filtrar por disputa de cinturão"),
    nome_lutador: Optional[str] = Query(None, description="Filtrar por nome do lutador")
):
    query = select(LutaFutura)
    filters = []

    if categoria_luta:
        filters.append(LutaFutura.categoria.ilike(f"%{categoria_luta}%"))
    if disputa_cinturao is not None:
        filters.append(LutaFutura.disputa_cinturao == disputa_cinturao)
    if nome_lutador:
        query = query.join(Lutador)
        filters.append(Lutador.nome.ilike(f"%{nome_lutador}%"))

    if filters:
        query = query.where(and_(*filters))

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    return result.scalars().all()