import scrapy
from pprint import pprint


class BlogSpider(scrapy.Spider):
    name = "blogspider"
    start_urls = [
        "https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id=131924"
    ]

    def parse(self, response):
        for row in response.xpath("//tr"):
            line = row.css("td *::text").extract()
            valFromTitle(line, "Competência")
            valFromTitle(line, "Código ISIN")
            # clean = [l.encode("utf-8").strip() for l in line]
            # print(clean[0].decode('ascii') + ": " + clean[1].decode('ascii'))
            # print(u' '.join(clean).encode('utf-8').strip())
            # print(u"|".join([l.strip() for l in line]))
            # if len(line) >= 2:
            #     print(f"{line[0].strip()}\t|\t{line[1].strip()}")
            # else:
            #     print(f"{line[0].strip()}")


def valFromTitle(row, title):
    """
    title_str: title string
    """
    for i, val in enumerate(row):
        if title in val and i + 1 < len(row):
            print(f"{row[i].strip()}\t|\t{row[i+1].strip()}")


# Competência
# Cód.
# ABL (m²)
# Cotas
# Núm. Cotistas
# Reajuste
# Vacância
# "Inadimplência"
# Ativos
# Ativos Imóveis
# Ativos Invest.
# Caixa
# A Receber
# Aluguéis
# Passivos
# PL
# Rend. Distr.
# Tx. Adm.
# Aluguéis/ Cota
# Rend./ Cota
# Tx. Adm. / Rend. Distr.
