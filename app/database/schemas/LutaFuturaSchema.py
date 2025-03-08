from pydantic import BaseModel, Field, field_validator
from typing import Optional


class LutaFuturaSchema(BaseModel):
    id_luta_prox: Optional[int] = Field(default=None, description="Primary Key.")

    weight_class_prox: str = Field(default="Nan", description="Weight class of the fight", min_length=3, max_length=50)
    fight_date_prox: str = Field(default="Nan", description="Date of the fight (stored as string)", min_length=3, max_length=30)
    location_prox: str = Field(default="Nan", description="Location of the fight", min_length=3, max_length=100)
    event_name_prox: str = Field(default="Nan", description="Name of the event", min_length=3, max_length=100)

    first_fighter_prox: int = Field(..., description="ID of the first fighter (foreign key to Lutador)")
    second_fighter_prox: int = Field(..., description="ID of the second fighter (foreign key to Lutador)")

    prob_victory_first: float = Field(default=-1, description="Probability of victory for the first fighter")
    prob_victory_second: float = Field(default=-1, description="Probability of victory for the second fighter")

    # Validadores personalizados
    @field_validator("weight_class_prox")
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
            raise ValueError(f"weight_class_prox must be one of {allowed_weight_classes}")
        return value

    @field_validator("prob_victory_first", "prob_victory_second")
    def validate_probabilities(cls, value):
        """Garante que as probabilidades de vitória estejam dentro do intervalo permitido."""
        if value not in [-1] and (value < 0 or value > 1):
            raise ValueError("Probability values must be between 0 and 1, or -1 for unknown values")
        return value

    @field_validator("prob_victory_first")
    def validate_prob_sum(cls, value, values):
        """Garante que a soma das probabilidades não ultrapasse 1 (exceto para valores padrão -1)."""
        if "prob_victory_second" in values and value != -1 and values["prob_victory_second"] != -1:
            if value + values["prob_victory_second"] > 1:
                raise ValueError("Sum of prob_victory_first and prob_victory_second cannot exceed 1")
        return value

    @field_validator("second_fighter_prox")
    def validate_different_fighters(cls, value, values):
        """Garante que os lutadores não sejam o mesmo."""
        if "first_fighter_prox" in values and values["first_fighter_prox"] == value:
            raise ValueError("first_fighter_prox and second_fighter_prox must be different fighters")
        return value