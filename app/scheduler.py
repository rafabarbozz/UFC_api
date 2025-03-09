from apscheduler.schedulers.background import BackgroundScheduler

from scrapers.lutador_scraper import get_fighters_data
from scrapers.luta_scraper import get_link_events, get_fights_data
from scrapers.luta_futura_scraper import get_next_fights_data

from database.db_config import get_db
from database.models.Lutador import Lutador
from database.models.Luta import Luta
from database.models.LutaFutura import LutaFutura

from asyncio import run

import pandas as pd

from update_database.update_luta import update_fights
from update_database.update_lutador import update_fighters
from update_database.update_luta_futura import update_next_fights


# Funções para executar os scrapers e salvar no banco de dados
async def atualizar_lutas_e_lutadores():
    try:
        # Obter links e ids
        links, ids = get_link_events()
        if not links or not ids:
            print("Erro: links ou ids estão vazios.")
            return

        df_lutas = get_fights_data(links, ids)
        if df_lutas is None or df_lutas.empty:
            print("Erro: Dados de lutas não encontrados ou vazios.")
            return

        links_lutadores = pd.concat([df_lutas['red_link'], df_lutas['blue_link']]).drop_duplicates().tolist()
        if not links_lutadores:
            print("Erro: Links de lutadores não encontrados.")
            return

        df_lutadores = get_fighters_data(links_lutadores)
        if df_lutadores is None or df_lutadores.empty:
            print("Erro: Dados de lutadores não encontrados ou vazios.")
            return

        update_fighters(df_lutadores)
        update_fights(df_lutas)
        
    except Exception as e:
        print(f"Exceção ocorreu em executar_e_salvar_luta_e_lutador: {e}")


async def atualizar_proximas_lutas():
    try:
        luta_futura_data = get_next_fights_data()
        if luta_futura_data is None or (hasattr(luta_futura_data, 'empty') and luta_futura_data.empty):
            print("Erro: Dados de lutas futuras não encontrados ou vazios.")
            return

        update_next_fights(luta_futura_data)
    except Exception as e:
        print(f"Exceção ocorreu em executar_e_salvar_luta_futura: {e}")



# Configuração do agendador
#scheduler = BackgroundScheduler()

# Agendamento das tarefas
#scheduler.add_job(lambda: run(atualizar_lutas_e_lutadores()), 'cron', day_of_week='thu', hour=21)
#scheduler.add_job(lambda: run(atualizar_proximas_lutas()), 'cron', day_of_week='thu', hour=21)

# Inicialização do agendador
#scheduler.start()

# Manter o script em execução (opcional)
#try:
#    # Mantenha o script em execução para que o agendador continue funcionando
#    while True:
#        pass
#except (KeyboardInterrupt, SystemExit):
##    # Desligar o agendador de forma limpa
#    scheduler.shutdown()


