from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Enum as SqlEnum
from dbase import engine
from enum import Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Define User model
class Veterinarios(Base):
    __tablename__ = "veterinarios"
    id_vets = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True)
    sobrenome = Column(String, index=True)
    telefone = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    datacadastro = Column(DateTime, index=True)
    cpf_vet = Column(String, unique=True, index=True)
    datahora_ultacesso = Column(DateTime, index=True)
    cadastrado = Column(Boolean, index=True)
    senhaconfirmada = Column(Boolean, index=True)
    ativo = Column(Boolean, index=True)
    hash_senha = Column(String, unique=True, index=True)
    crmv_num = Column(String, index=True)
    uf_crmv = Column(String, index=True)

class Enderecos(Base):
    __tablename__ = "enderecos"
    id_endereco = Column(Integer, primary_key=True)
    cep = Column(String, index=True)
    logradouro = Column(String, index=True)
    ddd = Column(Integer, index=True)
    numero_telefone = Column(String, index=True)
    bairro = Column(String, index=True)
    cidade = Column(String, index=True)
    uf = Column(String, index=True)
    codibge = Column(String, index=True)

class Tutores(Base):
    __tablename__ = "tutores"

    id_tutores = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    sobrenome = Column(String, index=True)
    telefone = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    datacadastro = Column(Date, index=True)
    cadastroconfirmado = Column(Boolean, index=True)
    cpf_tutor = Column(String, unique=True, index=True)
    enderecoassociado = Column(Integer, ForeignKey('enderecos.id_endereco'))

class Especies(Base):
    __tablename__ = "especies"
    id_especies = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True)
    descricao = Column(String, index=True)
    situacao = Column(String, index=True)

class Racas(Base):
    __tablename__ = "racas"
    id_racas = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True)
    descricao = Column(String, index=True)
    especie_associada = Column(Integer, ForeignKey('especies.id_especies'))
    situacao = Column(String, index=True)

class Animais(Base):
    __tablename__ = "animais"
    id_animais = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey('tutores.id_tutores'))
    nome = Column(String, unique=True, index=True)
    idade_estimada = Column(Integer, index=True)
    sexo = Column(String, index=True)
    cor = Column(String, index=True)
    peso_atual_kg = Column(String, index=True)
    especie = Column(Integer, ForeignKey('especies.id_especies'))
    raca = Column(Integer, ForeignKey('racas.id_racas'))
    situacao = Column(String, index=True)
    id_rfid = Column(Integer, index=True)
    data_rfid_vinculo = Column(Date, index=True)
    vet_rfid_vinculo = Column(Integer, ForeignKey('veterinarios.id_vets'))

class Situacao1(str, Enum):
    agendada = "agendada"
    realizada = "realizada"
    cancelada = "cancelada"
    nao_compareceu = "nao compareceu"

class RegistroConsultas(Base):
    __tablename__ = "registro_consultas"
    id_consulta = Column(Integer, primary_key=True, index=True)
    animal_atendido = Column(Integer, ForeignKey('animais.id_animais'))
    vet_responsavel = Column(Integer, ForeignKey('veterinarios.id_vets'))
    datahora_atendimento = Column(DateTime, index=True)
    motivo = Column(String, index=True)
    anamnese = Column(String, index=True)
    sintomas = Column(String, index=True)
    diagnostico = Column(String, index=True)
    tratamento = Column(String, index=True)
    prescr_medicam = Column(String, index=True)
    peso_kg = Column(String, index=True)
    temperatura = Column(String, index=True)
    obser = Column(String, index=True)
    situacao_atual = Column(SqlEnum(Situacao1), index=True)

class Situacao2(str, Enum):
    agendada = "Agendada"
    aplicada = "Aplicada"
    cancelada = "Cancelada"

class RegistroVacinas(Base):
    __tablename__ = "registro_vacinas"
    id_vacina = Column(Integer, primary_key=True, index=True)
    animal_atendido = Column(Integer, ForeignKey('animais.id_animais'))
    vet_responsavel = Column(Integer, ForeignKey('veterinarios.id_vets'))
    nome_vacina = Column(String, index=True)
    tipo_vacina = Column(String, index=True)
    antirrabica_ind = Column(Boolean, index=True)
    fabricante = Column(String, index=True)
    lote = Column(String, index=True)
    data_vacina = Column(Date, index=True)
    dose_vacina = Column(String, index=True)
    via_aplicacao = Column(String, index=True)
    data_prox_dose = Column(Date, index=True)
    validade_lote = Column(Date, index=True)
    observ = Column(String, index=True)
    situacao = Column(SqlEnum(Situacao2), index=True)

Base.metadata.create_all(bind=engine)