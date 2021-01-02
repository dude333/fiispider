import scrapy
import locale
from reportids import getMonthlyIDs, getDividendIDs
import re

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


class FIISpider(scrapy.Spider):
    name = "fiispider"

    custom_settings = {"CONCURRENT_REQUESTS": "1"}

    def __init__(self, *args, **kwargs):
        super(FIISpider, self).__init__(*args, **kwargs)

        self.monthly = dict()
        self.dividends = dict()
        self.cnpj = kwargs.get("cnpj")
        self.n = kwargs.get("n")

    def start_requests(self):
        monthlyIDs = getMonthlyIDs(self.cnpj, self.n)
        for id in monthlyIDs:
            yield scrapy.Request(
                f"https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={id}",
                self.parse,
            )

        dividendIDs = getDividendIDs(self.cnpj, self.n)
        for id in reversed(dividendIDs):
            yield scrapy.Request(
                f"https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={id}",
                self.parseDividends,
            )

    def closed(self, reason):
        print("\n*****")

        for competencia in self.monthly:
            cod = self.monthly[competencia][0]  # 0 = codigo
            provento = "-"
            if competencia in self.dividends:
                if (
                    len(self.dividends[competencia]) >= 2
                    and self.dividends[competencia][0] == cod
                ):
                    provento = self.dividends[competencia][1]

            # De código ISIN para código do papel: BRHABTCTF001 => HABT11
            self.monthly[competencia][0] = self.monthly[competencia][0][2:6] + "11"
            # Imprime a linha com os itens separados por ";"
            print(competencia, ";".join(self.monthly[competencia]), provento, sep=";")

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

        self.monthly[relat["competencia"]["val"]] = [
            relat["cod"]["val"],
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

    def parseDividends(self, response):
        relat = dict(
            cod={"name": "Código ISIN da cota:", "val": ""},
            provento={"name": "Valor do provento por cota", "val": ""},
            mes={"name": "Período de referência", "val": ""},
            ano={"name": "Ano", "val": ""},
        )

        print("\n-----\n")

        for row in response.xpath("//tr"):
            line = row.css("td *::text").extract()

            for item in relat:
                ret = valFromTitle(line, relat[item]["name"])
                if ret is not None:
                    if item == "mes":
                        ret = fixMonth(ret)
                    relat[item]["val"] = ret

        competencia = f"{relat['mes']['val']:02d}/{relat['ano']['val']:04.0f}"
        self.dividends[competencia] = [
            relat["cod"]["val"],
            f(relat["provento"]["val"]),
        ]


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


def fixMonth(month):
    if type(month) == int or type(month) == float or month.isnumeric():
        return int(month)

    try:
        return [
            "janeiro",
            "fevereiro",
            "março",
            "abril",
            "maio",
            "junho",
            "julho",
            "agosto",
            "setembro",
            "outubro",
            "novembro",
            "dezembro",
        ].index(month.lower()) + 1
    except ValueError:
        return fixMonth(month[0:2])
