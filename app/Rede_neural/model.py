import os
import yaml
import pandas as pd

import sys
import os

# Adicione o diretório atual ao sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dataset_utils import create_dataset, clean_fighters_dataset

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from datetime import datetime

from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard
from keras.optimizers import Adam
from keras import regularizers
from keras.layers import LeakyReLU, Activation

from mltu.configs import BaseModelConfigs
from mltu.tensorflow.callbacks import TrainLogger


class ModelConfig(BaseModelConfigs):
    def __init__(self, input_dim=50, batch_size=32, learning_rate=0.0001, train_epochs=500):
        super().__init__()
        self.model_path = os.path.join(os.getcwd(), "Models", datetime.strftime(datetime.now(), "%Y%m%d%H%M"))
        self.input_dim = input_dim
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.train_epochs = train_epochs
        self.layers = self._build_layers()


    def _build_layers(self):
        return [
            {'units': 128, 'activation': 'LeakyReLU', 'alpha': 0.01, 'dropout': 0.2, 'regularizer': 'l2(0.01)', 'input_dim': True},
            {'units': 128, 'activation': 'LeakyReLU', 'alpha': 0.01, 'dropout': 0.2, 'regularizer': 'l2(0.01)'},
            {'units': 128, 'activation': 'LeakyReLU', 'alpha': 0.01, 'dropout': 0.2, 'regularizer': 'l2(0.01)'},
            {'units': 64, 'activation': 'LeakyReLU', 'alpha': 0.01, 'regularizer': 'l2(0.01)'},
            {'units': 1, 'activation': 'sigmoid', 'regularizer': False}
        ]
    
     
    def save_to_yaml(self, filename):
        with open(filename, 'w') as file:
            yaml.dump(self.__dict__, file)



class NeuralNetwork:
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model = None


    def nn_model(self):
        """
        Configura e constrói o modelo de rede neural sequencial com base nas configurações fornecidas.
        
        Adiciona camadas ao modelo de acordo com o dicionário de configurações, incluindo camadas densas, ativação, 
        regularização e dropout.
        """
        
        self.model = Sequential()
        
        # Percorre cada dicionário dentro da lista 'layers'
        for layer_config in self.config.layers:
            regularizer = regularizers.l2(float(layer_config['regularizer'].split('(')[1][:-1])) if layer_config['regularizer'] else None
            
            units = layer_config['units']
            
            if 'input_dim' in layer_config and layer_config['input_dim']:
                self.model.add(Dense(
                    units, 
                    input_dim=self.config.input_dim, 
                    kernel_regularizer=regularizer
                ))
            else:
                self.model.add(Dense(
                    units, 
                    kernel_regularizer=regularizer
                ))
            
            if layer_config['activation'] == 'LeakyReLU':
                self.model.add(LeakyReLU(alpha=layer_config['alpha']))
            else:
                self.model.add(Activation(layer_config['activation']))
            
            if 'dropout' in layer_config:
                self.model.add(Dropout(layer_config['dropout']))
                                   
                       
    def compile_model(self):
        """
        Compila o modelo de rede neural com as configurações definidas.
        
        Configura o otimizador, a função de perda e as métricas de avaliação para o treinamento do modelo.
        """
        
        self.model.compile(
            optimizer=Adam(learning_rate=self.config.learning_rate),  
            loss='binary_crossentropy',  
            metrics=['accuracy'],         
        )
        
        self.model.summary()
                
                
    def train_model(self, X_train, y_train, X_val, y_val):
        """
        Treina o modelo de rede neural usando os dados de treinamento e validação.

        Parâmetros:
        - X_train (array-like): Dados de entrada para treinamento.
        - y_train (array-like): Rótulos para os dados de treinamento.
        - X_val (array-like): Dados de entrada para validação.
        - y_val (array-like): Rótulos para os dados de validação.

        Retorna:
        - history (History): Objeto History contendo informações sobre o treinamento.
        """
        
        # Criando pasta para salvar modelos
        if not os.path.exists(self.config.model_path):
            os.makedirs(self.config.model_path)
        
        # Callbacks
        earlystopper = EarlyStopping(
            monitor="val_loss",  
            patience=50,         
            verbose=1,           
            mode='min'           
        )
        
        checkpoint = ModelCheckpoint(
            f"{self.config.model_path}/model.keras",  
            monitor="val_accuracy",
            verbose=1,             
            save_best_only=True,    
            mode="max"             
        )
        
        tb_callback = TensorBoard(
            log_dir=f"{self.config.model_path}/logs", 
            update_freq=1                        
        )
        
        reduceLROnPlat = ReduceLROnPlateau(
            monitor="val_accuracy",  
            factor=0.9,            
            min_delta=1e-10,         
            patience=10,            
            verbose=1,              
            mode="auto"       
        )
        
        trainLogger = TrainLogger(self.config.model_path)
        
        # Treinamento
        history = self.model.fit(
            X_train, y_train,  
            validation_data=(X_val, y_val), 
            epochs=self.config.train_epochs,  
            batch_size=self.config.batch_size, 
            callbacks=[earlystopper, checkpoint, tb_callback, reduceLROnPlat, trainLogger]  
        )
        
        return history
    
    
    def train_and_evaluate(self, df_fighters, df_fights):
        """
        Método para treinar e avaliar o modelo, incluindo a separação dos dados e a geração dos gráficos de desempenho.

        Parâmetros:
        - df_fighters (DataFrame): DataFrame com dados dos lutadores.
        - df_fights (DataFrame): DataFrame com dados das lutas.

        Retorna:
        - history (History): Objeto History contendo informações sobre o treinamento.
        """
        # Limpando dados dos lutadores
        df_fighters = clean_fighters_dataset(df_fighters)
        
        # Criando Dataset para treinar o modelo
        dataset = create_dataset(df_fighters=df_fighters, df_fights=df_fights)

        # Separando entre treino, teste e validação
        X, y = dataset.iloc[:, 1:], dataset.iloc[:, 0]
        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0, test_size=0.2)
        X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, random_state=0, test_size=0.2)

        # Criando e compilando o modelo
        self.nn_model()
        self.compile_model()

        # Treinando o modelo
        history = self.train_model(X_train, y_train, X_val, y_val)

        # Salvando configurações e modelo
        self.save_config(f'{self.config.model_path}/model_config.yaml')
        self.save_model(f"{self.config.model_path}/trained_model.h5")
        
        return history
        
    
    def previsao(self, first_fighter, second_fighter):
        """
        Prever o resultado de uma luta entre dois lutadores usando um modelo de aprendizado de máquina.
        
        Parâmetros:
        - first_fighter (str): Dataframe contendo os dados do primeiro lutador.
        - second_fighter (str): Dataframe contendo os dados do segundo lutador.
        
        Retorna:
        - Tuple: Previsões ajustadas para os dois lutadores.
        """
        
        try:
            # Filtrar e processar dados dos lutadores
            f_fighter_data = first_fighter.drop(columns=['id_lutador', 'nome_lutador', 'apelido', 'sexo', 'categoria', 'link_corpo', 'link_rosto']).add_prefix('red_')
            s_fighter_data = second_fighter.drop(columns=['id_lutador', 'nome_lutador', 'apelido', 'sexo', 'categoria', 'link_corpo', 'link_rosto']).add_prefix('blue_')
            
            # Criar DataFrames para as previsões
            fight_1 = pd.concat([f_fighter_data.reset_index(drop=True), s_fighter_data.reset_index(drop=True)], axis=1)
            fight_2 = pd.concat([s_fighter_data.reset_index(drop=True), f_fighter_data.reset_index(drop=True)], axis=1)

            colunas_normalizar = ["red_idade_lutador", "red_peso_lutador", "red_altura_lutador", "red_win_lutas", "red_loose_lutas", "red_draw_lutas", "red_sig_solo_str", 
                                "red_tempo_medio_luta", "red_golpes_sig_conectados", "red_golpes_sig_absorvidos", "red_media_quedas", "red_media_fin", "red_anos_xp",
                                
                                "blue_idade_lutador", "blue_peso_lutador", "blue_altura_lutador", "blue_win_lutas", "blue_loose_lutas", "blue_draw_lutas", "blue_sig_solo_str", 
                                "blue_tempo_medio_luta", "blue_golpes_sig_conectados", "blue_golpes_sig_absorvidos", "blue_media_quedas", "blue_media_fin", "blue_anos_xp"]

            combined_data = pd.concat([fight_1[colunas_normalizar], fight_2[colunas_normalizar]])

            # Ajustar o scaler com os dados combinados
            scaler = MinMaxScaler()
            scaler.fit(combined_data)

            # Aplicar a normalização aos conjuntos de dados
            fight_1[colunas_normalizar] = scaler.transform(fight_1[colunas_normalizar])
            fight_2[colunas_normalizar] = scaler.transform(fight_2[colunas_normalizar])

            # Predizer o resultado da luta usando o modelo
            prediction_1 = self.model.predict(fight_1, verbose=0)
            prediction_2 = self.model.predict(fight_2, verbose=0)

            # Combinar as previsões para suavizar os resultados
            pred_1 = (prediction_1 + (1 - prediction_2)) / 2
            pred_2 = (prediction_2 + (1 - prediction_1)) / 2

            return pred_1, pred_2
        
        except FileNotFoundError:
            raise FileNotFoundError("O arquivo de dados dos lutadores não foi encontrado.")
        
        except Exception as e:
            raise RuntimeError(f"Um erro ocorreu: {e}")
        
    def save_config(self, filename):
        self.config.save_to_yaml(filename)
        
    
    def save_model(self, filepath):
        self.model.save(filepath)
        
        
    def load_model(self, filepath):
        self.model = load_model(filepath)
        

