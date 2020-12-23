import scrapy
import locale


class BlogSpider(scrapy.Spider):
    name = "blogspider"
    start_urls = [
        "https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id=131924",
        "https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id=127183",
        "https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id=133113",
    ]

    def parse(self, response):
        rendimentos = 0
        valor_a_receber = 0
        num_cotas = 0
        taxa_adm = 0
        taxa_perf = 0

        print("\n-----\n")

        for row in response.xpath("//tr"):
            line = row.css("td *::text").extract()

            valFromTitle(line, "Nome do Fundo")
            valFromTitle(line, "CNPJ do Fundo")
            valFromTitle(line, "Competência")
            valFromTitle(line, "Código ISIN")
            valFromTitle(line, "Número de cotistas")
            if num_cotas == 0:
                num_cotas = valFromTitle(line, "Número de Cotas Emitidas")
            valFromTitle(line, "Ativo – R$")
            valFromTitle(line, "Total investido")
            valFromTitle(line, "Direitos reais sobre bens imóveis")
            if valor_a_receber == 0:
                valor_a_receber = valFromTitle(line, "Valores a Receber")
            valFromTitle(line, "Contas a Receber por Aluguéis")
            valFromTitle(line, "Total do passivo")
            valFromTitle(line, "Patrimônio Líquido – R$")
            if rendimentos == 0:
                rendimentos = valFromTitle(line, "Rendimentos a distribuir")
            if taxa_adm == 0:
                taxa_adm = valFromTitle(line, "Taxa de administração a pagar")
            if taxa_perf == 0:
                taxa_perf = valFromTitle(line, "Taxa de performance a pagar")

        if num_cotas != 0:
            print(f"{'Aluguéis/Cota':30.30s} | {valor_a_receber/num_cotas:0.3f}")
            print(f"{'Rendimentos/Cota':30.30s} | {rendimentos/num_cotas:0.3f}")
            print(f"{'Taxas/Cota':30.30s} | {(taxa_adm+taxa_perf)/ num_cotas:0.3f}")

        if rendimentos != 0:
            print(
                f"{'Taxas/Rendimentos':30.30s} | {100*(taxa_adm+taxa_perf)/ rendimentos:0.3f}%"
            )


def valFromTitle(row, title):
    """
    title_str: title string
    """
    # locale.setlocale(locale.LC_ALL, "Portuguese_Brazil.1252")
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
    for i, val in enumerate(row):
        if title == "Ativo – R$" and title in val and i + 3 < len(row):
            print(f"{row[i].strip():30.30s} | {row[i+3].strip()}")
            try:
                return locale.atof(row[i + 3].strip())
            except Exception:
                return 0.0

        if title in val and i + 1 < len(row):
            print(f"{row[i].strip():30.30s} | {row[i+1].strip()}")
            try:
                return locale.atof(row[i + 1].strip())
            except Exception:
                return 0.0

    return 0.0


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
