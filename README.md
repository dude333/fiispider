# FIISpider
Programa para coleta de Informes Mensais de Fundos de Investimento Imobiliários (FIIs).

## Como Usar

## Baixar o programa

```
git clone https://github.com/dude333/fiispider.git
```

### Instalar as dependências
```
cd fiispider
pip install --user -r requirements.txt
```

### Extraír o relatório dos últimos n meses de um fundo
```
./run.py <CNPJ> <n>
```

#### Exemplo
```
./run.py 24.960.430/0001-13 6
```
Coleta os dados dos últimos 6 relatórios

## Formato do Relatório

A saída é dividida em duas partes

### Tabela
```
Nome do Fundo:                 | KINEA ÍNDICES DE PREÇOS FUNDO DE INVESTIMENTO IMOBILIÁRIO - FII
CNPJ do Fundo:                 | 24.960.430/0001-13
Código ISIN:                   | BRKNIPCTF001
Competência:                   | 11/2020
Número de cotistas             | 28.629
Ativo – R$                     | 4.320.095.375,05
Patrimônio Líquido – R$        | 4.274.528.605,10
Número de Cotas Emitidas       | 40.589.764,0000
Total mantido para as Necessid | 504.822.271,50
Total investido                | 3.815.266.193,02
Direitos reais sobre bens imóv | 0,00
Valores a Receber              | 6.910,53
Rendimentos a distribuir       | 40.589.935,00
Taxa de administração a pagar  | 3.355.850,92
Total do passivo               | 45.566.769,95
Aluguéis/Cota                  | 0.000
Rendimentos/Cota               | 1.000
Taxas/Cota                     | 0.083
Taxas/Rendimentos              | 8.268%
```

### CSV (para importar no Excel)
```
11/2020;KNIP11;abl;40.589.764,000;28.629,000;reajuste;vacância;inadimplência;4.320.095.375,050;0,000;3.815.266.193,020;504.822.271,500;6.910,530;0,000;45.566.769,950;4.274.528.605,100;40.589.935,000;3.355.850,920
```

#### Redefinição do formato do CSV
Para alterar o formato do csv, basta editar esta parte dentro da função **parse**, do arquivo **fiispyder.py**:

```
# Print CSV
self.csv.append(
    ";".join(
        [
            relat["competencia"]["val"],
            relat["cod"]["val"][2:6] + "11",
            "abl",
            f(relat["num_cotas"]["val"]),
            f(relat["num_cotistas"]["val"]),
            "reajuste",
            "vacância",
            "inadimplência",
            f(relat["ativo"]["val"]),
            f(relat["invest_imov"]["val"]),
            f(relat["invest_total"]["val"] - relat["invest_imov"]["val"]),
            f(relat["caixa"]["val"]),
            f(relat["valor_a_receber"]["val"]),
            f(relat["alugueis"]["val"]),
            f(relat["passivo"]["val"]),
            f(relat["pl"]["val"]),
            f(relat["rendimentos"]["val"]),
            f(relat["taxa_adm"]["val"] + relat["taxa_perf"]["val"]),
        ]
    )
)
```

## Como funciona

1. O arquivo **run.py** lê os parâmetros da linha de comando, CNPJ e número de meses a serem lidos, e chama a classe **FIISpider**.
1. A classe **FIISpider** é executada, que então chama a função **getIDs(cnpj, n)** (reportids.py), que busca os IDs dos relatórios mensais do FII dado pelo CNPJ.
1. A classe **FIISpider** faz a coleta dos dados mensais com base no ID do relatório.