from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from CRUDGov import (get_db, criar_animal, obter_animal, listar_animais, atualizar_animal, deletar_animal)
from SchemasGov import AnimaisCreate, AnimaisResponse

router = APIRouter(prefix="/api/governo/animais", tags=["Governo - Animais"])

@router.post(
    "/",response_model=AnimaisResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar um novo animal")
def post_animal(animal: AnimaisCreate, db: Session = Depends(get_db)):
    return criar_animal(db=db, animal=animal)

@router.get("/",  response_model=list[AnimaisResponse], status_code=status.HTTP_200_OK, summary="Listar animais cadastrados")
def get_animais(
    skip: int = Query(0, ge=0, description="Quantidade de registros para pular"),
    limit: int = Query(100, ge=1, le=500, description="Limite máximo de registros"),
    tutor_id: int | None = Query(None, description="Filtrar por ID do tutor"),
    situacao: str | None = Query(None, description="Filtrar por situação do animal"),
    db: Session = Depends(get_db)
):
    return listar_animais(
        db=db,
        skip=skip,
        limit=limit,
        tutor_id=tutor_id,
        situacao=situacao
    )

@router.get("/{id_rfid}", response_model=AnimaisResponse, status_code=status.HTTP_200_OK, summary="Buscar animal por ID")
def get_animal_por_id(id_rfid: int, db: Session = Depends(get_db)):
    return obter_animal(db=db, id_rfid=id_rfid)

@router.put("/{id_rfid}",response_model=AnimaisResponse, status_code=status.HTTP_200_OK, summary="Atualizar dados de um animal")
def put_animal(id_rfid: int, dados_atualizacao: AnimaisCreate,db: Session = Depends(get_db)):
    return atualizar_animal(db=db, id_rfid=id_rfid, dados_atualizacao=dados_atualizacao)

@router.delete("/{id_rfid}",  status_code=status.HTTP_200_OK, summary="Excluir um animal")
def delete_animal(id_rfid: int,db: Session = Depends(get_db)):
    return deletar_animal(db=db, id_rfid=id_rfid)
