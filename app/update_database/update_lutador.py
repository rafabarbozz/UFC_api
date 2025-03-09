from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from database.models.Lutador import Lutador
import pandas as pd

# Atualiza ou cria lutador no banco de dados baseado no DataFrame fornecido.
async def update_fighters(df_fighters: pd.DataFrame, db: AsyncSession):
    for _, row in df_fighters.iterrows():
        try:
            # Tenta encontrar um lutador existente pelo nome
            result = await db.execute(select(Lutador).where(Lutador.nome_lutador == row['nome_lutador']))
            existing_fighter = result.scalars().first()

            if existing_fighter:
                # Atualiza o lutador existente
                existing_fighter.sexo = row['sexo']
                existing_fighter.apelido = row["apelido"]
                existing_fighter.categoria = row['categoria']
                existing_fighter.win = row['win']
                existing_fighter.lose = row['lose']
                existing_fighter.draw = row['draw']
                existing_fighter.precisao_striking = row['precisao_striking']
                existing_fighter.sig_pe_str = row['sig_pe_str']
                existing_fighter.sig_clinch_str = row['sig_clinch_str']
                existing_fighter.sig_solo_str = row['sig_solo_str']
                existing_fighter.method_ko_tko = row['method_ko_tko']
                existing_fighter.method_dec = row['method_dec']
                existing_fighter.method_fin = row['method_fin']
                existing_fighter.golpes_sig_conectados = row['golpes_sig_conectados']
                existing_fighter.golpes_sig_absorvidos = row['golpes_sig_absorvidos']
                existing_fighter.media_quedas = row['media_quedas']
                existing_fighter.media_fin = row['media_fin']
                existing_fighter.defesa_golpes_sig = row['defesa_golpes_sig']
                existing_fighter.defesa_quedas = row['defesa_quedas']
                existing_fighter.media_knockdowns = row['media_knockdowns']
                existing_fighter.tempo_medio = row['tempo_medio']
                existing_fighter.sig_head_str = row['sig_head_str']
                existing_fighter.sig_body_str = row['sig_body_str']
                existing_fighter.sig_leg_str = row['sig_leg_str']
                existing_fighter.idade_lutador = row['idade_lutador']
                existing_fighter.altura_lutador = row['altura_lutador']
                existing_fighter.peso_lutador = row['peso_lutador']
                existing_fighter.anos_xp = row['anos_xp']
                existing_fighter.link_corpo = row['link_corpo']
                existing_fighter.link_rosto = row['link_rosto']
            else:
                # Cria um novo lutador
                novo_lutador = Lutador(
                    nome_lutador=row['nome_lutador'],
                    sexo=row['sexo'],
                    apelido=row['apelido'],
                    categoria=row['categoria'],
                    win=row['win'],
                    lose=row['lose'],
                    draw=row['draw'],
                    precisao_striking=row['precisao_striking'],
                    sig_pe_str=row['sig_pe_str'],
                    sig_clinch_str=row['sig_clinch_str'],
                    sig_solo_str=row['sig_solo_str'],
                    method_ko_tko=row['method_ko_tko'],
                    method_dec=row['method_dec'],
                    method_fin=row['method_fin'],
                    golpes_sig_conectados=row['golpes_sig_conectados'],
                    golpes_sig_absorvidos=row['golpes_sig_absorvidos'],
                    media_quedas=row['media_quedas'],
                    media_fin=row['media_fin'],
                    defesa_golpes_sig=row['defesa_golpes_sig'],
                    defesa_quedas=row['defesa_quedas'],
                    media_knockdowns=row['media_knockdowns'],
                    tempo_medio=row['tempo_medio'],
                    sig_head_str=row['sig_head_str'],
                    sig_body_str=row['sig_body_str'],
                    sig_leg_str=row['sig_leg_str'],
                    idade_lutador=row['idade_lutador'],
                    altura_lutador=row['altura_lutador'],
                    peso_lutador=row['peso_lutador'],
                    anos_xp=row['anos_xp'],
                    link_corpo=row['link_corpo'],
                    link_rosto=row['link_rosto']
                )
                db.add(novo_lutador)

            await db.commit()

        except SQLAlchemyError as e:
            await db.rollback()
            print(f"Erro inesperado ao processar o lutador com nome {row['nome_lutador']}: {e}")
            continue
        except KeyError as e:
            await db.rollback()
            print(f"Erro inesperado ao processar o lutador com nome {row['nome_lutador']}: Chave não encontrada no DataFrame - {e}")
            continue
        except Exception as e:
            await db.rollback()
            print(f"Erro inesperado ao processar o lutador com nome {row['nome_lutador']}: {e}")
            continue