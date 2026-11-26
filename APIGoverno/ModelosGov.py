from sqlalchemy import Column, Integer, String, Date, Boolean, Enum as SqlEnum
from DataBase import engine
from enum import Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Animais(Base):
    __tablename__ = "animais"
    id_animais = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, index=True)
    nome = Column(String, unique=True, index=True)
    idade_estimada = Column(Integer, index=True)
    sexo = Column(String, index=True)
    cor = Column(String, index=True)
    peso_atual_kg = Column(String, index=True)
    especie = Column(Integer, index=True)
    raca = Column(Integer, index=True)
    situacao = Column(String, index=True)
    id_rfid = Column(Integer, index=True)
    data_rfid_vinculo = Column(Date, index=True)
    vet_rfid_vinculo = Column(Integer, index=True)

class Situacao2(str, Enum):
    agendada = "Agendada"
    aplicada = "Aplicada"
    cancelada = "Cancelada"

class RegistroVacinas(Base):
    __tablename__ = "registro_vacinas"
    id_vacina = Column(Integer, primary_key=True, index=True)
    animal_atendido = Column(Integer, index=True)
    vet_responsavel = Column(Integer, index=True)
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