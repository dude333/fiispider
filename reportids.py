import requests
import json
from datetime import date
from dateutil.relativedelta import relativedelta


def getIDs(cnpj, n=4):
    if cnpj is None or len(cnpj) < 14:
        return None

    headers = {
        "Accept": "application/json",
    }

    n = int(n) - 1
    if n < 0 or n > 24:
        n = 3
    dataInicial = date.today().replace(day=1) + relativedelta(months=-n)
    dataFinal = date.today()

    params = (
        ("tipoFundo", "1"),
        ("cnpjFundo", cnpj),
        ("idCategoriaDocumento", "6"),
        ("idTipoDocumento", "40"),
        ("idEspecieDocumento", "0"),
        ("situacao", "A"),
        ("dataInicial", dataInicial.strftime("%d/%m/%Y")),
        ("dataFinal", dataFinal.strftime("%d/%m/%Y")),
        ("_", "1608729063621"),
        ("d", "0"),
        ("s", "0"),
        ("l", "14"),
    )

    response = requests.get(
        "http://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados",
        headers=headers,
        params=params,
        verify=False,
    )

    response_dict = json.loads(response.text)

    ids = []
    if "data" in response_dict:
        for item in response_dict["data"]:
            if "id" in item:
                ids.append(item["id"])

    return ids
