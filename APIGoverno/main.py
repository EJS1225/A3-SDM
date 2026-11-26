from fastapi import FastAPI
from RotasGovAnimais import router as animais_gov_router
from RotasGovVacinas import router as antirrabicas_gov_router

app = FastAPI(title='API Gov Simulada', description='Simulação de uma API Governamental', version='1.0.0')

app.include_router(animais_gov_router)
app.include_router(antirrabicas_gov_router)