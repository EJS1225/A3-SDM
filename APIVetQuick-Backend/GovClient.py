import os
from typing import Any
import httpx
from fastapi import HTTPException, status

GOV_API_BASE_URL = os.getenv("GOV_API_URL", "http://localhost:8001").rstrip("/")
GOV_API_TIMEOUT = float(os.getenv("GOV_API_TIMEOUT", "10.0"))


class GovApiClient:
    def __init__(self, base_url: str = GOV_API_BASE_URL, timeout: float = GOV_API_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout

    def _request(self, method: str, path: str, *, json: dict[str, Any] | None = None, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.request(method, url, json=json, params=params)
        except httpx.TimeoutException as exc:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Tempo esgotado ao comunicar com a API Governamental.",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Falha de rede ao acessar a API Governamental: {exc}",
            ) from exc

        if resp.status_code >= 400:
            try:
                detalhe = resp.json().get("detail", resp.text)
            except ValueError:
                detalhe = resp.text
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"API Governamental retornou erro ({resp.status_code}): {detalhe}",
            )

        if not resp.content:
            return None
        return resp.json()

    # --- Animais ---
    def buscar_animal_por_rfid(self, id_rfid: int) -> dict[str, Any] | None:
        try:
            return self._request("GET", f"/api/governo/animais/{id_rfid}")
        except HTTPException as exc:
            if exc.status_code == status.HTTP_404_NOT_FOUND:
                return None
            raise

    def criar_animal(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/api/governo/animais/", json=payload)

    def atualizar_animal(self, id_rfid: int, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("PUT", f"/api/governo/animais/{id_rfid}", json=payload)

    # --- Vacinações Antirrábicas ---
    def listar_vacinas_antirrabicas(self, animal_atendido: int | None = None, data_vacina: str | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"limit": 500}
        if animal_atendido is not None:
            params["animal_atendido"] = animal_atendido
        if data_vacina is not None:
            params["data_vacina"] = data_vacina
        return self._request("GET", "/api/governo/vacinacoes-antirrabicas/", params=params)

    def criar_vacina_antirrabica(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/api/governo/vacinacoes-antirrabicas/", json=payload)

    def atualizar_vacina_antirrabica(self, id_vacina_gov: int, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("PUT", f"/api/governo/vacinacoes-antirrabicas/{id_vacina_gov}", json=payload)