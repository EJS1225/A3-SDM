from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import (VeterinarioConfirmarSenhaRequest, VeterinarioRegistroRequest, VeterinarioRegistroResponse,
                     VeterinariosResponse, )
from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    LoginRequest,
    TokenResponse,
    create_access_token,
    hash_password,
    verify_password,
    get_current_veterinario
)
from CrudDef import get_db
from modelos import Veterinarios


router = APIRouter(prefix="/api/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
def login_veterinario(payload: LoginRequest, db: Session = Depends(get_db)):
    email_normalizado = payload.email.strip().lower()

    veterinario = (
        db.query(Veterinarios)
        .filter(Veterinarios.email == email_normalizado)
        .first()
    )

    if veterinario is None or not verify_password(payload.senha, veterinario.hash_senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not veterinario.cadastrado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O cadastro do veterinário ainda não foi concluído.",
        )

    if not veterinario.senhaconfirmada:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A senha do veterinário ainda não foi confirmada.",
        )

    if not veterinario.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O cadastro do veterinário está inativo.",
        )

    veterinario.datahora_ultacesso = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()

    access_token = create_access_token(
        data={
            "sub": str(veterinario.id_vets),
            "email": veterinario.email,
            "role": "veterinario",
            "crmv": f"{veterinario.crmv_num}/{veterinario.uf_crmv}"
            if veterinario.crmv_num and veterinario.uf_crmv
            else None,
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

@router.post("/register", response_model=VeterinarioRegistroResponse, status_code=status.HTTP_201_CREATED,)
def registrar_veterinario(payload: VeterinarioRegistroRequest,db: Session = Depends(get_db),):
    email_normalizado = payload.email.strip().lower()
    cpf_limpo = payload.cpf_vet

    existente = (
        db.query(Veterinarios)
        .filter(
            (Veterinarios.email == email_normalizado)
            | (Veterinarios.cpf_vet == cpf_limpo)
        )
        .first()
)
    if existente is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Já existe um veterinário cadastrado com este e-mail ou CPF.",)

    agora = datetime.now(timezone.utc).replace(tzinfo=None)

    novo_vet = Veterinarios(
        nome=payload.nome.strip(),
        sobrenome=payload.sobrenome.strip(),
        telefone=payload.telefone.strip(),
        email=email_normalizado,
        cpf_vet=cpf_limpo,
        crmv_num=payload.crmv_num.strip(),
        uf_crmv=payload.uf_crmv.strip().upper(),
        datacadastro=agora,
        datahora_ultacesso=agora,
        cadastrado=True,
        senhaconfirmada=False,
        ativo=False,  # Mude para True se o acesso for liberado logo após confirmar a senha
        hash_senha=None,
    )

    db.add(novo_vet)
    db.commit()
    db.refresh(novo_vet)

    return VeterinarioRegistroResponse(
        id_vets=novo_vet.id_vets,
        nome=novo_vet.nome,
        sobrenome=novo_vet.sobrenome,
        email=novo_vet.email,
        cadastrado=novo_vet.cadastrado,
        senhaconfirmada=novo_vet.senhaconfirmada,
        ativo=novo_vet.ativo,
        mensagem="Cadastro realizado. Confirme sua senha para habilitar o acesso.",
    )


@router.post("/confirmar-senha", response_model=VeterinarioRegistroResponse)
def confirmar_senha_veterinario(payload: VeterinarioConfirmarSenhaRequest,db: Session = Depends(get_db),):
    if payload.senha != payload.confirmar_senha:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="A senha e a confirmação de senha não coincidem.",)

    email_normalizado = payload.email.strip().lower()
    veterinario = (db.query(Veterinarios).filter(Veterinarios.email == email_normalizado).first())

    if veterinario is None or not veterinario.cadastrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veterinário não encontrado ou cadastro pendente.",)

    if veterinario.senhaconfirmada and veterinario.hash_senha:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A senha deste veterinário já foi confirmada.",)

    veterinario.hash_senha = hash_password(payload.senha)
    veterinario.senhaconfirmada = True
    veterinario.ativo = True  # Remova ou ajuste se houver etapa separada de ativação por admin

    db.commit()
    db.refresh(veterinario)

    return VeterinarioRegistroResponse(
        id_vets=veterinario.id_vets,
        nome=veterinario.nome,
        sobrenome=veterinario.sobrenome,
        email=veterinario.email,
        cadastrado=veterinario.cadastrado,
        senhaconfirmada=veterinario.senhaconfirmada,
        ativo=veterinario.ativo,
        mensagem="Senha confirmada com sucesso. O login já pode ser realizado.",
    )

@router.get("/me", response_model=VeterinariosResponse)
def me_endpoint(current_vet: Veterinarios = Depends(get_current_veterinario)):
    return current_vet