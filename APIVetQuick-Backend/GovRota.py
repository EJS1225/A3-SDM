from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from auth import get_current_veterinario
from CrudDef import get_db
from GovSync import sincronizar_animal, sincronizar_lote_antirrabicas, sincronizar_vacina_antirrabica
from modelos import Veterinarios

router = APIRouter(prefix="/api/sync/governo", tags=["Sincronização Governo"])


@router.post("/animais/{id_animais}")
def sync_animal_endpoint(
    id_animais: int,
    db: Session = Depends(get_db),
    _: Veterinarios = Depends(get_current_veterinario),
):
    return sincronizar_animal(db, id_animais)


@router.post("/vacinas/{id_vacina}")
def sync_vacina_endpoint(
    id_vacina: int,
    db: Session = Depends(get_db),
    _: Veterinarios = Depends(get_current_veterinario),
):
    return sincronizar_vacina_antirrabica(db, id_vacina)


@router.post("/vacinas-antirrabicas/lote")
def sync_lote_antirrabicas_endpoint(
    db: Session = Depends(get_db),
    _: Veterinarios = Depends(get_current_veterinario),
):
    return sincronizar_lote_antirrabicas(db)