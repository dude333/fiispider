import scrapy
import locale


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
            valFromTitle(line, "Número de Cotas Emitidas")
            valFromTitle(line, "Ativo – R$")
            valFromTitle(line, "Total investido")
            valFromTitle(line, "Direitos reais sobre bens imóveis")
            valFromTitle(line, "Valores a Receber")
            valFromTitle(line, "Contas a Receber por Aluguéis")
            valFromTitle(line, "Total do passivo")
            valFromTitle(line, "Patrimônio Líquido – R$")
            valFromTitle(line, "Rendimentos a distribuir")
            valFromTitle(line, "Taxa de administração a pagar")
            valFromTitle(line, "Taxa de performance a pagar")


def valFromTitle(row, title):
    """
    title_str: title string
    """
    # locale.setlocale(locale.LC_ALL, "pt_BR.UTF8")
    for i, val in enumerate(row):
        if title == "Ativo – R$" and title in val and i + 3 < len(row):
            print(f"{row[i].strip():30.30s} | {row[i+3].strip()}")
            try:
                return locale.atoi(row[i + 3].strip())
            except ValueError:
                return 0

        if title in val and i + 1 < len(row):
            print(f"{row[i].strip():30.30s} | {row[i+1].strip()}")
            try:
                return locale.atoi(row[i + 1].strip())
            except ValueError:
                return 0


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
