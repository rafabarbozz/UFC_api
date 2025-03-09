import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler

def clean_fighters_dataset(df_fighters):
    """
    Função para limpar os dados dos lutadores com base em idade, altura, peso e anos de experiência.

    - Remove lutadores com todas as características (idade, altura, peso, anos de experiência) faltando.
    - Substitui valores faltantes (0) com os valores mais comuns (moda) da coluna, considerando a categoria.
    - Detecta e corrige outliers utilizando o método IQR.
    
    - df_fighters (DataFrame): DataFrame que contém os dados dos lutadores.
    """
    # Função para corrigir outliers utilizando IQR
    def correct_outliers(df, col):
        df[col] = df[col].astype(float)
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Substituir outliers acima ou abaixo por limites inferiores/superiores
        df[col] = np.where(df[col] < lower_bound, lower_bound, df[col])
        df[col] = np.where(df[col] > upper_bound, upper_bound, df[col])

        return df

    # Remover lutadores com todas as características faltando
    df_fighters = df_fighters[
        ~((df_fighters['peso_lutador'] == 0) & 
          (df_fighters['idade_lutador'] == 0) & 
          (df_fighters['altura_lutador'] == 0) & 
          (df_fighters['anos_xp'] == 0))
    ].copy()

    # Detectar e corrigir outliers em idade, altura, peso e anos de experiência
    for col in ['peso_lutador', 'idade_lutador', 'altura_lutador', 'anos_xp']:
        df_fighters = correct_outliers(df_fighters, col)

    # Substituir valores faltantes com a moda baseada na categoria
    for col in ['peso_lutador', 'idade_lutador', 'altura_lutador', 'anos_xp']:
        moda_por_categoria = (
            df_fighters[df_fighters[col] != 0]
            .groupby('categoria')[col]
            .agg(lambda x: x.value_counts().idxmax())
        )
        for categoria, valor_comum in moda_por_categoria.items():
            df_fighters.loc[
                (df_fighters['categoria'] == categoria) & (df_fighters[col] == 0), col
            ] = valor_comum

    return df_fighters



def create_dataset(df_fights: str, df_fighters: str):
    """
    Função para criar o dataset que será utilizado para treinar a rede neural
    
    - df_fights(DataFrame): DataFarame que contém os dados das lutas
    - df_fighters(DataFrame): DataFarame que contém os dados das lutadores
    """
    # Escolhendo colunas do dataframe das lutas
    df_fights = df_fights[['label', 'red_name_id', 'blue_name_id', 'title_bout']]
    
    # Fazer a limpeza dos dados dos lutadores
    fighters = clean_fighters_dataset(df_fighters)
    
    # Dataframe que recebe as informações da lutas e dos lutadores da luta    
    dataset = pd.DataFrame() 
    
    # Colocando informações do primeiro lutador no dataset
    dataset = pd.merge(df_fights, fighters, left_on='red_name_id', right_on='id_lutador').drop(columns=['id_lutador', 'nome_lutador', 'apelido', 'sexo', 'categoria', 'link_corpo', 'link_rosto'])
    
    red_columns_name = {
        'win_lutas': 'red_win_lutas',
        'loose_lutas': 'red_loose_lutas',
        'draw_lutas': 'red_draw_lutas',
        'precisao_striking': 'red_precisao_striking',
        'sig_pe_str': 'red_sig_str_pe',
        'sig_clinch_str': 'red_sig_clinch_str',
        'sig_solo_str': 'red_sig_solo_str',
        'method_ko_tko': 'red_method_ko_tko',
        'method_dec': 'red_method_dec',
        'method_fin': 'red_method_fin',
        'golpes_sig_conectados': 'red_golpes_sig_conn',
        'golpes_sig_absorvidos': 'red_golpes_sig_abs',
        'media_quedas': 'red_media_quedas',
        'media_fin': 'red_media_fin',
        'defesa_golpes_sig': 'red_defesa_golpes_sig',
        'defesa_quedas': 'red_defesa_quedas',
        'media_knockdowns': 'red_media_knockdowns',
        'tempo_medio_luta': 'red_tempo_medio',
        'sig_head_str': 'red_sig_head_str',
        'sig_body_str': 'red_sig_body_str',
        'sig_leg_str': 'red_sig_leg_str',
        'idade_lutador': 'red_idade',
        'altura_lutador': 'red_altura',
        'peso_lutador': 'red_peso',
        'anos_xp': 'red_anos_xp'
    }

    dataset = dataset.rename(columns=red_columns_name)
    
    # Colocando infomações do segundo lutador no dataset
    dataset = pd.merge(dataset, fighters, left_on='blue_name_id', right_on='id_lutador').drop(columns=['id_lutador', 'nome_lutador', 'apelido', 'sexo', 'categoria', 'link_corpo', 'link_rosto'])
    
    blue_columns_name = {
        'win_lutas': 'blue_win_lutas',
        'loose_lutas': 'blue_loose_lutas',
        'draw_lutas': 'blue_draw_lutas',
        'precisao_striking': 'blue_precisao_striking',
        'sig_pe_str': 'blue_sig_str_pe',
        'sig_clinch_str': 'blue_sig_clinch_str',
        'sig_solo_str': 'blue_sig_solo_str',
        'method_ko_tko': 'blue_method_ko_tko',
        'method_dec': 'blue_method_dec',
        'method_fin': 'blue__method_fin',
        'golpes_sig_conectados': 'blue_golpes_sig_conn',
        'golpes_sig_absorvidos': 'blue_golpes_sig_abs',
        'media_quedas': 'blue_media_quedas',
        'media_fin': 'blue_media_fin',
        'defesa_golpes_sig': 'blue_defesa_golpes_sig',
        'defesa_quedas': 'blue_defesa_que das',
        'media_knockdowns': 'blue_media_knockdowns',
        'tempo_medio_luta': 'blue_tempo_medio',
        'sig_head_str': 'blue_sig_head_str',
        'sig_body_str': 'blue_sig_body_str',
        'sig_leg_str': 'blue_sig_leg_str',
        'idade_lutador': 'blue_idade',
        'altura_lutador': 'blue_altura',
        'peso_lutador': 'blue_peso',
        'anos_xp': 'blue_anos_xp'
    }


    dataset = dataset.rename(columns=blue_columns_name)

    dataset_norm = dataset.drop(columns=['red_name_id', 'blue_name_id']).copy()

    # Colunas a serem normalizadas
    colunas_normalizar = [
        'red_win_lutas', 'red_loose_lutas', 'red_draw_lutas', 'red_golpes_sig_conn', 
        'red_golpes_sig_abs', 'red_media_quedas', 'red_media_fin', 'red_media_knockdowns', 
        'red_tempo_medio', 'red_sig_head_str', 'red_sig_body_str', 'red_sig_leg_str', 
        'red_idade', 'red_altura', 'red_peso', 'red_anos_xp',
        
        'blue_win_lutas', 'blue_loose_lutas', 'blue_draw_lutas', 'blue_golpes_sig_conn', 
        'blue_golpes_sig_abs', 'blue_media_quedas', 'blue_media_fin', 'blue_media_knockdowns', 
        'blue_tempo_medio', 'blue_sig_head_str', 'blue_sig_body_str', 'blue_sig_leg_str', 
        'blue_idade', 'blue_altura', 'blue_peso', 'blue_anos_xp'
    ]
    
    # Normalizando colunas selecionadas
    dataset_norm[colunas_normalizar] = MinMaxScaler().fit_transform(dataset_norm[colunas_normalizar])

    return dataset_norm
