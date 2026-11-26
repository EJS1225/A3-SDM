from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from dbase import SessionLocal
from datetime import date
from validacao import consultar_viacep
from modelos import (
    Tutores,
    Animais,
    Veterinarios,
    RegistroConsultas,
    RegistroVacinas,
    Enderecos
)
from schemas import (
    TutoresCreate,
    AnimaisCreate,
    MicrochipUpdate,
    ConsultasCreate,
    VacinasCreate,
)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD - TUTORES

def get_tutor(db: Session, id_tutores: int):
    return db.query(Tutores).filter(Tutores.id_tutores == id_tutores).first()

def get_tutores(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Tutores).offset(skip).limit(limit).all()

def _resolver_endereco_tutor(db: Session, tutor: TutoresCreate, endereco_atual_id: int | None = None) -> int | None:
    if tutor.cep:
        try:
            dados_cep = consultar_viacep(tutor.cep)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,detail=str(exc),) from exc

        ddd_str = (dados_cep.get("ddd") or "").strip()
        ddd_int = int(ddd_str) if ddd_str.isdigit() else None

        endereco = None
        if endereco_atual_id is not None:
            endereco = db.query(Enderecos).filter(Enderecos.id_endereco == endereco_atual_id).first()

        if endereco is None:
            endereco = Enderecos()
            db.add(endereco)

        endereco.cep = dados_cep["cep_limpo"]
        endereco.logradouro = dados_cep.get("logradouro") or ""
        endereco.bairro = dados_cep.get("bairro") or ""
        endereco.cidade = dados_cep.get("localidade") or ""
        endereco.uf = dados_cep.get("uf") or ""
        endereco.codibge = dados_cep.get("ibge") or ""
        endereco.ddd = ddd_int
        if tutor.numero_telefone is not None:
            endereco.numero_telefone = tutor.numero_telefone

        db.flush()
        return endereco.id_endereco

    if tutor.enderecoassociado is not None:
        endereco_existente = (db.query(Enderecos).filter(Enderecos.id_endereco == tutor.enderecoassociado).first())
        if endereco_existente is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Endereço com id {tutor.enderecoassociado} não encontrado.",)
        return endereco_existente.id_endereco

    return endereco_atual_id


def create_tutores(db: Session, tutor: TutoresCreate):
    id_endereco = _resolver_endereco_tutor(db, tutor)
    db_tutor = Tutores(
        nome=tutor.nome,
        sobrenome=tutor.sobrenome,
        telefone=tutor.telefone,
        email=tutor.email,
        datacadastro=tutor.datacadastro,
        cadastroconfirmado=tutor.cadastroconfirmado,
        cpf_tutor=tutor.cpf_tutor,
        enderecoassociado=id_endereco,
    )
    db.add(db_tutor)
    db.commit()
    db.refresh(db_tutor)
    return db_tutor


def update_tutor(db: Session, id_tutores: int, tutor: TutoresCreate):
    db_tutor = get_tutor(db, id_tutores)
    if db_tutor is None:
        return None

    id_endereco = _resolver_endereco_tutor(db, tutor, endereco_atual_id=db_tutor.enderecoassociado)
    db_tutor.nome = tutor.nome
    db_tutor.sobrenome = tutor.sobrenome
    db_tutor.telefone = tutor.telefone
    db_tutor.email = tutor.email
    db_tutor.datacadastro = tutor.datacadastro
    db_tutor.cadastroconfirmado = tutor.cadastroconfirmado
    db_tutor.cpf_tutor = tutor.cpf_tutor
    db_tutor.enderecoassociado = id_endereco
    db.commit()
    db.refresh(db_tutor)
    return db_tutor

def delete_tutor(db: Session, id_tutores: int):
    db_tutor = get_tutor(db, id_tutores)
    if db_tutor is None:
        return None
    db.delete(db_tutor)
    db.commit()
    return db_tutor

# CRUD - ANIMAIS

def get_animal(db: Session, id_animais: int):
    return db.query(Animais).filter(Animais.id_animais == id_animais).first()

def get_animais(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Animais).offset(skip).limit(limit).all()

def create_animais(db: Session, animal: AnimaisCreate):
    db_animal = Animais(
        tutor_id=animal.tutor_id,
        nome=animal.nome,
        idade_estimada=animal.idade_estimada,
        sexo=animal.sexo,
        cor=animal.cor,
        peso_atual_kg=animal.peso_atual_kg,
        especie=animal.especie,
        raca=animal.raca,
        situacao=animal.situacao,
        id_rfid=animal.id_rfid,
        data_rfid_vinculo=animal.data_rfid_vinculo,
        vet_rfid_vinculo=animal.vet_rfid_vinculo,
    )
    db.add(db_animal)
    db.commit()
    db.refresh(db_animal)
    return db_animal

def update_animal(db: Session, id_animais: int, animal: AnimaisCreate):
    db_animal = get_animal(db, id_animais)
    if db_animal is None:
        return None
    db_animal.tutor_id = animal.tutor_id
    db_animal.nome = animal.nome
    db_animal.idade_estimada = animal.idade_estimada
    db_animal.sexo = animal.sexo
    db_animal.cor = animal.cor
    db_animal.peso_atual_kg = animal.peso_atual_kg
    db_animal.especie = animal.especie
    db_animal.raca = animal.raca
    db_animal.situacao = animal.situacao
    db_animal.id_rfid = animal.id_rfid
    db_animal.data_rfid_vinculo = animal.data_rfid_vinculo
    db_animal.vet_rfid_vinculo = animal.vet_rfid_vinculo
    db.commit()
    db.refresh(db_animal)
    return db_animal

def delete_animal(db: Session, id_animais: int):
    db_animal = get_animal(db, id_animais)
    if db_animal is None:
        return None
    db.delete(db_animal)
    db.commit()
    return db_animal

# CRUD - MICROCHIP (RFID do Animal)
def validar_veterinario_e_rfid(db: Session, id_animais: int, id_rfid: int | None, vet_rfid_vinculo: int | None,):
    if vet_rfid_vinculo is not None:
        vet = db.query(Veterinarios).filter(Veterinarios.id_vets == vet_rfid_vinculo).first()
        if vet is None:
            raise HTTPException(status_code=400, detail=f"Veterinário com id {vet_rfid_vinculo} não encontrado.",)

    if id_rfid is not None:
        animal_duplicado = (db.query(Animais).filter(Animais.id_rfid == id_rfid, Animais.id_animais != id_animais).first())
        if animal_duplicado is not None:
            raise HTTPException(status_code=409, detail=f"O RFID {id_rfid} já está vinculado ao animal de id {animal_duplicado.id_animais}.",)

def get_microchip_animal(db: Session, id_animais: int):
    return get_animal(db, id_animais)

def create_or_update_microchip_animal(db: Session, id_animais: int, microchip: MicrochipUpdate):
    db_animal = get_animal(db, id_animais)
    if db_animal is None:
        return None

    if microchip.id_rfid is None:
        raise HTTPException(status_code=422, detail="O campo 'id_rfid' é obrigatório para vincular um microchip.",)

    validar_veterinario_e_rfid(db=db, id_animais=id_animais, id_rfid=microchip.id_rfid, vet_rfid_vinculo=microchip.vet_rfid_vinculo,)

    db_animal.id_rfid = microchip.id_rfid
    db_animal.data_rfid_vinculo = microchip.data_rfid_vinculo or date.today()
    db_animal.vet_rfid_vinculo = microchip.vet_rfid_vinculo
    db.commit()
    db.refresh(db_animal)
    return db_animal

def patch_microchip_animal(db: Session, id_animais: int, microchip: MicrochipUpdate):
    db_animal = get_animal(db, id_animais)
    if db_animal is None:
        return None

    update_data = microchip.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=422,
            detail="Envie ao menos um campo para atualização parcial.",
        )

    novo_id_rfid = update_data.get("id_rfid", db_animal.id_rfid)
    novo_vet = update_data.get("vet_rfid_vinculo", db_animal.vet_rfid_vinculo)
    validar_veterinario_e_rfid(db=db, id_animais=id_animais, id_rfid=novo_id_rfid if "id_rfid" in update_data else None, vet_rfid_vinculo=novo_vet if "vet_rfid_vinculo" in update_data else None,)
    for campo, valor in update_data.items():
        setattr(db_animal, campo, valor)
    if "data_rfid_vinculo" not in update_data and "id_rfid" in update_data and update_data["id_rfid"] is not None:
        db_animal.data_rfid_vinculo = date.today()
    db.commit()
    db.refresh(db_animal)
    return db_animal

def delete_microchip_animal(db: Session, id_animais: int):
    db_animal = get_animal(db, id_animais)
    if db_animal is None:
        return None
    db_animal.id_rfid = None
    db_animal.data_rfid_vinculo = None
    db_animal.vet_rfid_vinculo = None
    db.commit()
    db.refresh(db_animal)
    return db_animal

# CRUD - CONSULTAS
def get_consultas_animal(db: Session, id_animais: int, skip: int = 0, limit: int = 10):
    return db.query(RegistroConsultas).filter(RegistroConsultas.animal_atendido == id_animais).offset(skip).limit(limit).all()

def get_consulta(db: Session, id_consulta: int):
    return db.query(RegistroConsultas).filter(RegistroConsultas.id_consulta == id_consulta).first()

def get_consultas(db: Session, skip: int = 0, limit: int = 10):
    return db.query(RegistroConsultas).offset(skip).limit(limit).all()

def create_consultas(db: Session, consulta: ConsultasCreate):
    db_consulta = RegistroConsultas(
        animal_atendido=consulta.animal_atendido,
        vet_responsavel=consulta.vet_responsavel,
        datahora_atendimento=consulta.datahora_atendimento,
        motivo=consulta.motivo,
        anamnese=consulta.anamnese,
        sintomas=consulta.sintomas,
        diagnostico=consulta.diagnostico,
        tratamento=consulta.tratamento,
        prescr_medicam=consulta.prescr_medicam,
        peso_kg=consulta.peso_kg,
        temperatura=consulta.temperatura,
        obser=consulta.obser,
        situacao_atual=consulta.situacao_atual,
    )
    db.add(db_consulta)
    db.commit()
    db.refresh(db_consulta)
    return db_consulta

def update_consulta(db: Session, id_consulta: int, consulta: ConsultasCreate):
    db_consulta = get_consulta(db, id_consulta)
    if db_consulta is None:
        return None
    db_consulta.animal_atendido = consulta.animal_atendido
    db_consulta.vet_responsavel = consulta.vet_responsavel
    db_consulta.datahora_atendimento = consulta.datahora_atendimento
    db_consulta.motivo = consulta.motivo
    db_consulta.anamnese = consulta.anamnese
    db_consulta.sintomas = consulta.sintomas
    db_consulta.diagnostico = consulta.diagnostico
    db_consulta.tratamento = consulta.tratamento
    db_consulta.prescr_medicam = consulta.prescr_medicam
    db_consulta.peso_kg = consulta.peso_kg
    db_consulta.temperatura = consulta.temperatura
    db_consulta.obser = consulta.obser
    db_consulta.situacao_atual = consulta.situacao_atual
    db.commit()
    db.refresh(db_consulta)
    return db_consulta

def delete_consulta(db: Session, id_consulta: int):
    db_consulta = get_consulta(db, id_consulta)
    if db_consulta is None:
        return None
    db.delete(db_consulta)
    db.commit()
    return db_consulta


# CRUD - VACINAS

def get_vacinas_animal(db: Session, id_animais: int, skip: int = 0, limit: int = 10):
    return db.query(RegistroVacinas).filter(RegistroVacinas.animal_atendido == id_animais).offset(skip).limit(limit).all()

def get_vacina(db: Session, id_vacina: int):
    return db.query(RegistroVacinas).filter(RegistroVacinas.id_vacina == id_vacina).first()

def get_vacinas(db: Session, skip: int = 0, limit: int = 10):
    return db.query(RegistroVacinas).offset(skip).limit(limit).all()

def create_vacinas(db: Session, vacina: VacinasCreate):
    db_vacina = RegistroVacinas(
        animal_atendido=vacina.animal_atendido,
        vet_responsavel=vacina.vet_responsavel,
        nome_vacina=vacina.nome_vacina,
        tipo_vacina=vacina.tipo_vacina,
        antirrabica_ind=vacina.antirrabica_ind,
        fabricante=vacina.fabricante,
        lote=vacina.lote,
        data_vacina=vacina.data_vacina,
        dose_vacina=vacina.dose_vacina,
        via_aplicacao=vacina.via_aplicacao,
        data_prox_dose=vacina.data_prox_dose,
        validade_lote=vacina.validade_lote,
        observ=vacina.observ,
        situacao=vacina.situacao,
    )
    db.add(db_vacina)
    db.commit()
    db.refresh(db_vacina)
    return db_vacina

def update_vacina(db: Session, id_vacina: int, vacina: VacinasCreate):
    db_vacina = get_vacina(db, id_vacina)
    if db_vacina is None:
        return None
    db_vacina.animal_atendido = vacina.animal_atendido
    db_vacina.vet_responsavel = vacina.vet_responsavel
    db_vacina.nome_vacina = vacina.nome_vacina
    db_vacina.tipo_vacina = vacina.tipo_vacina
    db_vacina.antirrabica_ind = vacina.antirrabica_ind
    db_vacina.fabricante = vacina.fabricante
    db_vacina.lote = vacina.lote
    db_vacina.data_vacina = vacina.data_vacina
    db_vacina.dose_vacina = vacina.dose_vacina
    db_vacina.via_aplicacao = vacina.via_aplicacao
    db_vacina.data_prox_dose = vacina.data_prox_dose
    db_vacina.validade_lote = vacina.validade_lote
    db_vacina.observ = vacina.observ
    db_vacina.situacao = vacina.situacao
    db.commit()
    db.refresh(db_vacina)
    return db_vacina

def delete_vacina(db: Session, id_vacina: int):
    db_vacina = get_vacina(db, id_vacina)
    if db_vacina is None:
        return None
    db.delete(db_vacina)
    db.commit()
    return db_vacina


