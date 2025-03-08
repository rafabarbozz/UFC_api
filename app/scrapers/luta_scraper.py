import time
import requests
import pandas as pd
from datetime import datetime

from bs4 import BeautifulSoup
from tqdm import tqdm
from unidecode import unidecode

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def get_link_events():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("disable-notifications")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.ufc.com.br/events#events-list-past")

    # Tratar a mensagem de cookies, após a rolagem 
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#onetrust-close-btn-container > button"))
        )
        cookie_button.click()
    except:
        pass  # Lidar com a exceção se o botão de cookies não for encontrado ou não estiver visível

    clicks = 0  
    qtd_elementos_ant = 0
    
    while True:
        try:
            # Tamanho do scroll
            time.sleep(4)  
            driver.execute_script(f"window.scrollTo(0, window.scrollY + 7);")

            # Esperar até que o botão de pesquisa seja visível
            more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/main/div[1]/div/div/div/div/div/div/div/div/div[5]/div/div/details[2]/div/div/ul/li/a"))
            )
            
            more_button.click()
            clicks += 1
            print(f"{clicks} clicks no botão 'Carregue Mais'")

            # Contar a quantidade de elementos carregados
            qtd_elementos_atual = driver.find_elements(By.CSS_SELECTOR, "div.l-listing__item.views-row")
            
            if len(qtd_elementos_atual) == qtd_elementos_ant:
                break
            
            qtd_elementos_ant = len(qtd_elementos_atual)
            
        except Exception as e:
            print("Não há mais páginas para carregar: ", e)
            break
        
    url_Fighters = driver.page_source
    soup = BeautifulSoup(url_Fighters, 'html.parser').find("details", id="events-list-past")
    source_link_events = soup.find_all("h3", "c-card-event--result__headline")
    
    link_events = [] 
    for link in tqdm(source_link_events):
        link_events.append("https://www.ufc.com.br" + link.find("a", href=True).get('href'))


    events_IDs = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        
        if href.startswith("/event/") and "#" in href:
            id = href.split("#")[1]
            events_IDs.append(id)
    
    driver.quit()

    return link_events, events_IDs


def get_fights_data(link_events, events_IDs) -> pd.DataFrame:
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    
    columns = ['label',
               
               'red_name', 'red_link', 'red_total_str', 'red_takedowns', 'red_sub_att', 'red_reversals', 'red_sig_str', 
               'red_knockdowns', 'red_head_sig_str', 'red_body_sig_str', 'red_leg_sig_str', 'red_distance_sig_str', 'red_clinch_sig_str', 'red_ground_sig_str',
               
               'blue_name', 'blue_link', 'blue_total_str', 'blue_takedowns', 'blue_sub_att', 'blue_reversals', 'blue_sig_str', 
               'blue_knockdowns', 'blue_head_sig_str', 'blue_body_sig_str', 'blue_leg_sig_str', 'blue_distance_sig_str', 'blue_clinch_sig_str', 'blue_ground_sig_str',
               
               'fin_method', 'fight_time', 'rounds', 'weight_class', 'event_name', 'fight_date', 'title_bout'
               ]

    fights_data_complete = {col: [] for col in columns} 
    
    for i, link in tqdm(enumerate(link_events)):   
        fighter_source = session.get(link).text
        soup = BeautifulSoup(fighter_source, "html.parser")
        
        # Resultado da luta
        result_red_source = soup.find_all("div", class_="c-listing-fight__corner-body--red")
        for result in result_red_source:
            fights_data_complete['label'].append(0 if "Win" in result.text.strip() else 1)
               
                    
        # Nome do evento
        title = soup.find("div", class_="field field--name-node-title field--type-ds field--label-hidden field__item").text.strip() if soup.find("div", class_="field field--name-node-title field--type-ds field--label-hidden field__item") else None
        top_name = soup.find("span", class_="e-divider__top").text.strip() if soup.find("span", class_="e-divider__top") else None
        bot_name = soup.find("span", class_="e-divider__bottom").text.strip() if soup.find("span", class_="e-divider__bottom") else None
        if title:
            event_name = title
        if top_name and bot_name:
            event_name += f": {top_name} vs {bot_name}"
                
        # Data do evento
        fight_date_source = soup.find("div", class_="c-hero__headline-suffix tz-change-inner").text.strip().split(" / ")[0]
        fight_date = datetime.strptime(fight_date_source, "%d.%m.%y").date()
        
        
        # Nome dos lutadores
        red_names_source = soup.find_all("div", class_="c-listing-fight__corner-name c-listing-fight__corner-name--red")
        for name in red_names_source:
            red_name = unidecode(name.text.strip().replace("\n", " ").lower())
            fights_data_complete["red_name"].append(red_name)

        blue_names_source = soup.find_all("div", class_="c-listing-fight__corner-name c-listing-fight__corner-name--blue")
        for name in blue_names_source:
            blue_name = unidecode(name.text.strip().replace("\n", " ").lower())
            fights_data_complete["blue_name"].append(blue_name)
            
            
        # Links dos lutadores
        red_fighter_link = soup.find_all("div", class_="c-listing-fight__corner-image--red")
        for link in red_fighter_link:
            red_fighter_link = link.find("a", href=True).get('href')
            fights_data_complete["red_link"].append(red_fighter_link)
        
        blue_fighter_link = soup.find_all("div", class_="c-listing-fight__corner-image--blue")
        for link in blue_fighter_link:
            blue_fighter_link = link.find("a", href=True).get('href')
            fights_data_complete["blue_link"].append(blue_fighter_link)                    
               
                    
        # Categoria de peso
        weight_class_source = soup.find_all("div", class_="details-content__class")
        for weight in weight_class_source:
            weight_class = weight.text.strip()
            if not weight_class:
                weight_class = "Nan"
                
            fights_data_complete["title_bout"].append(1 if "disputa" in weight_class.lower() or "title bout" in weight_class.lower() else 0)
            
            if "disputa" in weight_class.lower():
                weight_class = weight_class.replace(" Disputa de Cinturão", "")
            if "bout" in weight_class.lower():
                weight_class = weight_class.replace(" Interim Title Bout", "")
                
            fights_data_complete["weight_class"].append(weight_class)

        
        # Ids de cada luta para posterior consulta a API
        ids_fights = []
        ids_fights_source = (soup.find_all("div", class_="c-listing-fight"))
        for id in ids_fights_source:
            ids_fights.append(id.get("data-fmid"))
        
        
        for j in range(len(ids_fights)):
            url = f"https://www.ufc.com.br/matchup/{events_IDs[i]}/{ids_fights[j]}/post"

            info_fight_source = session.get(url)    

            # Soup da luta específica
            soup_fight = BeautifulSoup(info_fight_source.text, "html.parser").find("main", class_="l-page__main")
                        
                        
            # Quantidade de rounds
            rounds = soup_fight.find("h4", class_="e-t5 round")
            if rounds and rounds.text.strip() != '':
                rounds = int(rounds.text.strip())
            else:
                rounds = 0
                
                
            # Tempo de luta
            time_source = soup_fight.find("h4", class_="e-t5 time")
            if time_source and time_source.text.strip() != '':
                if ":" in time_source.text.strip():
                    time = time_source.text.strip().split(":")
                    if time[0]:
                        fight_time = (rounds - 1) * 60 + int(time[0]) * 60 + int(time[1])
                    else:
                        fight_time = (rounds - 1) * 60 + int(time[1])
                else:
                    fight_time = (rounds - 1) * 60 + int(time[0]) * 60
            else:
                fight_time = 0            
            
            
            # Método de finalização
            fin_method = soup_fight.find("h4", class_="e-t5 method")
            fin_method = fin_method.text.strip() if fin_method else "Nan"
              
                    
            # Total strikes
            total_strikes = soup_fight.find("div", class_="c-stat-metric-compare total_strikes")
            if total_strikes:
                red_total_strikes_percent = total_strikes.find("span", class_="red").find("span", class_="c-stat-metric-compare__percent percent").text.strip()
                red_total_str = float(red_total_strikes_percent.replace("(", "").replace(")", "").replace("%", "")) / 100 if red_total_strikes_percent else 0.0
                
                blue_total_strikes_percent = total_strikes.find("span", class_="blue").find("span", class_="c-stat-metric-compare__percent_2 percent").text.strip()
                blue_total_str = float(blue_total_strikes_percent.replace("(", "").replace(")", "").replace("%", "")) / 100 if blue_total_strikes_percent else 0.0
            
            else:
                red_total_str = 0.0
                blue_total_str = 0.0
                
                
            # Quedas
            takedowns = soup_fight.find("div", class_="c-stat-metric-compare takedowns")
            if takedowns:
                red_takedowns_percent = takedowns.find("span", class_="red").find("span", class_="c-stat-metric-compare__percent percent").text.strip()
                red_takedowns = float(red_takedowns_percent.replace("(", "").replace(")", "").replace("%", "")) / 100 if red_takedowns_percent else 0.0
                
                blue_takedowns_percent = takedowns.find("span", class_="blue").find("span", class_="c-stat-metric-compare__percent_2 percent").text.strip()
                blue_takedowns = float(blue_takedowns_percent.replace("(", "").replace(")", "").replace("%", "")) / 100 if blue_takedowns_percent else 0.0
            else:
                red_takedowns = 0.0
                blue_takedowns = 0.0

            
            # Tentativas de finalização
            submission_attempts = soup_fight.find("div", class_="c-stat-metric-compare sub_attempts")
            red_sub_attempts = int(submission_attempts.find("span", class_="red").find("span", class_="c-stat-metric-compare__value c-stat-metric-compare__number").text.strip()) if submission_attempts else 0
            blue_sub_attempts = int(submission_attempts.find("span", class_="blue").find("span", class_="c-stat-metric-compare__value_2 c-stat-metric-compare__number").text.strip()) if submission_attempts else 0
            
            
            # Raspagens
            reversals = soup_fight.find("div", class_="c-stat-metric-compare rev")
            red_reversals = int(reversals.find("span", class_="red").find("span", class_="c-stat-metric-compare__value c-stat-metric-compare__number").text.strip()) if reversals else 0
            blue_reversals = int(reversals.find("span", class_="blue").find("span", class_="c-stat-metric-compare__value_2 c-stat-metric-compare__number").text.strip()) if reversals else 0
            
            
            # Golpes significativos
            sig_str = soup_fight.find("div", class_="c-stat-metric-compare sig_strikes")
            red_sig_str = int(sig_str.find("span", class_="red").find("span", class_="c-stat-metric-compare__value c-stat-metric-compare__number").text.strip()) if sig_str else 0
            blue_sig_str = int(sig_str.find("span", class_="blue").find("span", class_="c-stat-metric-compare__value_2 c-stat-metric-compare__number").text.strip()) if sig_str else 0


            # Knockdowns
            knockdowns = soup_fight.find("div", class_="c-stat-metric-compare knockdowns")     
            red_knockdowns = int(knockdowns.find("span", class_="red").find("span", class_="c-stat-metric-compare__value c-stat-metric-compare__number").text.strip()) if knockdowns else 0
            blue_knockdowns = int(knockdowns.find("span", class_="blue").find("span", class_="c-stat-metric-compare__value_2 c-stat-metric-compare__number").text.strip()) if knockdowns else 0
            
            
            # Golpes significativos na Cabeça
            head_sig_str = soup_fight.find_all("text", id="e-stat-body_x5F__x5F_head_value")
            if head_sig_str:
                red_head_sig_str = float(head_sig_str[0].text.strip().replace("%", "")) / 100
                blue_head_sig_str = float(head_sig_str[1].text.strip().replace("%", "")) / 100
            else:
                red_head_sig_str = 0.0
                blue_head_sig_str = 0.0


            # Golpes significativos no Corpo
            body_sig_str = soup_fight.find_all("text", id="e-stat-body_x5F__x5F_body_percent")
            if body_sig_str:
                red_body_sig_str = float(body_sig_str[0].text.strip().replace("%", "")) / 100
                blue_body_sig_str = float(body_sig_str[1].text.strip().replace("%", "")) / 100
            else:
                red_body_sig_str = 0.0
                blue_body_sig_str = 0.0
                
                
            # Golpes significativos nas Pernas
            leg_sig_str = soup_fight.find_all("text", id="e-stat-body_x5F__x5F_leg_percent")
            if leg_sig_str:
                red_leg_sig_str = float(leg_sig_str[0].text.strip().replace("%", "")) / 100
                blue_leg_sig_str = float(leg_sig_str[1].text.strip().replace("%", "")) / 100
            else: 
                red_leg_sig_str = 0.0
                blue_leg_sig_str = 0.0
                
            
            # Golpes significativos na Distância
            distance_sig_str = soup_fight.find("div", class_="c-stat-metric-compare distance")
            if distance_sig_str:
                red_distance_percent = distance_sig_str.find("span", class_="red").find("span", class_="c-stat-metric-compare__percent percent").text.strip()
                red_distance_sig_str = float(red_distance_percent.replace("(", "").replace(")", "").replace("%", "")) / 100 if red_distance_percent else 0.0
                
                blue_distance_percent = distance_sig_str.find("span", class_="blue").find("span", class_="c-stat-metric-compare__percent_2 percent").text.strip()
                blue_distance_sig_str = float(blue_distance_percent.replace("(", "").replace(")", "").replace("%", "")) / 100 if blue_distance_percent else 0.0
            else:
                red_distance_sig_str = 0.0
                blue_distance_sig_str = 0.0
                
            
            # Golpes significativos no Clinche
            clinch_sig_str = soup_fight.find("div", class_="c-stat-metric-compare clinch")
            if clinch_sig_str:
                red_clinch_percent = clinch_sig_str.find("span", class_="red").find("span", class_="c-stat-metric-compare__percent percent").text.strip()
                red_clinch_sig_str = float(red_clinch_percent.replace("(", "").replace(")", "").replace("%", "")) / 100 if red_clinch_percent else 0.0
                
                blue_clinch_percent = clinch_sig_str.find("span", class_="blue").find("span", class_="c-stat-metric-compare__percent_2 percent").text.strip()
                blue_clinch_sig_str = float(blue_clinch_percent.replace("(", "").replace(")", "").replace("%", "")) / 100 if blue_clinch_percent else 0.0
            
            else:
                red_clinch_sig_str = 0.0
                blue_clinch_sig_str = 0.0
                
 
            # Golpes significativos no Solo
            ground_sig_str = soup_fight.find("div", class_="c-stat-metric-compare ground")   
            if ground_sig_str:
                red_ground_percent = ground_sig_str.find("span", class_="red").find("span", class_="c-stat-metric-compare__percent percent").text.strip()
                red_ground_sig_str = float(red_ground_percent.replace("(", "").replace(")", "").replace("%", "")) / 100 if red_ground_percent else 0.0
                
                blue_ground_percent = ground_sig_str.find("span", class_="blue").find("span", class_="c-stat-metric-compare__percent_2 percent").text.strip()
                blue_ground_sig_str = float(blue_ground_percent.replace("(", "").replace(")", "").replace("%", "")) / 100 if blue_ground_percent else 0.0
                
            else:
                red_ground_sig_str = 0.0
                blue_ground_sig_str = 0.0

            
            fights_data_complete["red_total_str"].append(red_total_str)
            fights_data_complete["red_takedowns"].append(red_takedowns)
            fights_data_complete["red_sub_att"].append(red_sub_attempts)
            fights_data_complete["red_reversals"].append(red_reversals)
            fights_data_complete["red_sig_str"].append(red_sig_str)
            fights_data_complete["red_knockdowns"].append(red_knockdowns)
            fights_data_complete["red_head_sig_str"].append(red_head_sig_str)
            fights_data_complete["red_body_sig_str"].append(red_body_sig_str)
            fights_data_complete["red_leg_sig_str"].append(red_leg_sig_str)
            fights_data_complete["red_distance_sig_str"].append(red_distance_sig_str)
            fights_data_complete["red_clinch_sig_str"].append(red_clinch_sig_str)
            fights_data_complete["red_ground_sig_str"].append(red_ground_sig_str)
            
            fights_data_complete["blue_total_str"].append(blue_total_str)
            fights_data_complete["blue_takedowns"].append(blue_takedowns)
            fights_data_complete["blue_sub_att"].append(blue_sub_attempts)
            fights_data_complete["blue_reversals"].append(blue_reversals)
            fights_data_complete["blue_sig_str"].append(blue_sig_str)
            fights_data_complete["blue_knockdowns"].append(blue_knockdowns)
            fights_data_complete["blue_head_sig_str"].append(blue_head_sig_str)
            fights_data_complete["blue_body_sig_str"].append(blue_body_sig_str)
            fights_data_complete["blue_leg_sig_str"].append(blue_leg_sig_str)
            fights_data_complete["blue_distance_sig_str"].append(blue_distance_sig_str)
            fights_data_complete["blue_clinch_sig_str"].append(blue_clinch_sig_str)
            fights_data_complete["blue_ground_sig_str"].append(blue_ground_sig_str)
            
            fights_data_complete['fight_time'].append(fight_time)
            fights_data_complete['rounds'].append(rounds)
            fights_data_complete['fin_method'].append(fin_method)
            fights_data_complete["event_name"].append(event_name)
            fights_data_complete["fight_date"].append(fight_date)
            
        
    fights_df = pd.DataFrame(fights_data_complete)
    
    return fights_df  


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