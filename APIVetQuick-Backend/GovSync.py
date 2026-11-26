from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from GovClient import GovApiClient
from modelos import Animais, RegistroVacinas
import logging
from dbase import SessionLocal


def _animal_to_gov_payload(animal: Animais) -> dict:
    if animal.id_rfid is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"O animal {animal.id_animais} ({animal.nome}) não possui id_rfid vinculado para sincronizar com o governo.",
        )
    return {
        "tutor_id": animal.tutor_id,
        "nome": animal.nome,
        "idade_estimada": animal.idade_estimada,
        "sexo": animal.sexo,
        "cor": animal.cor,
        "peso_atual_kg": animal.peso_atual_kg,
        "especie": animal.especie,
        "raca": animal.raca,
        "situacao": animal.situacao,
        "id_rfid": animal.id_rfid,
        "data_rfid_vinculo": animal.data_rfid_vinculo.isoformat() if animal.data_rfid_vinculo else None,
        "vet_rfid_vinculo": animal.vet_rfid_vinculo,
    }


def _vacina_to_gov_payload(vacina: RegistroVacinas) -> dict:
    if not vacina.antirrabica_ind:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"A vacina {vacina.id_vacina} não é antirrábica (antirrabica_ind=False).",
        )
    situacao_valor = vacina.situacao.value if hasattr(vacina.situacao, "value") else str(vacina.situacao)
    return {
        "animal_atendido": vacina.animal_atendido,
        "vet_responsavel": vacina.vet_responsavel,
        "nome_vacina": vacina.nome_vacina,
        "tipo_vacina": vacina.tipo_vacina,
        "antirrabica_ind": True,
        "fabricante": vacina.fabricante,
        "lote": vacina.lote,
        "data_vacina": vacina.data_vacina.isoformat() if vacina.data_vacina else None,
        "dose_vacina": vacina.dose_vacina,
        "via_aplicacao": vacina.via_aplicacao,
        "data_prox_dose": vacina.data_prox_dose.isoformat() if vacina.data_prox_dose else None,
        "validade_lote": vacina.validade_lote.isoformat() if vacina.validade_lote else None,
        "observ": vacina.observ,
        "situacao": situacao_valor,
    }


def sincronizar_animal(db: Session, id_animais: int, client: GovApiClient | None = None) -> dict:
    client = client or GovApiClient()
    animal = db.query(Animais).filter(Animais.id_animais == id_animais).first()
    if not animal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado no VetQuick.")

    payload = _animal_to_gov_payload(animal)
    existente = client.buscar_animal_por_rfid(animal.id_rfid)

    if existente is None:
        resultado = client.criar_animal(payload)
        acao = "criado"
    else:
        id_gov = existente.get("id_rfid", animal.id_rfid)
        resultado = client.atualizar_animal(id_gov, payload)
        acao = "atualizado"

    return {"acao": acao, "id_animais": animal.id_animais, "id_rfid": animal.id_rfid, "dados_gov": resultado}


def sincronizar_vacina_antirrabica(db: Session, id_vacina: int, client: GovApiClient | None = None) -> dict:
    client = client or GovApiClient()
    vacina = db.query(RegistroVacinas).filter(RegistroVacinas.id_vacina == id_vacina).first()
    if not vacina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de vacina não encontrado no VetQuick.")

    # Garante que o animal esteja sincronizado antes de enviar a vacina
    sincronizar_animal(db, vacina.animal_atendido, client=client)

    payload = _vacina_to_gov_payload(vacina)
    candidatas = client.listar_vacinas_antirrabicas(
        animal_atendido=vacina.animal_atendido,
        data_vacina=vacina.data_vacina.isoformat() if vacina.data_vacina else None,
    )
    correspondente = next(
        (item for item in candidatas if item.get("lote") == vacina.lote and item.get("nome_vacina") == vacina.nome_vacina),
        None,
    )

    if correspondente is None:
        resultado = client.criar_vacina_antirrabica(payload)
        acao = "criado"
    else:
        resultado = client.atualizar_vacina_antirrabica(correspondente["id_vacina"], payload)
        acao = "atualizado"

    return {"acao": acao, "id_vacina": vacina.id_vacina, "dados_gov": resultado}


def sincronizar_lote_antirrabicas(db: Session, client: GovApiClient | None = None) -> dict:
    client = client or GovApiClient()
    vacinas = db.query(RegistroVacinas).filter(RegistroVacinas.antirrabica_ind.is_(True)).all()
    sucessos = []
    falhas = []

    for vacina in vacinas:
        try:
            sucessos.append(sincronizar_vacina_antirrabica(db, vacina.id_vacina, client=client))
        except HTTPException as exc:
            falhas.append({"id_vacina": vacina.id_vacina, "erro": exc.detail})

    return {
        "total_encontradas": len(vacinas),
        "sincronizadas": len(sucessos),
        "falhas": len(falhas),
        "detalhes_sucesso": sucessos,
        "detalhes_falha": falhas,
    }

logger = logging.getLogger("gov_sync")

def _rodar_sync_animal_bg(id_animais: int) -> None:
    db = SessionLocal()
    try:
        sincronizar_animal(db, id_animais)
        logger.info("Animal %s sincronizado com a API Gov.", id_animais)
    except Exception as exc:
        logger.warning("Falha ao sincronizar animal %s com a API Gov: %s", id_animais, exc)
    finally:
        db.close()


def _rodar_sync_vacina_bg(id_vacina: int) -> None:
    db = SessionLocal()
    try:
        sincronizar_vacina_antirrabica(db, id_vacina)
        logger.info("Vacina %s sincronizada com a API Gov.", id_vacina)
    except Exception as exc:
        logger.warning("Falha ao sincronizar vacina %s com a API Gov: %s", id_vacina, exc)
    finally:
        db.close()


def agendar_sync_animal(background_tasks, id_animais: int, id_rfid: int | None) -> None:
    if id_rfid is not None:
        background_tasks.add_task(_rodar_sync_animal_bg, id_animais)


def agendar_sync_vacina(background_tasks, id_vacina: int, antirrabica_ind: bool) -> None:
    if antirrabica_ind:
        background_tasks.add_task(_rodar_sync_vacina_bg, id_vacina)