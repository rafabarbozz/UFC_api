import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.models.LutaFutura import LutaFutura  
from database.models.Lutador import Lutador 
from Rede_neural.model import NeuralNetwork, ModelConfig

# Atualiza ou cria lutas futuras no banco de dados baseado no DataFrame fornecido
def update_next_fights(df_prox_fights: pd.DataFrame, db: Session):  
    # Configuração do modelo de rede neural
    model_config = ModelConfig()
    neural_network = NeuralNetwork(model_config)
    model_path = "Rede_neural/Models/202408101459/trained_model.h5"

    try:
        neural_network.load_model(model_path)

    except FileNotFoundError:
        raise FileNotFoundError(f"O arquivo do modelo não foi encontrado no caminho: {model_path}")

    except Exception as e:
        raise RuntimeError(f"Erro ao carregar o modelo: {e}")

    for _, row in df_prox_fights.iterrows():
        # Verificando algum lutador não está na base de dados
        try:
            first_fighter_name = row['first_fighter_prox']
            second_fighter_name = row['second_fighter_prox']

            first_fighter_prox = db.query(Lutador).filter(Lutador.nome_lutador == first_fighter_name).first()
            if not first_fighter_prox:
                print(f"Lutador não encontrado: {first_fighter_name}")
                continue

            second_fighter_prox = db.query(Lutador).filter(Lutador.nome_lutador == second_fighter_name).first()
            if not second_fighter_prox:
                print(f"Lutador não encontrado: {second_fighter_name}")
                continue

        except Exception as e:
            print(f"Erro inesperado: {e}")
            continue

        # Busca os dados dos lutadores no banco de dados
        lutador_1 = pd.DataFrame([db.query(Lutador).filter(Lutador.nome_lutador == first_fighter_prox.nome_lutador).first().__dict__])
        lutador_2 = pd.DataFrame([db.query(Lutador).filter(Lutador.nome_lutador == second_fighter_prox.nome_lutador).first().__dict__])

        try:
            pred_1, pred_2 = neural_network.previsao(lutador_1, lutador_2)
        except ValueError as e:
            print(f"Erro ao fazer a previsão: {e}")
            continue

        try:
            # Cria uma nova instância de LutaFutura com os dados do DataFrame
            nova_luta_futura = LutaFutura(
                first_fighter_prox=first_fighter_prox.id_lutador,
                second_fighter_prox=second_fighter_prox.id_lutador,
                weight_class_prox=row['weight_class_prox'],
                fight_date_prox=row['fight_date_prox'],
                location_prox=row['location_prox'],
                event_name_prox=row['event_name_prox'],
                prob_victory_first=pred_1[0][0] * 100,
                prob_victory_second=pred_2[0][0] * 100,
            )

            # Adiciona a nova luta futura à sessão e commita
            db.add(nova_luta_futura)
            db.commit()

        except SQLAlchemyError as e:
            db.rollback()
            print(f"Erro inesperado ao processar a luta futura - {row['event_name_prox']}: {first_fighter_prox.nome_lutador} vs {second_fighter_prox.nome_lutador}")
            print(e)
            continue
        except KeyError as e:
            db.rollback()
            print(f"Erro inesperado ao processar a luta futura - {row['event_name_prox']}: {first_fighter_prox.nome_lutador} vs {second_fighter_prox.nome_lutador}")
            print(f"Chave não encontrada no DataFrame: {e}")
            continue
        except Exception as e:
            db.rollback()
            print(f"Erro inesperado ao processar a luta futura - {row['event_name_prox']}: {first_fighter_prox.nome_lutador} vs {second_fighter_prox.nome_lutador}")
            print(e)
            continue