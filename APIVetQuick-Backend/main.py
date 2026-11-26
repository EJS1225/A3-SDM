from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from rota_auth import router as rota_auth_router
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from auth import get_current_veterinario
from GovRota import router as gov_sync_router
from GovSync import agendar_sync_animal, agendar_sync_vacina

from schemas import (
    TutoresCreate,
    TutoresResponse,
    AnimaisCreate,
    AnimaisResponse,
    MicrochipUpdate,
    MicrochipResponse,
    ConsultasCreate,
    ConsultasResponse,
    VacinasCreate,
    VacinasResponse,
)

from CrudDef import (
    get_db,
    get_tutores,
    get_tutor,
    create_tutores,
    update_tutor,
    delete_tutor,
    get_animais,
    get_animal,
    create_animais,
    update_animal,
    delete_animal,
    get_microchip_animal,
    create_or_update_microchip_animal,
    patch_microchip_animal,
    delete_microchip_animal,
    get_consultas,
    get_consultas_animal,
    create_consultas,
    update_consulta,
    delete_consulta,
    get_vacinas,
    get_vacina,
    get_vacinas_animal,
    create_vacinas,
    update_vacina,
    delete_vacina,
    get_consulta,
)

# FASTAPI APP & ENDPOINTS

app = FastAPI(title="VetQuick", description="API VetQuick", version="1.0.0")
app.include_router(gov_sync_router)


app.include_router(rota_auth_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Tutores ---
@app.get("/api/tutores/", response_model=list[TutoresResponse])
def get_tutores_endpoint(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_tutores(db, skip=skip, limit=limit)
@app.get("/api/tutores/{id_tutores}", response_model=TutoresResponse)
def get_tutor_endpoint(id_tutores: int, db: Session = Depends(get_db)):
    db_tutor = get_tutor(db, id_tutores)
    if db_tutor is None:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return db_tutor

@app.post("/api/tutores/", response_model=TutoresResponse)
def create_tutores_endpoint(tutor: TutoresCreate, db: Session = Depends(get_db)):
    return create_tutores(db, tutor)

@app.put("/api/tutores/{id_tutores}", response_model=TutoresResponse)
def update_tutor_endpoint(id_tutores: int, tutor: TutoresCreate, db: Session = Depends(get_db)):
    db_tutor = update_tutor(db, id_tutores, tutor)
    if db_tutor is None:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return db_tutor

@app.delete("/api/tutores/{id_tutores}", response_model=TutoresResponse)
def delete_tutor_endpoint(id_tutores: int, db: Session = Depends(get_db)):
    db_tutor = delete_tutor(db, id_tutores)
    if db_tutor is None:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return db_tutor


# --- Animais ---
@app.get("/api/animais/", response_model=list[AnimaisResponse])
def get_animais_list_endpoint(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_animais(db, skip=skip, limit=limit)

@app.get("/api/animais/{id_animais}", response_model=AnimaisResponse)
def get_animais_endpoint(id_animais: int, db: Session = Depends(get_db)):
    db_animal = get_animal(db, id_animais)
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    return db_animal

@app.post("/api/animais/", response_model=AnimaisResponse)
def create_animais_endpoint(
    animal: AnimaisCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    db_animal = create_animais(db, animal)
    agendar_sync_animal(background_tasks, db_animal.id_animais, db_animal.id_rfid)
    return db_animal

@app.put("/api/animais/{id_animais}", response_model=AnimaisResponse)
def update_animal_endpoint(
    id_animais: int,
    animal: AnimaisCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    db_animal = update_animal(db, id_animais, animal)
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    agendar_sync_animal(background_tasks, db_animal.id_animais, db_animal.id_rfid)
    return db_animal

@app.delete("/api/animais/{id_animais}", response_model=AnimaisResponse)
def delete_animal_endpoint(id_animais: int, db: Session = Depends(get_db)):
    db_animal = delete_animal(db, id_animais)
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    return db_animal

# --- Microchip ---
@app.get("/api/animais/{id_animais}/microchip", response_model=MicrochipResponse)
def get_microchip_animal_endpoint(id_animais: int, db: Session = Depends(get_db)):
    db_animal = get_microchip_animal(db, id_animais)
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    return db_animal

@app.post("/api/animais/{id_animais}/microchip", response_model=MicrochipResponse, status_code=201)
def create_microchip_animal_endpoint( id_animais: int, microchip: MicrochipUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db),):
    db_animal = create_or_update_microchip_animal(db, id_animais, microchip)
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    agendar_sync_animal(background_tasks, db_animal.id_animais, db_animal.id_rfid)
    return db_animal


@app.put("/api/animais/{id_animais}/microchip", response_model=MicrochipResponse)
def update_microchip_animal_endpoint(id_animais: int, microchip: MicrochipUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db),):
    db_animal = create_or_update_microchip_animal(db, id_animais, microchip)
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    agendar_sync_animal(background_tasks, db_animal.id_animais, db_animal.id_rfid)
    return db_animal


@app.patch("/api/animais/{id_animais}/microchip", response_model=MicrochipResponse)
def patch_microchip_animal_endpoint(id_animais: int, microchip: MicrochipUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db),):
    db_animal = patch_microchip_animal(db, id_animais, microchip)
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    agendar_sync_animal(background_tasks, db_animal.id_animais, db_animal.id_rfid)
    return db_animal

@app.delete("/api/animais/{id_animais}/microchip", response_model=MicrochipResponse)
def delete_microchip_animal_endpoint(id_animais: int, db: Session = Depends(get_db)):
    db_animal = delete_microchip_animal(db, id_animais)
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    return db_animal

# --- Consultas ---
@app.get("/api/animais/{id_animais}/consultas", response_model=list[ConsultasResponse])
def get_consultas_animal_endpoint(id_animais: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db),):
    db_animal = get_animal(db, id_animais)
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    return get_consultas_animal(db, id_animais=id_animais, skip=skip, limit=limit)

@app.get("/api/consultas/", response_model=list[ConsultasResponse])
def get_consultas_endpoint(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_consultas(db, skip=skip, limit=limit)

@app.get("/api/consultas/{id_consulta}", response_model=ConsultasResponse)
def get_consulta_endpoint(id_consulta: int, db: Session = Depends(get_db)):
    db_consulta = get_consulta(db, id_consulta)
    if db_consulta is None:
        raise HTTPException(status_code=404, detail="Consulta not found")
    return db_consulta

@app.post("/api/consultas/", response_model=ConsultasResponse)
def create_consultas_endpoint(consulta: ConsultasCreate, db: Session = Depends(get_db)):
    return create_consultas(db, consulta)

@app.put("/api/consultas/{id_consulta}", response_model=ConsultasResponse)
def update_consulta_endpoint(id_consulta: int, consulta: ConsultasCreate, db: Session = Depends(get_db)):
    db_consulta = update_consulta(db, id_consulta, consulta)
    if db_consulta is None:
        raise HTTPException(status_code=404, detail="Consulta not found")
    return db_consulta

@app.delete("/api/consultas/{id_consulta}", response_model=ConsultasResponse)
def delete_consulta_endpoint(id_consulta: int, db: Session = Depends(get_db)):
    db_consulta = delete_consulta(db, id_consulta)
    if db_consulta is None:
        raise HTTPException(status_code=404, detail="Consulta not found")
    return db_consulta


# --- Vacinas ---
@app.get("/api/animais/{id_animais}/vacinas", response_model=list[VacinasResponse])
def get_vacinas_animal_endpoint(id_animais: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db),):
    db_animal = get_animal(db, id_animais)
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    return get_vacinas_animal(db, id_animais=id_animais, skip=skip, limit=limit)

@app.get("/api/vacinas/", response_model=list[VacinasResponse])
def get_vacinas_endpoint(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_vacinas(db, skip=skip, limit=limit)

@app.get("/api/vacinas/{id_vacinas}", response_model=VacinasResponse)
def get_vacina_endpoint(id_vacinas: int, db: Session = Depends(get_db)):
    db_vacina = get_vacina(db, id_vacinas)
    if db_vacina is None:
        raise HTTPException(status_code=404, detail="Vacina not found")
    return db_vacina

@app.post("/api/vacinas/", response_model=VacinasResponse)
def create_vacinas_endpoint(vacina: VacinasCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db),):
    db_vacina = create_vacinas(db, vacina)
    agendar_sync_vacina(background_tasks, db_vacina.id_vacina, db_vacina.antirrabica_ind)
    return db_vacina


@app.put("/api/vacinas/{id_vacina}", response_model=VacinasResponse)
def update_vacina_endpoint(id_vacina: int, vacina: VacinasCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db),):
    db_vacina = update_vacina(db, id_vacina, vacina)
    if db_vacina is None:
        raise HTTPException(status_code=404, detail="Vacina not found")
    agendar_sync_vacina(background_tasks, db_vacina.id_vacina, db_vacina.antirrabica_ind)
    return db_vacina
@app.delete("/api/vacinas/{id_vacina}", response_model=VacinasResponse)
def delete_vacina_endpoint(id_vacina: int, db: Session = Depends(get_db)):
    db_vacina = delete_vacina(db, id_vacina)
    if db_vacina is None:
        raise HTTPException(status_code=404, detail="Vacina not found")
    return db_vacina