from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date


class LutaSchema(BaseModel):
    id_luta: Optional[int] = Field(default=None, description="Primary Key.")

    label: int = Field(default=-1, description="Label of the fight")

    red_id: int = Field(..., description="ID of the red corner fighter")
    red_link: str = Field(default="Nan", description="Link of the red corner fighter", min_length=3, max_length=250)
    red_total_str: float = Field(default=-1, description="Total strikes of the red corner fighter")
    red_takedowns: float = Field(default=-1, description="Takedowns of the red corner fighter")
    red_sub_att: int = Field(default=-1, description="Submission attempts of the red corner fighter")
    red_reversals: int = Field(default=-1, description="Reversals of the red corner fighter")
    red_sig_str: int = Field(default=-1, description="Significant strikes of the red corner fighter")
    red_knockdowns: int = Field(default=-1, description="Knockdowns of the red corner fighter")
    red_head_sig_str: float = Field(default=-1, description="Head significant strikes of the red corner fighter")
    red_body_sig_str: float = Field(default=-1, description="Body significant strikes of the red corner fighter")
    red_leg_sig_str: float = Field(default=-1, description="Leg significant strikes of the red corner fighter")
    red_distance_sig_str: float = Field(default=-1, description="Distance strikes of the red corner fighter")
    red_clinch_sig_str: float = Field(default=-1, description="Clinch strikes of the red corner fighter")
    red_ground_sig_str: float = Field(default=-1, description="Ground strikes of the red corner fighter")

    blue_id: int = Field(..., description="ID of the blue corner fighter")
    blue_link: str = Field(default="Nan", description="Link of the blue corner fighter", min_length=3, max_length=250)
    blue_total_str: float = Field(default=-1, description="Total strikes of the blue corner fighter")
    blue_takedowns: float = Field(default=-1, description="Takedowns of the blue corner fighter")
    blue_sub_att: int = Field(default=-1, description="Submission attempts of the blue corner fighter")
    blue_reversals: int = Field(default=-1, description="Reversals of the blue corner fighter")
    blue_sig_str: int = Field(default=-1, description="Significant strikes of the blue corner fighter")
    blue_knockdowns: int = Field(default=-1, description="Knockdowns of the blue corner fighter")
    blue_head_sig_str: float = Field(default=-1, description="Head significant strikes of the blue corner fighter")
    blue_body_sig_str: float = Field(default=-1, description="Body significant strikes of the blue corner fighter")
    blue_leg_sig_str: float = Field(default=-1, description="Leg significant strikes of the blue corner fighter")
    blue_distance_sig_str: float = Field(default=-1, description="Distance strikes of the blue corner fighter")
    blue_clinch_sig_str: float = Field(default=-1, description="Clinch strikes of the blue corner fighter")
    blue_ground_sig_str: float = Field(default=-1, description="Ground strikes of the blue corner fighter")

    fin_method: str = Field(default="Nan", description="Method of finish of the fight", min_length=3, max_length=50)
    fight_time: int = Field(default=-1, description="Duration of the fight in seconds")
    rounds: int = Field(default=-1, description="Number of rounds in the fight")
    weight_class: str = Field(default="Nan", description="Weight class of the fight", min_length=3, max_length=50)
    event_name: str = Field(default="Nan", description="Name of the event", min_length=3, max_length=100)
    fight_date: date = Field(..., description="Date of the fight")
    title_bout: int = Field(default=0, description="If the fight is a title bout (0 for No, 1 for Yes)")
    

    # Validadores personalizados
    @field_validator("fight_date")
    def validate_fight_date(cls, value):
        """Garante que a data da luta não seja no futuro."""
        if value > date.today():
            raise ValueError("fight_date cannot be in the future")
        return value

    @field_validator("fin_method")
    def validate_fin_method(cls, value):
        """Garante que o método de finalização seja válido."""
        allowed_methods = [
            "KO/TKO",
            "Decision - Unanimous",
            "Decision - Split",
            "Decision - Majority",
            "Submission",
            "TKO - Doctor's Stoppage",
            "Could Not Continue",
            "DQ",
            "DEC"
        ]
        if value not in allowed_methods:
            raise ValueError(f"fin_method must be one of {allowed_methods}")
        return value

    @field_validator("weight_class")
    def validate_weight_class(cls, value):
        """Verifica se a categoria de peso informada é válida."""
        allowed_weight_classes = [
            "Peso-palha feminino",
            "Peso-mosca",
            "Peso-mosca feminino",
            "Peso-galo",
            "Peso-galo feminino",
            "Peso-pena",
            "Peso-leve",
            "Peso Meio-Médio",
            "Peso-médio",
            "Peso-meio-pesado",
            "Peso-pesado",
            "Catchweight",
        ]
        if value not in allowed_weight_classes:
            raise ValueError(f"weight_class must be one of {allowed_weight_classes}")
        return value

    @field_validator("rounds")
    def validate_rounds(cls, value):
        """Garante que o número de rounds esteja dentro do limite padrão."""
        if value > 5:
            raise ValueError("rounds cannot be greater than 5")
        return value

    @field_validator("fight_time")
    def validate_fight_time(cls, value, values):
        """Valida o tempo total da luta em relação ao número de rounds."""
        max_fight_time = 300 * values.get("rounds", 5)  # Cada round dura no máximo 300s (5 min)
        if value > max_fight_time:
            raise ValueError(f"fight_time cannot exceed {max_fight_time} seconds for {values.get('rounds', 5)} rounds")
        return value

    @field_validator("blue_id")
    def validate_different_fighters(cls, value, values):
        """Garante que os lutadores vermelhos e azuis não sejam o mesmo."""
        if "red_id" in values and values["red_id"] == value:
            raise ValueError("red_id and blue_id must be different fighters")
        return value