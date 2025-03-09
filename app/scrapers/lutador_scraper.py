import requests
import re
import pandas as pd

from bs4 import BeautifulSoup
from tqdm import tqdm
from unidecode import unidecode

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


# Função que pega os dados dos lutadores
def get_fighters_data(link_fighters) -> pd.DataFrame:
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    # Inicializa um dicionário com todas as colunas esperadas, cada uma com uma lista vazia
    columns = ['nome_lutador', 'apelido', 'sexo', 'categoria', 'win', 'lose', 'draw', 'precisao_striking', 'sig_pe_str', 'sig_clinch_str', 'sig_solo_str',
                'method_ko_tko', 'method_dec', 'method_fin', 'golpes_sig_conectados', 'golpes_sig_absorvidos', 'media_quedas',
                'media_fin', 'defesa_golpes_sig', 'defesa_quedas', 'media_knockdowns', 'tempo_medio', 'sig_head_str', 'sig_body_str', 
                'sig_leg_str', 'idade_lutador', 'altura_lutador', 'peso_lutador', 'anos_xp','link_corpo','link_rosto']

    fighters_data_complete = {col: [] for col in columns}

    for i, link in tqdm(enumerate(link_fighters)):
        fighter_source = session.get(link).text
        soup = BeautifulSoup(fighter_source, "html.parser")
        
        # Número de vitórias, derrotas e empates
        wld_source = soup.find("p", class_="hero-profile__division-body")
        if wld_source:
            wld_source = wld_source.text.split(" ")[0].split("-") 
        else:
            continue
 
        # Se não tiver nenhuma luta não é registrado
        if wld_source[0] == '0' and wld_source[1] == '0' and wld_source[2] == '0': 
            continue
        else:
            # Categoria do lutador
            category = soup.find("p", class_="hero-profile__tag")
            category_text = re.search(r'Peso-\w+ feminino|Peso \w+-\w+|Peso-\w+', category.text)
            
            if category_text:
                category_text = category_text.group()
            else:
                category_text = 'Nan'
            
            fighters_data_complete['categoria'].append(category_text)
            
            # Sexo do lutador
            if "feminino" in category_text:
                fighters_data_complete['sexo'].append("F")
            else:
                fighters_data_complete['sexo'].append("M")
            
            
            # Nome do lutador
            name = soup.find("h1", class_="hero-profile__name")
            fighters_data_complete['nome_lutador'].append(unidecode(name.text.strip().lower()) if name else "")

            # Pegando o apelido do lutador 
            apelido = soup.find("p", class_="hero-profile__nickname")
            fighters_data_complete['apelido'].append(apelido.text.strip().replace('"','') if apelido else "")
        
            # Win, lose, draw
            fighters_data_complete['win'].append(int(wld_source[0]) if wld_source[0] else 0)
            fighters_data_complete['lose'].append(int(wld_source[1]) if wld_source[1] else 0)
            fighters_data_complete['draw'].append(int(wld_source[2]) if wld_source[2] else 0)

            # Link do corpo dos lutadores
            corpo = soup.find("div", class_="hero-profile__image-wrap")
            if corpo:
                corpo_link = str(corpo).split('src="')
                imagem_corpo_link = corpo_link[1].split('"')[0]  
            else:
                imagem_corpo_link = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTW734W8l_2Kc-8YlsF-GSBf-2UTEBO36LWfQ&s'
                 
            fighters_data_complete['link_corpo'].append(imagem_corpo_link)
  

            # Link do rosto dos lutadores
            lutadores_divs = soup.find_all('div', class_='c-card-event--athlete-results__image')
            imagem_link_rosto = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTW734W8l_2Kc-8YlsF-GSBf-2UTEBO36LWfQ&s'
            nome_procurado = fighters_data_complete['nome_lutador'][-1].split()[0].upper()
            
            for div in lutadores_divs:
                lutador_link = div.find('img')
                                            
                if lutador_link:
                    if nome_procurado in lutador_link['src']:
                        imagem_link_rosto = lutador_link['src']
                        break   
            
            fighters_data_complete['link_rosto'].append(imagem_link_rosto)

            # Precisão de striking
            striking_source = soup.find("text", class_="e-chart-circle__percent")
            fighters_data_complete['precisao_striking'].append(float(striking_source.text.replace('%', '')) / 100 if striking_source else 0)

            # Golpes significantes por posição e porcetagem por método de vitória
            fighters_info3 = soup.find_all("div", class_="c-stat-3bar__value")
            list_aux = [float(element.text.split(' ')[1].replace('(','').replace(')','').replace('%','')) / 100 for element in fighters_info3]
            if list_aux:
                for idx, col in enumerate(['sig_pe_str', 'sig_clinch_str', 'sig_solo_str', 'method_ko_tko', 'method_dec', 'method_fin']):
                    fighters_data_complete[col].append(list_aux[idx] if idx < len(list_aux) else 0)
            else:
                for col in ['sig_pe_str', 'sig_clinch_str', 'sig_solo_str', 'method_ko_tko', 'method_dec', 'method_fin']:
                    fighters_data_complete[col].append(0)

            # Estatísticas diversas
            stats = {
                "Golpes Sig. Conectados": "0", "Golpes Sig. Absorvidos": "0", "Média de quedas": "0", "Média de finalizações": "0",
                "Defesa de Golpes Sig.": "0", "Defesa de Quedas": "0", "Média de Knockdowns": "0", "Tempo médio de luta": "0"
            }
            
            # Preenche as estatísticas com valores reais ou zeros se não forem encontrados
            for record in soup.select('.stats-records--compare'):
                for group in record.select('.c-stat-compare__group'):
                    number = group.select_one('.c-stat-compare__number')
                    label = group.select_one('.c-stat-compare__label')
                    if number and label:
                        stats[label.text.strip()] = number.text.strip().replace(' ', '').replace('\n', '').replace('%', '')

            fighters_data_complete['golpes_sig_conectados'].append(float(stats['Golpes Sig. Conectados']))
            fighters_data_complete['golpes_sig_absorvidos'].append(float(stats['Golpes Sig. Absorvidos']))
            fighters_data_complete['media_quedas'].append(float(stats['Média de quedas']))
            fighters_data_complete['media_fin'].append(float(stats['Média de finalizações']))
            fighters_data_complete['defesa_golpes_sig'].append(float(int(stats['Defesa de Golpes Sig.']) / 100))
            fighters_data_complete['defesa_quedas'].append(float(int(stats['Defesa de Quedas']) / 100))
            fighters_data_complete['media_knockdowns'].append(float(stats['Média de Knockdowns']))
            
            if stats['Tempo médio de luta'] != '0':
                time_parts = stats['Tempo médio de luta'].split(':')
                fighters_data_complete['tempo_medio'].append(int(time_parts[0]) * 60 + int(time_parts[1]))
            else:
                fighters_data_complete['tempo_medio'].append(0)

            # Golpes significantes por área
            sig_strike_source = soup.find("svg", class_="c-stat-body__svg")
            list_aux_2 = [element.replace("%","") for element in sig_strike_source.text.replace("\n"," ").strip().split("\n") if element] if sig_strike_source else []

            if list_aux_2:
                stats = re.findall(r'\d+', list_aux_2[0])
                fighters_data_complete['sig_head_str'].append(float(stats[1]) / 100)
                fighters_data_complete['sig_body_str'].append(float(stats[3]) / 100)
                fighters_data_complete['sig_leg_str'].append(float(stats[5]) / 100)
            else:
                fighters_data_complete['sig_head_str'].append(0.0)
                fighters_data_complete['sig_body_str'].append(0.0)
                fighters_data_complete['sig_leg_str'].append(0.0)

            # Dados biográficos dos lutadores (idade, altura, peso, anos de experiência)
            debut_source = soup.find_all("div", class_="c-bio__field")
            altura = ''
            peso = ''
            idade = ''
            data_estreia = ''
            ano_str_luta = 0

            for element in debut_source:
                text = element.text.replace("\n", " ").strip()
                
                if "Altura" in text:
                    altura = text.split()[-1]
                
                elif "Peso" in text:
                    peso = text.split()[-1]
                
                elif "Idade" in text:
                    idade = text.split()[-1]
                
                elif "Estreia no UFC" in text:
                    data_estreia = text.split()[-1]
                    ano_str_luta = int(data_estreia.split('.')[2]) + 1900 if int(data_estreia.split('.')[2]) > 24 else int(data_estreia.split('.')[2]) + 2000
                
                
            fighters_data_complete['altura_lutador'].append(float(altura) if altura else 0.0)
            fighters_data_complete['peso_lutador'].append(float(peso) if peso else 0.0)
            fighters_data_complete['idade_lutador'].append(int(idade) if idade else 0)


            # Última luta que o lutador participou
            last_fight_source = soup.find("div", class_="c-card-event--athlete-results__date")
            if last_fight_source:
                data_ult_luta = last_fight_source.text.split()[-1]
                ano_ult_luta = int(data_ult_luta.split('.')[2]) + 1900 if int(data_ult_luta.split('.')[2]) > 24 else int(data_ult_luta.split('.')[2]) + 2000
            else:
                ano_ult_luta = 0
            
            if (ano_ult_luta - ano_str_luta) < 0:
                fighters_data_complete['anos_xp'].append(0)
            else:
                fighters_data_complete['anos_xp'].append((ano_ult_luta - ano_str_luta) if (ano_str_luta != 0 and ano_ult_luta != 0) else 0)
                

    df_fighters = pd.DataFrame(fighters_data_complete).drop_duplicates(subset=['nome_lutador'])
    
    
    return df_fighters