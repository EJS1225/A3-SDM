from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from CRUDGov import (get_db, criar_registro_vacina, atualizar_registro_vacina, deletar_registro_vacina, listar_vacinacoes_antirrabicas, obter_vacinacao_antirrabica,)
from SchemasGov import VacinasCreate, VacinasResponse

router = APIRouter(prefix="/api/governo/vacinacoes-antirrabicas", tags=["Governo - Vacinações Antirrábicas"],)


@router.post("/", response_model=VacinasResponse, status_code=status.HTTP_201_CREATED, summary="Registrar vacinação antirrábica",)
def post_vacinacao_antirrabica(vacina: VacinasCreate, db: Session = Depends(get_db),):
    dados = vacina.model_copy(update={"antirrabica_ind": "True"})
    return criar_registro_vacina(db=db, vacina=dados)


@router.get("/", response_model=list[VacinasResponse], status_code=status.HTTP_200_OK, summary="Listar vacinações antirrábicas",)
def get_vacinacoes_antirrabicas(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
    animal_atendido: int | None = Query(None, description="Filtrar por ID do animal"),
    vet_responsavel: int | None = Query(None, description="Filtrar por ID do veterinário"),
    situacao: str | None = Query(None, description="Agendada, Aplicada ou Cancelada"),
    data_vacina: date | None = Query(None, description="Filtrar por data da vacina (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    return listar_vacinacoes_antirrabicas(
        db=db,
        skip=skip,
        limit=limit,
        animal_atendido=animal_atendido,
        vet_responsavel=vet_responsavel,
        situacao=situacao,
        data_vacina=data_vacina,
    )


@router.get("/{id_vacina}", response_model=VacinasResponse, status_code=status.HTTP_200_OK, summary="Buscar vacinação antirrábica por ID",)
def get_vacinacao_antirrabica(id_vacina: int, db: Session = Depends(get_db),):
    return obter_vacinacao_antirrabica(db=db, id_vacina=id_vacina)


@router.put("/{id_vacina}",response_model=VacinasResponse, status_code=status.HTTP_200_OK, summary="Atualizar vacinação antirrábica",)
def put_vacinacao_antirrabica(id_vacina: int, dados_atualizacao: VacinasCreate, db: Session = Depends(get_db),):
    obter_vacinacao_antirrabica(db=db, id_vacina=id_vacina)
    dados = dados_atualizacao.model_copy(update={"antirrabica_ind": "True"})
    return atualizar_registro_vacina(db=db, id_vacina=id_vacina, dados_atualizacao=dados,)


@router.delete("/{id_vacina}", status_code=status.HTTP_200_OK, summary="Excluir vacinação antirrábica",)
def delete_vacinacao_antirrabica(id_vacina: int, db: Session = Depends(get_db),):
    obter_vacinacao_antirrabica(db=db, id_vacina=id_vacina)
    return deletar_registro_vacina(db=db, id_vacina=id_vacina)