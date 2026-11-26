from datetime import date
from pydantic import BaseModel, ConfigDict
from ModelosGov import Situacao2

class AnimaisCreate(BaseModel):
    tutor_id: int
    nome: str
    idade_estimada: int
    sexo: str
    cor: str
    peso_atual_kg: str
    especie: int
    raca: int
    situacao: str
    id_rfid: int
    data_rfid_vinculo: date
    vet_rfid_vinculo: int

class AnimaisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_animais: int
    tutor_id: int
    nome: str
    idade_estimada: int
    sexo: str
    cor: str
    peso_atual_kg: str
    especie: int
    raca: int
    situacao: str
    id_rfid: int
    data_rfid_vinculo: date
    vet_rfid_vinculo: int

class VacinasCreate(BaseModel):
    animal_atendido: int
    vet_responsavel: int
    nome_vacina: str
    tipo_vacina: str
    antirrabica_ind: bool
    fabricante: str
    lote: str
    data_vacina: date
    dose_vacina: str
    via_aplicacao: str
    data_prox_dose: date
    validade_lote: date
    observ: str
    situacao: Situacao2

class VacinasResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_vacina: int
    animal_atendido: int
    vet_responsavel: int
    nome_vacina: str
    tipo_vacina: str
    antirrabica_ind: bool
    fabricante: str
    lote: str
    data_vacina: date
    dose_vacina: str
    via_aplicacao: str
    data_prox_dose: date
    validade_lote: date
    observ: str
    situacao: Situacao2
