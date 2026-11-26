from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
from modelos import Situacao1, Situacao2
from validacao import validar_e_limpar_cpf

# Pydantic schema for data validation
class VeterinariosCreate(BaseModel):
    nome: str
    sobrenome: str
    telefone: str
    email: str
    datacadastro: datetime
    cpf_vet: str
    datahora_ultacesso: datetime
    cadastrado: bool
    senhaconfirmada: bool
    hash_senha: str
    crmv_num: str
    uf_crmv: str

    @field_validator("cpf_vet")
    @classmethod
    def validar_cpf_vet(cls, v: str) -> str:
        return validar_e_limpar_cpf(v)

class VeterinariosResponse(BaseModel):
    id_vets: int
    sobrenome: str
    telefone: str
    email: str
    datacadastro: datetime
    cpf_vet: str
    datahora_ultacesso: datetime
    cadastrado: bool
    senhaconfirmada: bool
    crmv_num: str
    uf_crmv: str

    class ConfigDict:
        orm_mode = True

class MicrochipUpdate(BaseModel):
    id_rfid: Optional[int] = Field(default=None, gt=0, description="Código numérico positivo do RFID")
    data_rfid_vinculo: Optional[date] = None
    vet_rfid_vinculo: Optional[int] = Field(default=None, gt=0, description="ID do veterinário responsável")

    @field_validator("data_rfid_vinculo")
    @classmethod
    def validar_data_vinculo(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("A data de vínculo do microchip não pode ser futura.")
        return v

class MicrochipResponse(BaseModel):
    id_animais: int
    id_rfid: Optional[int] = None
    data_rfid_vinculo: Optional[date] = None
    vet_rfid_vinculo: Optional[int] = None

    class ConfigDict:
        orm_mode = True


class TutoresCreate(BaseModel):
    nome: str
    sobrenome: str
    telefone: str
    email: str
    datacadastro: date
    cadastroconfirmado: bool
    cpf_tutor: str
    cep: Optional[str] = Field(default=None, description="CEP do tutor para validação via ViaCEP")
    numero_telefone: Optional[str] = None
    enderecoassociado: Optional[int] = None

    @field_validator("cpf_tutor")
    @classmethod
    def validar_cpf_tutor(cls, v: str) -> str:
        return validar_e_limpar_cpf(v)
    
class TutoresResponse(BaseModel):
    id_tutores: int
    nome:str
    sobrenome: str
    telefone: str
    email: str
    datacadastro: date
    cadastroconfirmado: bool
    cpf_tutor: str
    enderecoassociado: int

    class ConfigDict:
        orm_mode = True


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
    class ConfigDict:
        orm_mode = True

class ConsultasCreate(BaseModel):
    animal_atendido: int
    vet_responsavel: int
    datahora_atendimento: datetime
    motivo: str
    anamnese: str
    sintomas: str
    diagnostico: str
    tratamento: str
    prescr_medicam: str
    peso_kg: str
    temperatura: str
    obser: str
    situacao_atual: Situacao1
    
class ConsultasResponse(BaseModel):
    id_consulta: int
    animal_atendido: int
    vet_responsavel: int
    datahora_atendimento: datetime
    motivo: str
    anamnese: str
    sintomas: str
    diagnostico: str
    tratamento: str
    prescr_medicam: str
    peso_kg: str
    temperatura: str
    obser: str
    situacao_atual: Situacao1
    
    class ConfigDict:
        orm_mode = True

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

    class ConfigDict:
        orm_mode = True

class VeterinarioRegistroRequest(BaseModel):
    nome: str
    sobrenome: str
    telefone: str
    email: EmailStr
    cpf_vet: str
    crmv_num: str
    uf_crmv: str

    @field_validator("cpf_vet")
    @classmethod
    def validar_cpf_registro(cls, v: str) -> str:
        return validar_e_limpar_cpf(v)


class VeterinarioConfirmarSenhaRequest(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=8, description="Senha do veterinário (mínimo 8 caracteres)")
    confirmar_senha: str = Field(min_length=8)


class VeterinarioRegistroResponse(BaseModel):
    id_vets: int
    nome: str
    sobrenome: str
    email: str
    cadastrado: bool
    senhaconfirmada: bool
    ativo: bool
    mensagem: str