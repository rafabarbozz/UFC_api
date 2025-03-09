import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.models.Lutador import Lutador  

# Atualiza ou cria lutador no banco de dados baseado no DataFrame fornecido.
def update_fighters(df_fighters: pd.DataFrame, db: Session):
    for _, row in df_fighters.iterrows():
        try:
            # Tenta encontrar um lutador existente pelo nome
            existing_fighter = db.query(Lutador).filter(Lutador.nome_lutador == row['nome_lutador']).first()

            if existing_fighter:
                # Atualiza o lutador existente
                existing_fighter.sexo = row['sexo']
                existing_fighter.apelido = row["apelido"]
                existing_fighter.categoria = row['categoria']
                existing_fighter.win_lutas = row['win_lutas']
                existing_fighter.loose_lutas = row['loose_lutas']
                existing_fighter.draw_lutas = row['draw_lutas']
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
                existing_fighter.tempo_medio_luta = row['tempo_medio_luta']
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
                new_fighter = Lutador(
                    nome_lutador=row['nome_lutador'],
                    sexo=row['sexo'],
                    apelido=row["apelido"],
                    categoria=row['categoria'],
                    win_lutas=row['win_lutas'],
                    loose_lutas=row['loose_lutas'],
                    draw_lutas=row['draw_lutas'],
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
                    tempo_medio_luta=row['tempo_medio_luta'],
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
                db.add(new_fighter)

            db.commit()

        except SQLAlchemyError as e:
            db.rollback()
            print(f"Erro inesperado ao processar o lutador com nome {row['nome_lutador']}: {e}")
            continue
        except KeyError as e:
            db.rollback()
            print(f"Erro inesperado ao processar o lutador com nome {row['nome_lutador']}: Chave não encontrada no DataFrame - {e}")
            continue
        except Exception as e:
            db.rollback()
            print(f"Erro inesperado ao processar o lutador com nome {row['nome_lutador']}: {e}")
            continue