from sqlalchemy import Column, Integer, String, Float, DECIMAL
from database.db_config import Base

# Definindo a estrutura da tabela Lutador
class Lutador(Base):
    __tablename__ = "lutadores"

    id_lutador = Column(Integer, primary_key=True, autoincrement=True)
    
    nome_lutador = Column(String(100), nullable=False, default="Nan")
    apelido = Column(String(100), nullable=False, default="Nan")
    
    sexo = Column(String(1), nullable=False, default="Nan")
    categoria = Column(String(20), nullable=False, default="Nan")
    
    win = Column(Integer, nullable=False, default=-1)
    lose = Column(Integer, nullable=False, default=-1)
    draw = Column(Integer, nullable=False, default=-1)
    
    precisao_striking = Column(Float, nullable=False, default=-1)
    sig_pe_str = Column(Float, nullable=False, default=-1)
    sig_clinch_str = Column(Float, nullable=False, default=-1)
    sig_solo_str = Column(Float, nullable=False, default=-1)
    
    method_ko_tko = Column(Float, nullable=False, default=-1)
    method_dec = Column(Float, nullable=False, default=-1)
    method_fin = Column(Float, nullable=False, default=-1)
    
    golpes_sig_conectados = Column(Float, nullable=False, default=-1)
    golpes_sig_absorvidos = Column(Float, nullable=False, default=-1)
    
    media_quedas = Column(Float, nullable=False, default=-1)
    media_fin = Column(Float, nullable=False, default=-1)
    
    defesa_golpes_sig = Column(Float, nullable=False, default=-1)
    defesa_quedas = Column(Float, nullable=False, default=-1)
    
    media_knockdowns = Column(Float, nullable=False, default=-1)
    tempo_medio = Column(Integer, nullable=False, default=-1)
    
    sig_head_str = Column(Float, nullable=False, default=-1)
    sig_body_str = Column(Float, nullable=False, default=-1)
    sig_leg_str = Column(Float, nullable=False, default=-1)
    
    idade_lutador = Column(Integer, nullable=False, default=-1)
    altura_lutador = Column(DECIMAL(5, 2), nullable=False, default=-1)
    peso_lutador = Column(DECIMAL(5, 2), nullable=False, default=-1)
    
    anos_xp = Column(Integer, nullable=False, default=-1)
    
    link_corpo = Column(String(250), nullable=False, default="Nan")
    link_rosto = Column(String(250), nullable=False, default="Nan")