import scrapy
import locale
from reportids import getMonthlyIDs
import re

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

        self.csv = []
        self.run_num = 0
        self.cnpj = kwargs.get("cnpj")
        self.n = kwargs.get("n")

    def start_requests(self):
        monthlyIDs = getMonthlyIDs(self.cnpj, self.n)
        for id in monthlyIDs:
            yield scrapy.Request(
                f"https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={id}",
                self.parse,
            )

    def closed(self, reason):
        print("\n*****")
        print("\n".join(self.csv))

    def parse(self, response):
        relat = dict(
            nome={"name": "Nome do Fundo:", "val": ""},
            cnpj={"name": "CNPJ do Fundo:", "val": ""},
            competencia={"name": "Competência:", "val": ""},
            cod={"name": "Código ISIN:", "val": ""},
            num_cotistas={"name": "Número de cotistas", "val": 0},
            num_cotas={"name": "Número de Cotas Emitidas", "val": 0},
            ativo={"name": "Ativo – R$", "val": 0},
            caixa={"name": "Total mantido para as Necessidades de Liquidez", "val": 0},
            invest_total={"name": "Total investido", "val": 0},
            invest_imov={"name": "Direitos reais sobre bens imóveis", "val": 0},
            valor_a_receber={"name": "Valores a Receber", "val": 0},
            alugueis={"name": "Contas a Receber por Aluguéis", "val": 0},
            passivo={"name": "Total do passivo", "val": 0},
            pl={"name": "Patrimônio Líquido", "val": 0},
            rendimentos={"name": "Rendimentos a distribuir", "val": 0},
            taxa_adm={"name": "Taxa de administração a pagar", "val": 0},
            taxa_perf={"name": "Taxa de performance a pagar", "val": 0},
        )

        print("\n-----\n")

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
                    f(relat["pl"]["val"]),
                    f(relat["ativo"]["val"]),
                    f(relat["invest_imov"]["val"]),
                    f(relat["invest_total"]["val"] - relat["invest_imov"]["val"]),
                    f(relat["caixa"]["val"]),
                    f(relat["valor_a_receber"]["val"]),
                    f(relat["alugueis"]["val"]),
                    f(relat["passivo"]["val"]),
                    f(relat["rendimentos"]["val"]),
                    f(relat["taxa_adm"]["val"] + relat["taxa_perf"]["val"]),
                ]
            )
        )

        self.run_num += 1
        if self.run_num == len(self.start_urls):
            print("*** Dividendos ***")

            cod = relat["cod"]["val"]
            yield scrapy.Request(
                f"http://bvmf.bmfbovespa.com.br/Fundos-Listados/FundosListadosDetalhe.aspx?"
                f"Sigla={cod}&tipoFundo=Imobiliario&aba=abaEventosCorporativos&idioma=pt-br",
                callback=self.parseDividends,
            )

    def parseDividends(self, response):
        table = response.xpath(
            "//table[@id='ctl00_contentPlaceHolderConteudo_ucEventosCorporativos_grdDividendo_ctl01']//tr"
        )
        for row in table:
            print(row.css("td *::text").extract().strip())


def valFromTitle(row, title):
    # locale.setlocale(locale.LC_ALL, "Portuguese_Brazil.1252")
    for i, val in enumerate(row):
        val = val.strip()
        if title == "Ativo – R$" and title in val and i + 3 < len(row):
            v = row[i + 3].strip()
            print(f"{row[i].strip():30.30s} | {v}")
            try:
                return locale.atof(v)
            except Exception:
                return v

        if re.match(rf"^[\w\r\n]*{title}", val, re.IGNORECASE) and i + 1 < len(row):
            v = row[i + 1].strip()
            print(f"{row[i].strip():30.30s} | {v}")
            try:
                return locale.atof(v)
            except Exception:
                return v

    return None


def f(number):
    try:
        return str(locale.format("%.3f", number, True))
    except Exception:
        return str(number)
