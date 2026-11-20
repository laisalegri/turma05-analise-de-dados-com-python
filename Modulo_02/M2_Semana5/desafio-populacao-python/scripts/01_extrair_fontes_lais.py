"""
Desafio -- Etapa 1: extração. Mesma lógica que a professora acabou de
mostrar na Vitrine (scripts/01_extrair_fontes.py), com as MESMAS 3 fontes
(CSV, API, Scraping) -- só que aqui CSV e API vêm da Vitrine em miniatura,
e API/Scraping são fontes públicas DE VERDADE, não mocks.

Fonte 1 -- CSV (análoga ao vendas.csv/produtos.csv da Vitrine, slide 10):
    raw/populacao_2010.csv -- o Censo 2010, já pronto num arquivo. Não
    precisamos buscar isso de novo: é histórico, não muda. Igual à Vitrine
    com os CSVs dela, é só ler.

Fonte 2 -- API (análoga à API de produtos da Vitrine, slide 13):
    GET https://servicodados.ibge.gov.br/api/v1/localidades/estados
    Devolve uma lista de 27 objetos, um por estado + DF, no formato:
        {"id": 35, "sigla": "SP", "nome": "São Paulo",
         "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"}}

Fonte 3 -- Web Scraping (análoga ao preço do concorrente, slide 15):
    A página da Wikipédia "Lista de unidades federativas do Brasil por
    população" tem uma tabela (classe "wikitable") com uma linha por estado:
    nome do estado e colunas de população de 2026 (estimativa) e 2022
    (Censo), com um espaço especial (NBSP, "\xa0") como separador de milhar
    em boa parte dos números (ex.: "44\xa0411\xa0238").

    Atenção, pegadinha real: a Wikipédia devolve HTTP 403 (bloqueado) para
    requisições sem um User-Agent próprio -- o requests padrão é tratado
    como robô. Por isso USER_AGENT_WIKIPEDIA abaixo já vem definido; use-o
    em headers=USER_AGENT_WIKIPEDIA no requests.get().

Rode com:  python3 scripts/01_extrair_fontes.py
"""
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"

URL_API_ESTADOS = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
URL_WIKIPEDIA_POPULACAO = "https://pt.wikipedia.org/wiki/Lista_de_unidades_federativas_do_Brasil_por_popula%C3%A7%C3%A3o"
USER_AGENT_WIKIPEDIA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"}


def extrair_populacao_2010_csv() -> pd.DataFrame:
   pop = pd.read_csv(RAW / "populacao_2010.csv", sep=",", encoding="utf-8")
   print(f"\n------------------------------------------------------")
   print(f"Extraindo do CSV:")
   print(f"------------------------------------------------------")
   print(pop.head(5))
   print(f"\nO arquivo CSV populacao_2010.csv tem {len(pop)} linhas.")
   return pop



def extrair_estados_api() -> pd.DataFrame:
   resposta = requests.get(URL_API_ESTADOS, timeout=30)
   resposta.raise_for_status()
   estados_api = pd.DataFrame(resposta.json())
   estados_api["regiao"] = estados_api["regiao"].apply(lambda x: x["nome"])
   estados_api = estados_api[["id", "sigla", "nome", "regiao"]]
   print(f"------------------------------------------------------")
   print(f"Extraindo da API:")
   print(f"------------------------------------------------------")
   print(estados_api.head(5))
   print(f"\nNa API do IBGE retorna {len(estados_api)} estados.")
   return estados_api

def extrair_populacao_wikipedia() -> pd.DataFrame:
    response = requests.get(
        URL_WIKIPEDIA_POPULACAO,
        timeout=30,
        headers=USER_AGENT_WIKIPEDIA
    )
    response.encoding = 'utf-8'
    html = BeautifulSoup (response.text, "html.parser")
    tabela = html.find("table", {"class": "wikitable"})
    linhas = tabela.select("tr")[2:]
    dados = []
    for tr in linhas:
       celulas = tr.find_all(["th", "td"])
       estado = celulas[0].get_text(strip=True)
       if estado == "Total":
          continue
       pop_2026 = int(celulas[1].get_text(strip=True).replace("\xa0","").replace(" ", ""))
       pop_2022 = int(celulas[2].get_text(strip=True).replace("\xa0","").replace(" ", ""))
       dados.append({"estado": estado, "populacao_2022": pop_2022, "populacao_2026": pop_2026})
    df = pd.DataFrame(dados)
    print(f"------------------------------------------------------")
    print(f"Extraindo via Webscraping:")
    print(f"------------------------------------------------------")
    print(df.head(5))
    print(f"\nNa Wikipedia retorna {len(df)} estados.")
    print(f"\n------------------------------------------------------")
    return df



if __name__ == "__main__":
    populacao_2010 = extrair_populacao_2010_csv()
    estados = extrair_estados_api()
    populacao = extrair_populacao_wikipedia()
