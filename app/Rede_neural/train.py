import pandas as pd
from sqlalchemy.orm import Session
from database.db_config import SessionLocal 
from database.models.Lutador import Lutador 
from database.models.Luta import Luta  
from model import ModelConfig, NeuralNetwork

def train_neural_network():
    """Treina e avalia a rede neural usando dados do banco de dados."""

    db: Session = SessionLocal()
    try:
        # Obtendo os dataframes com os dados
        fighters = pd.read_sql(db.query(Lutador).statement, db.bind)
        fights = pd.read_sql(db.query(Luta).statement, db.bind)

        # Criar a configuração do modelo
        config = ModelConfig(input_dim=51, batch_size=32, learning_rate=0.0001, train_epochs=1000)

        # Criar uma instância da classe NeuralNetwork com a configuração
        nn = NeuralNetwork(config=config)

        # Treinar e avaliar o modelo
        history = nn.train_and_evaluate(df_fighters=fighters, df_fights=fights)

        print("Treinamento e avaliação concluídos.")
        return history

    except Exception as e:
        print(f"Erro durante o treinamento: {e}")
        return None

    finally:
        db.close()

if __name__ == "__main__":
    train_neural_network()