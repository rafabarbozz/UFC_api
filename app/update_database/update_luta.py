from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database.models.Luta import Luta
import pandas as pd

# Atualiza ou cria lutas no banco de dados baseado no DataFrame fornecido.
async def update_fights(df_fights: pd.DataFrame, db: AsyncSession):
    for _, row in df_fights.iterrows():
        try:
            # Obtém o lutador a partir do nome para adicionar na luta usando execute
            sql = text("SELECT * FROM lutadores WHERE nome_lutador = :nome")
            result_red = await db.execute(sql, {"nome": row['red_name']})
            fighter_red = result_red.fetchone()

            if not fighter_red:
                print(f"Lutador não encontrado: {row['red_name']}")
                continue

            result_blue = await db.execute(sql, {"nome": row['blue_name']})
            fighter_blue = result_blue.fetchone()

            if not fighter_blue:
                print(f"Lutador não encontrado: {row['blue_name']}")
                continue

            # Cria uma nova instância de Luta com os dados do DataFrame
            nova_luta = Luta(
                label=row['label'],
                red_id=fighter_red.id_lutador,
                red_link=row['red_link'],
                red_total_str=row['red_total_str'],
                red_takedowns=row['red_takedowns'],
                red_sub_att=row['red_sub_att'],
                red_reversals=row['reversals'],
                red_sig_str=row['red_sig_str'],
                red_knockdowns=row['red_knockdowns'],
                red_head_sig_str=row['red_head_sig_str'],
                red_body_sig_str=row['red_body_sig_str'],
                red_leg_sig_str=row['red_leg_sig_str'],
                red_distance_sig_str=row['red_distance_sig_str'],
                red_clinch_sig_str=row['red_clinch_sig_str'],
                red_ground_sig_str=row['red_ground_sig_str'],
                blue_id=fighter_blue.id_lutador,
                blue_link=row['blue_link'],
                blue_total_str=row['blue_total_str'],
                blue_takedowns=row['blue_takedowns'],
                blue_sub_att=row['blue_sub_att'],
                blue_reversals=row['reversals'],
                blue_sig_str=row['blue_sig_str'],
                blue_knockdowns=row['blue_knockdowns'],
                blue_head_sig_str=row['blue_head_sig_str'],
                blue_body_sig_str=row['blue_body_sig_str'],
                blue_leg_sig_str=row['blue_leg_sig_str'],
                blue_distance_sig_str=row['blue_distance_sig_str'],
                blue_clinch_sig_str=row['blue_clinch_sig_str'],
                blue_ground_sig_str=row['blue_ground_sig_str'],
                fin_method=row['fin_method'],
                fight_time=row['fight_time'],
                rounds=row['rounds'],
                weight_class=row['weight_class'],
                event_name=row['event_name'],
                fight_date=row['fight_date'],
                title_bout=row['title_bout'],
            )

            # Adiciona a nova luta à sessão e commita
            db.add(nova_luta)
            await db.commit()

        except SQLAlchemyError as e:
            await db.rollback()
            print(f"Erro inesperado ao processar a luta - {row['event_name']}: {row['red_name']} vs {row['blue_name']}")
            print(e)
            continue
        except KeyError as e:
            await db.rollback()
            print(f"Erro inesperado ao processar a luta - {row['event_name']}: {row['red_name']} vs {row['blue_name']}")
            print(f"Chave não encontrada no DataFrame: {e}")
            continue
        except Exception as e:
            await db.rollback()
            print(f"Erro inesperado ao processar a luta - {row['event_name']}: {row['red_name']} vs {row['blue_name']}")
            print(e)
            continue