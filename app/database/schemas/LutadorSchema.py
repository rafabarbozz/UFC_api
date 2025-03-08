from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from typing import Optional


class LutadorSchema(BaseModel):
    id_lutador: Optional[int] = Field(
        default=None,
        description="Campo inteiro auto-incrementado usado como primary key"
    )
    
    nome_lutador: str = Field(default="Nan", max_length=100)
    apelido: str = Field(default="Nan", max_length=100)
    
    sexo: str = Field(default="Nan", max_length=1)
    categoria: str = Field(default="Nan", max_length=20)
    
    win_lutas: int = Field(default=-1, description="Número de vitórias do lutador")
    lose_lutas: int = Field(default=-1, description="Número de derrotas do lutador")
    draw_lutas: int = Field(default=-1, description="Número de empates do lutador")
    
    precisao_striking: float = Field(default=-1, description="Precisão de golpes do lutador")
    sig_pe_str: float = Field(default=-1, description="Golpes significativos em pé")
    sig_clinch_str: float = Field(default=-1, description="Golpes significativos no clinch")
    sig_solo_str: float = Field(default=-1, description="Golpes significativos no solo")
    
    method_ko_tko: float = Field(default=-1, description="Porcentagem de nocautes")
    method_dec: float = Field(default=-1, description="Porcentagem de vitórias por decisão")
    method_fin: float = Field(default=-1, description="Porcentagem de finalizações")
    
    golpes_sig_conectados: float = Field(default=-1, description="Golpes significativos conectados")
    golpes_sig_absorvidos: float = Field(default=-1, description="Golpes significativos absorvidos")
    
    media_quedas: float = Field(default=-1, description="Média de quedas por luta")
    media_fin: float = Field(default=-1, description="Média de finalizações por luta")
    
    defesa_golpes_sig: float = Field(default=-1, description="Defesa contra golpes significativos")
    defesa_quedas: float = Field(default=-1, description="Defesa contra quedas")
    
    media_knockdowns: float = Field(default=-1, description="Média de knockdowns por luta")
    tempo_medio_luta: int = Field(default=-1, description="Duração média das lutas em segundos")
    
    sig_head_str: float = Field(default=-1, description="Porcentagem de golpes significativos na cabeça")
    sig_body_str: float = Field(default=-1, description="Porcentagem de golpes significativos no corpo")
    sig_leg_str: float = Field(default=-1, description="Porcentagem de golpes significativos na perna")
    
    idade_lutador: int = Field(default=-1, description="Idade do lutador")
    altura_lutador: Decimal = Field(default=Decimal("-1"), description="Altura do lutador em metros")
    peso_lutador: Decimal = Field(default=Decimal("-1"), description="Peso do lutador em kg")
    
    anos_xp: int = Field(default=-1, description="Anos de experiência do lutador")
    
    link_corpo: str = Field(default="Nan", max_length=250)
    link_rosto: str = Field(default="Nan", max_length=250)

    # Custom validators
    @field_validator("sexo")
    def validar_sexo(cls, value):
        """Validates that the sexo value is 'M' or 'F'."""
        if value not in ["M", "F"]:
            raise ValueError("The sexo field must be 'M' (Male) or 'F' (Female)")
        return value

    @field_validator("method_ko_tko", "method_dec", "method_fin")
    def validar_soma_metodos(cls, value, values):
        """Ensures that the sum of victory methods does not exceed 100%."""
        if all(key in values for key in ["method_ko_tko", "method_dec", "method_fin"]):
            soma = values["method_ko_tko"] + values["method_dec"] + values["method_fin"]
            if soma > 1:
                raise ValueError("The sum of method_ko_tko, method_dec and method_fin cannot exceed 100%.")
        return value

    @field_validator("altura_lutador")
    def validar_altura(cls, value):
        """Checks if the fighter's height is within a realistic range."""
        if not (0.0 <= value <= 84.0):
            raise ValueError("The fighter's height must be between 1.40m and 2.30m.")
        return value

    @field_validator("peso_lutador")
    def validar_peso(cls, value):
        """Checks if the fighter's weight is within a realistic range."""
        if not (0.0 <= value <= 290.0):
            raise ValueError("The fighter's weight must be between 45kg and 265kg.")
        return value

    @field_validator("anos_xp")
    def validar_anos_experiencia(cls, value, values):
        """Ensures that the fighter's experience does not exceed what their age permits."""
        if "idade_lutador" in values and value > values["idade_lutador"] - 18:
            raise ValueError("The fighter cannot have more years of experience than their age permits.")
        return value