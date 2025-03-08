from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from database.db_config import Base

# Definindo a estrutura da tabela Luta
class Luta(Base):
    __tablename__ = "lutas"

    id_luta = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(Integer, nullable=False, default=-1)
    
    red_id = Column(Integer, ForeignKey("lutadores.id_lutador"), nullable=False)
    red_link = Column(String(250), nullable=False, default="Nan")
    red_total_str = Column(Float, nullable=False, default=-1)
    red_takedowns = Column(Float, nullable=False, default=-1)
    red_sub_att = Column(Integer, nullable=False, default=-1)
    red_reversals = Column(Integer, nullable=False, default=-1)
    red_sig_str = Column(Integer, nullable=False, default=-1)
    red_knockdowns = Column(Integer, nullable=False, default=-1)
    red_head_sig_str = Column(Float, nullable=False, default=-1)
    red_body_sig_str = Column(Float, nullable=False, default=-1)
    red_leg_sig_str = Column(Float, nullable=False, default=-1)
    red_distance_sig_str = Column(Float, nullable=False, default=-1)
    red_clinch_sig_str = Column(Float, nullable=False, default=-1)
    red_ground_sig_str = Column(Float, nullable=False, default=-1)
    
    blue_id = Column(Integer, ForeignKey("lutadores.id_lutador"), nullable=False)
    blue_link = Column(String(250), nullable=False, default="Nan")
    blue_total_str = Column(Float, nullable=False, default=-1)
    blue_takedowns = Column(Float, nullable=False, default=-1)
    blue_sub_att = Column(Integer, nullable=False, default=-1)
    blue_reversals = Column(Integer, nullable=False, default=-1)
    blue_sig_str = Column(Integer, nullable=False, default=-1)
    blue_knockdowns = Column(Integer, nullable=False, default=-1)
    blue_head_sig_str = Column(Float, nullable=False, default=-1)
    blue_body_sig_str = Column(Float, nullable=False, default=-1)
    blue_leg_sig_str = Column(Float, nullable=False, default=-1)
    blue_distance_sig_str = Column(Float, nullable=False, default=-1)
    blue_clinch_sig_str = Column(Float, nullable=False, default=-1)
    blue_ground_sig_str = Column(Float, nullable=False, default=-1)
    
    fin_method = Column(String(50), nullable=False, default="Nan")
    fight_time = Column(Integer, nullable=False, default=-1)
    rounds = Column(Integer, nullable=False, default=-1)
    weight_class = Column(String(50), nullable=False, default="Nan")
    event_name = Column(String(100), nullable=False, default="Nan")
    fight_date = Column(Date, nullable=False)
    title_bout = Column(Integer, nullable=False, default=0)
