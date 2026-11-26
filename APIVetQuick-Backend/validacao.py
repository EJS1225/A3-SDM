import re
import httpx
def validar_e_limpar_cpf(cpf: str) -> str:
    """Remove caracteres não numéricos, valida os 11 dígitos e os dígitos verificadores do CPF."""
    if not isinstance(cpf, str):
        raise ValueError("CPF inválido.")

    cpf_limpo = re.sub(r"\D", "", cpf)

    if len(cpf_limpo) != 11:
        raise ValueError("CPF deve conter exatamente 11 dígitos.")

    # Rejeita sequências em que todos os dígitos são iguais (ex.: 111.111.111-11)
    if cpf_limpo == cpf_limpo[0] * 11:
        raise ValueError("CPF inválido.")

    # Cálculo do 1º dígito verificador
    soma_1 = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
    digito_1 = (soma_1 * 10) % 11
    digito_1 = 0 if digito_1 == 10 else digito_1

    if digito_1 != int(cpf_limpo[9]):
        raise ValueError("CPF inválido (primeiro dígito verificador incorreto).")

    # Cálculo do 2º dígito verificador
    soma_2 = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
    digito_2 = (soma_2 * 10) % 11
    digito_2 = 0 if digito_2 == 10 else digito_2

    if digito_2 != int(cpf_limpo[10]):
        raise ValueError("CPF inválido (segundo dígito verificador incorreto).")

    return cpf_limpo
def validar_formato_cep(cep: str) -> str:
    """Remove caracteres não numéricos e garante 8 dígitos no CEP."""
    if not isinstance(cep, str):
        raise ValueError("CEP inválido.")

    cep_limpo = re.sub(r"\D", "", cep)
    if len(cep_limpo) != 8:
        raise ValueError("CEP deve conter exatamente 8 dígitos.")

    return cep_limpo

def consultar_viacep(cep: str) -> dict:
    """Consulta o ViaCEP e retorna os dados do endereço se o CEP existir."""
    cep_limpo = validar_formato_cep(cep)
    url = f"https://viacep.com.br/ws/{cep_limpo}/json/"

    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url)
            response.raise_for_status()
            dados = response.json()
    except httpx.TimeoutException as exc:
        raise ValueError("Tempo esgotado ao consultar o serviço ViaCEP.") from exc
    except httpx.HTTPError as exc:
        raise ValueError("Erro de comunicação com o serviço ViaCEP.") from exc

    if not isinstance(dados, dict) or dados.get("erro") is True:
        raise ValueError(f"CEP {cep_limpo} não encontrado no ViaCEP.")

    dados["cep_limpo"] = cep_limpo
    return dados