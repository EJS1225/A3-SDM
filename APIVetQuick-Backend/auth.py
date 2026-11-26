import os
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from CrudDef import get_db
from modelos import Veterinarios

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "NossoSegredo")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

security = HTTPBearer()


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_veterinario(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db),) -> Veterinarios:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado.", headers={"WWW-Authenticate": "Bearer"},)
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        vet_id = payload.get("sub")
        if vet_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    vet = db.query(Veterinarios).filter(Veterinarios.id_vets == int(vet_id)).first()
    if vet is None:
        raise credentials_exception

    if not vet.cadastrado or not vet.senhaconfirmada or not vet.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Veterinário sem permissão de acesso (cadastro, confirmação de senha ou status ativo pendente).",)
    return vet