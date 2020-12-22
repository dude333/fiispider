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
            # clean = [l.encode("utf-8").strip() for l in line]
            # print(clean[0].decode('ascii') + ": " + clean[1].decode('ascii'))
            # print(u' '.join(clean).encode('utf-8').strip())
            # print(u"|".join([l.strip() for l in line]))
            # if len(line) >= 2:
            #     print(f"{line[0].strip()}\t|\t{line[1].strip()}")
            # else:
            #     print(f"{line[0].strip()}")
            if len(line) >= 2 and "Competência" in line[0]:
                print(f"{line[0].strip()}\t|\t{line[1].strip()}")
            valFromTitle(line, "Competência", 0, 1)


def valFromTitle(row, title_str, title_col, val_col):
    """
    title_str: title string
    title_col: position from title on row array
    val_col:   position from value on row array
    """
    if len(row) >= max(title_col, val_col) and title_str in row[title_col]:
        print(f"{row[title_col].strip()}\t|\t{row[val_col].strip()}")


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
