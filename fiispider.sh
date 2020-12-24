#!/bin/bash

if [[ $# -ne 1 ]]; then
  echo "$0: entre com o CNPJ"
  exit 4
fi

cnpj=`tr -dc '0-9' <<< $1`

curl -g -k -H "Accept:application/json" -X GET \
"https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?tipoFundo=1&cnpjFundo=${cnpj}&idCategoriaDocumento=6&idTipoDocumento=40&idEspecieDocumento=0&situacao=A&dataInicial=01/01/2020&dataFinal=23/12/2020&_=1608729063621&d=0&s=0&l=14" > /tmp/x

scrapy runspider --nolog fiispider.py -a ids=`cat /tmp/x | jq '.data[] | .id' | tr '\n' ','`
