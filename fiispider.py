import scrapy
import locale
from reportids import getIDs

# https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?
# d=9&s=0&l=10&o[0][dataEntrega]=desc&tipoFundo=1&
# cnpjFundo=01201140000190&
# idCategoriaDocumento=6&idTipoDocumento=40&idEspecieDocumento=0&situacao=A&
# dataInicial=01/01/2020&
# dataFinal=23/12/2020&_=1608729063621

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


class FIISpider(scrapy.Spider):
    name = "fiispider"

    custom_settings = {"CONCURRENT_REQUESTS": "1"}

    def __init__(self, *args, **kwargs):
        super(FIISpider, self).__init__(*args, **kwargs)

        ids = getIDs(kwargs.get("cnpj"))
        if ids is None or len(ids) == 0:
            self.start_urls = [
                "https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id=131924",
                "https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id=127183",
                "https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id=133113",
            ]
        else:
            self.start_urls = []
            for id in ids:
                self.start_urls.append(
                    f"https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={id}",
                )

    def parse(self, response):
        relat = dict(
            nome={"name": "Nome do Fundo", "val": ""},
            cnpj={"name": "CNPJ do Fundo", "val": ""},
            competencia={"name": "Competência", "val": ""},
            cod={"name": "Código ISIN", "val": ""},
            num_cotistas={"name": "Número de cotistas", "val": 0},
            num_cotas={"name": "Número de Cotas Emitidas", "val": 0},
            ativo={"name": "Ativo – R$", "val": 0},
            invest_total={"name": "Total investido", "val": 0},
            invest_imov={"name": "Direitos reais sobre bens imóveis", "val": 0},
            valor_a_receber={"name": "Valores a Receber", "val": 0},
            alugueis={"name": "Contas a Receber por Aluguéis", "val": 0},
            passivo={"name": "Total do passivo", "val": 0},
            pl={"name": "Patrimônio Líquido – R$", "val": 0},
            rendimentos={"name": "Rendimentos a distribuir", "val": 0},
            taxa_adm={"name": "Taxa de administração a pagar", "val": 0},
            taxa_perf={"name": "Taxa de performance a pagar", "val": 0},
        )

        print("\n-----+\n")

        for row in response.xpath("//tr"):
            line = row.css("td *::text").extract()

            for item in relat:
                ret = valFromTitle(line, relat[item]["name"])
                if ret is not None:
                    relat[item]["val"] = ret

        if relat["num_cotas"]["val"] != 0:
            print(
                f"{'Aluguéis/Cota':30.30s} | {relat['valor_a_receber']['val']/relat['num_cotas']['val']:0.3f}"
            )
            print(
                f"{'Rendimentos/Cota':30.30s} | {relat['rendimentos']['val']/relat['num_cotas']['val']:0.3f}"
            )
            print(
                f"{'Taxas/Cota':30.30s} | {(relat['taxa_adm']['val']+relat['taxa_perf']['val'])/ relat['num_cotas']['val']:0.3f}"
            )

        if relat["rendimentos"]["val"] != 0:
            print(
                f"{'Taxas/Rendimentos':30.30s} | {100*(relat['taxa_adm']['val']+relat['taxa_perf']['val'])/ relat['rendimentos']['val']:0.3f}%"
            )

        for key, item in relat.items():
            if key == "nome" or key == "cnpj":
                continue
            if key == "cod":
                print(item["val"][2:6] + "11", end=";")
                continue
            if type(item["val"]) is float or type(item["val"]) is int:
                print(locale.format("%.3f", item["val"], True), end=";")
            else:
                print(f"{item['val']}", end=";")


def valFromTitle(row, title):
    """
    title_str: title string
    """
    # locale.setlocale(locale.LC_ALL, "Portuguese_Brazil.1252")
    for i, val in enumerate(row):
        if title == "Ativo – R$" and title in val and i + 3 < len(row):
            v = row[i + 3].strip()
            print(f"{row[i].strip():30.30s} | {v}")
            try:
                return locale.atof(v)
            except Exception:
                return v

        if title in val and i + 1 < len(row):
            v = row[i + 1].strip()
            print(f"{row[i].strip():30.30s} | {v}")
            try:
                return locale.atof(v)
            except Exception:
                return v

    return None


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
