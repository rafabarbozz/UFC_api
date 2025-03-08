from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from database.db_config import Base

# Definindo a estrutura da tabela Luta Futura
class LutaFutura(Base):
    __tablename__ = "lutas_futuras"

    id_luta_prox = Column(Integer, primary_key=True, autoincrement=True)
    
    weight_class_prox = Column(String(50), nullable=False, default="Nan")
    fight_date_prox = Column(Date, nullable=False)
    location_prox = Column(String(100), nullable=False, default="Nan")
    event_name_prox = Column(String(100), nullable=False, default="Nan")
    
    red_fighter_prox = Column(Integer, ForeignKey("lutadores.id_lutador"), nullable=False)
    blue_fighter_prox = Column(Integer, ForeignKey("lutadores.id_lutador"), nullable=False)
    
    red_prob_victory = Column(Float, nullable=False, default=-1)
    blue_prob_victory = Column(Float, nullable=False, default=-1)