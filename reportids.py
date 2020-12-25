import requests
import json


def getIDs(cnpj):
    if cnpj is None or len(cnpj) < 14:
        return None

    headers = {
        "Accept": "application/json",
    }

    params = (
        ("tipoFundo", "1"),
        ("cnpjFundo", cnpj),
        ("idCategoriaDocumento", "6"),
        ("idTipoDocumento", "40"),
        ("idEspecieDocumento", "0"),
        ("situacao", "A"),
        ("dataInicial", "01/10/2020"),
        ("dataFinal", "23/12/2020"),
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
