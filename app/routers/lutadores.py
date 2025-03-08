from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional

from database.db_config import get_db
from database.models.Lutador import Lutador
from database.schemas.LutadorSchema import LutadorSchema

router = APIRouter()

@router.get("/", response_model=List[LutadorSchema])
async def listar_lutadores(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    nome_lutador: Optional[str] = Query(None, description="Filtrar por nome do lutador"),
    apelido_lutador: Optional[str] = Query(None, description="Filtrar por apelido do lutador"),
    sexo_lutador: Optional[str] = Query(None, description="Filtrar por sexo do lutador (M/F)"),
    idade_lutador: Optional[int] = Query(None, description="Filtrar por idade do lutador"),
    categoria_lutador: Optional[str] = Query(None, description="Filtrar por categoria do lutador")
):
    query = select(Lutador)
    filters = []

    if nome_lutador:
        filters.append(Lutador.nome_lutador.ilike(f"%{nome_lutador}%"))
    if apelido_lutador:
        filters.append(Lutador.apelido.ilike(f"%{apelido_lutador}%"))
    if sexo_lutador:
        filters.append(Lutador.sexo == sexo_lutador)
    if idade_lutador:
        filters.append(Lutador.idade_lutador == idade_lutador)
    if categoria_lutador:
        filters.append(Lutador.categoria.ilike(f"%{categoria_lutador}%"))

    if filters:
        query = query.where(and_(*filters))

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    return result.scalars().all()