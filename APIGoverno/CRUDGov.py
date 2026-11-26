from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from DataBase import SessionLocal
from ModelosGov import RegistroVacinas, Animais, Situacao2
from SchemasGov import AnimaisCreate, VacinasCreate
from datetime import date

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD - ANIMAIS

def criar_animal(db: Session, animal: AnimaisCreate) -> Animais:
    db_animal = Animais(**animal.model_dump())
    db.add(db_animal)
    try:
        db.commit()
        db.refresh(db_animal)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro de integridade ao cadastrar animal (verifique se o nome já existe ou se as chaves estrangeiras são válidas).")
    return db_animal


def obter_animal(db: Session, id_rfid: int) -> Animais:
    animal = db.query(Animais).filter(Animais.id_rfid == id_rfid).first()
    if not animal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Animal com id {id_rfid} não encontrado.")
    return animal


def listar_animais(db: Session, skip: int = 0, limit: int = 100, tutor_id: int | None = None, situacao: str | None = None) -> list[Animais]:
    query = db.query(Animais)
    if tutor_id is not None:
        query = query.filter(Animais.tutor_id == tutor_id)
    if situacao is not None:
        query = query.filter(Animais.situacao == situacao)
    return query.offset(skip).limit(limit).all()


def atualizar_animal(db: Session, id_rfid: int, dados_atualizacao: AnimaisCreate) -> Animais:
    animal = obter_animal(db, id_rfid)
    for campo, valor in dados_atualizacao.model_dump().items():
        setattr(animal, campo, valor)
    try:
        db.commit()
        db.refresh(animal)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro de integridade ao atualizar animal (verifique duplicidade de nome ou chaves estrangeiras).")
    return animal


def deletar_animal(db: Session, id_rfid: int) -> dict:
    animal = obter_animal(db, id_rfid)
    try:
        db.delete(animal)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é possível excluir o animal pois existem registros vinculados (como vacinas).")
    return {"mensagem": f"Animal {id_rfid} removido com sucesso."}

# CRUD - REGISTRO DE VACINAS

def _validar_situacao_vacina(situacao: str) -> Situacao2:
    try:
        return Situacao2(situacao)
    except ValueError:
        valores_validos = [item.value for item in Situacao2]
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Situação inválida '{situacao}'. Valores permitidos: {valores_validos}.")


def criar_registro_vacina(db: Session, vacina: VacinasCreate) -> RegistroVacinas:
    dados = vacina.model_dump()
    dados["situacao"] = _validar_situacao_vacina(dados["situacao"])
    db_vacina = RegistroVacinas(**dados)
    db.add(db_vacina)
    try:
        db.commit()
        db.refresh(db_vacina)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro de integridade ao registrar vacina (verifique animal_atendido e vet_responsavel).")
    return db_vacina


def obter_registro_vacina(db: Session, id_vacina: int) -> RegistroVacinas:
    vacina = db.query(RegistroVacinas).filter(RegistroVacinas.id_vacina == id_vacina).first()
    if not vacina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Registro de vacina com id {id_vacina} não encontrado.")
    return vacina


def listar_registros_vacinas(db: Session, skip: int = 0, limit: int = 100,  animal_atendido: int | None = None, vet_responsavel: int | None = None,situacao: str | None = None) -> list[RegistroVacinas]:
    query = db.query(RegistroVacinas)
    if animal_atendido is not None:
        query = query.filter(RegistroVacinas.animal_atendido == animal_atendido)
    if vet_responsavel is not None:
        query = query.filter(RegistroVacinas.vet_responsavel == vet_responsavel)
    if situacao is not None:
        enum_situacao = _validar_situacao_vacina(situacao)
        query = query.filter(RegistroVacinas.situacao == enum_situacao)
    return query.offset(skip).limit(limit).all()


def atualizar_registro_vacina(db: Session, id_vacina: int, dados_atualizacao: VacinasCreate) -> RegistroVacinas:
    vacina = obter_registro_vacina(db, id_vacina)
    dados = dados_atualizacao.model_dump()
    dados["situacao"] = _validar_situacao_vacina(dados["situacao"])

    for campo, valor in dados.items():
        setattr(vacina, campo, valor)
    try:
        db.commit()
        db.refresh(vacina)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro de integridade ao atualizar registro de vacina (verifique chaves estrangeiras).")
    return vacina

def deletar_registro_vacina(db: Session, id_vacina: int) -> dict:
    vacina = obter_registro_vacina(db, id_vacina)
    db.delete(vacina)
    db.commit()
    return {"mensagem": f"Registro de vacina {id_vacina} removido com sucesso."}

def listar_vacinacoes_antirrabicas(db: Session, skip: int = 0, limit: int = 100, animal_atendido: int | None = None, vet_responsavel: int | None = None, situacao: str | None = None, data_vacina: date | None = None,) -> list[RegistroVacinas]:
    query = db.query(RegistroVacinas).filter(RegistroVacinas.antirrabica_ind.is_(True))
    if animal_atendido is not None:
        query = query.filter(RegistroVacinas.animal_atendido == animal_atendido)
    if vet_responsavel is not None:
        query = query.filter(RegistroVacinas.vet_responsavel == vet_responsavel)
    if situacao is not None:
        enum_situacao = _validar_situacao_vacina(situacao)
        query = query.filter(RegistroVacinas.situacao == enum_situacao)
    if data_vacina is not None:
        query = query.filter(RegistroVacinas.data_vacina == data_vacina)
    return query.offset(skip).limit(limit).all()


def obter_vacinacao_antirrabica(db: Session, id_vacina: int) -> RegistroVacinas:
    vacina = (db.query(RegistroVacinas).filter(RegistroVacinas.id_vacina == id_vacina,RegistroVacinas.antirrabica_ind.is_(True),).first())
    if not vacina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Vacinação antirrábica com id {id_vacina} não encontrada.",)
    return vacina

