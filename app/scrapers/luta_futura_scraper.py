import requests
import pandas as pd
from datetime import datetime

from bs4 import BeautifulSoup
from unidecode import unidecode

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def get_next_fights_data() -> pd.DataFrame:
    """
    Função para pegar as informações das próximas lutas que irão ocorrer
    """
    
    # Código usado para testar o link 3 vezes e não conseguir conectar vai esperar um tempo e tentar novamente
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    # Pegar o link do próximo evento
    url_events = session.get('https://www.ufc.com.br/events#events-list-upcoming').text
    soup = BeautifulSoup(url_events, "html.parser")
    
    # Link completo para o próximo evento
    link_prox_event = "https://www.ufc.com.br" + soup.find('h3', class_='c-card-event--result__headline').find('a')['href']
        
    # Soup para pegar as informações do primeiro lutador, segundo, categoria, data, local e nome do evento
    soup_event = BeautifulSoup(session.get(link_prox_event).text, "html.parser")
    
    # Fighters name
    names_red_corner_source = soup_event.find_all('div', class_='c-listing-fight__corner-name c-listing-fight__corner-name--red')
    names_red_corner = [unidecode(name.text.replace('\n', ' ').strip().lower()) for name in names_red_corner_source]

    names_blue_corner_source = soup_event.find_all('div', class_='c-listing-fight__corner-name c-listing-fight__corner-name--blue')
    names_blue_corner = [unidecode(name.text.replace('\n', ' ').strip().lower())  for name in names_blue_corner_source]
    
    
    # Weight classes
    weight_class_source = (soup_event.find_all('div', class_='c-listing-fight__class-text'))
    weight_classes = [weight.text.replace('\n', ' ').strip().replace(' Luta', '') for weight in weight_class_source] # Está pegando duplicado pois tem outra tag com a mesma classe, fazer tratamento na hora de criar dataframe
    
    
    # Event date
    event_date = soup_event.find('div', class_='c-hero__headline-suffix tz-change-inner').text.split(' / ')[0].strip()
    
    
    # Event location
    event_location = soup_event.find('div', class_='field field--name-venue field--type-entity-reference field--label-hidden field__item').text.replace('\n', ' ').strip()


    # Event name
    event_name = soup_event.find('div', class_='field field--name-node-title field--type-ds field--label-hidden field__item').text.strip() # Nome do evento
    top_name = soup_event.find('span', class_='e-divider__top').text.strip() # Nome do lutador que fica no topo
    bottom_name = soup_event.find('span', class_='e-divider__bottom').text.strip() # Nome do lutador que fica na parte de baixo
    event_name_complete = event_name + ': ' + top_name + ' vs ' + bottom_name # Nome completo do evento
    
    
    data = {
        'first_fighter_prox': names_red_corner,
        'second_fighter_prox': names_blue_corner,
        'weight_class_prox': weight_classes[::2],
        'fight_date_prox': datetime.strptime(event_date, "%d.%m.%y").date(),
        'location_prox': event_location,
        'event_name_prox': event_name_complete
    }

    df_fights_prox = pd.DataFrame(data)
    

    return df_fights_prox   