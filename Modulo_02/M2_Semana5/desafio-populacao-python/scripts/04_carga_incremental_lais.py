
import importlib.util
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ============================================================
# 1. CONFIGURAÇÕES DO PROJETO
# ============================================================

# Define o diretório raiz do projeto.
# __file__ representa o caminho deste próprio arquivo Python.
# resolve() transforma o caminho em absoluto.
# parent.parent sobe dois níveis na estrutura de diretórios.
ROOT = Path(__file__).resolve().parent.parent

# Carrega as variáveis de ambiente do arquivo .env.
# Isso permite armazenar informações sensíveis fora do código.
load_dotenv(ROOT / ".env")

# Recupera a senha do banco de dados armazenada no .env.
DB_PASSWORD = os.environ["DB_PASSWORD"]

# String de conexão com o PostgreSQL.
# localhost = banco na máquina local.
# 5433 = porta configurada para o PostgreSQL.
# ibge = nome do banco de dados.
CONEXAO_POSTGRES = (
    f"postgresql+psycopg2://postgres:{DB_PASSWORD}@localhost:5433/ibge"
)

# Identificação do pipeline ETL.
NOME_PIPELINE = "etl_populacao_brasil"

# Ano da estimativa populacional que estamos processando.
ANO_ESTIMATIVA = 2026


# ============================================================
# 2. IMPORTAÇÃO DINÂMICA DO MÓDULO DE TRANSFORMAÇÃO
# ============================================================

# Localiza o arquivo Python responsável pela transformação
# dos dados, sem precisar importar o módulo pelo nome tradicional.
_spec = importlib.util.spec_from_file_location(
    "transformar",
    ROOT / "scripts" / "02_transformar_lais.py"
)

# Cria um módulo Python a partir da especificação encontrada.
transformar = importlib.util.module_from_spec(_spec)

# Executa o código do módulo e disponibiliza suas funções.
# Assim podemos reutilizar as funções de extração e transformação.
_spec.loader.exec_module(transformar)


# ============================================================
# 3. IDENTIFICAR ESTADOS COM POPULAÇÃO ALTERADA
# ============================================================

def estados_com_populacao_alterada(
    df_unificado: pd.DataFrame,
    engine
) -> pd.DataFrame:

    # CONSULTA AO BANCO DE DADOS
    # --------------------------------------------------------

    # Busca a população atualmente vigente na dimensão SCD2.
    # O filtro registro_atual = true garante que estamos
    # comparando com a versão atual de cada estado.
    #
    # O alias "populacao_vigente" renomeia a coluna populacao
    # apenas no resultado da consulta, facilitando a comparação.
    #
    # SELECT é uma operação de leitura: não altera o banco.
    vigente = pd.read_sql(
        """
        SELECT
            sigla,
            populacao AS populacao_vigente
        FROM dw_populacao.dim_estado_scd2
        WHERE registro_atual = true
        """,
        engine
    )

    # MERGE DOS DATAFRAMES
    # --------------------------------------------------------

    # Junta os dados recém-extraídos com os dados vigentes
    # no banco, utilizando a sigla como chave de relacionamento.
    #
    # how="left":
    # Mantém todos os registros do DataFrame da esquerda
    # (df_unificado), mesmo que não exista correspondência
    # no DataFrame vigente.
    #
    # Isso permite identificar também estados que ainda
    # não possuem registro correspondente no banco.
    comparado = df_unificado.merge(
        vigente,
        on="sigla",
        how="left"
    )

    # COMPARAÇÃO DOS VALORES
    # --------------------------------------------------------

    # Compara a população recém-extraída de 2026 com a
    # população atualmente registrada no banco.
    #
    # O operador != significa "diferente".
    # A comparação é realizada linha a linha e retorna
    # valores booleanos (True ou False).
    #
    # True  = população diferente.
    # False = população igual.
    #
    # Atenção: se populacao_vigente for nula (NaN),
    # a comparação também retornará True.
    # Nesse caso, pode ser um estado ainda não cadastrado.
    alterados = comparado[
        comparado["populacao_2026"] !=
        comparado["populacao_vigente"]
    ]

    # EXIBIÇÃO DO RESULTADO
    # --------------------------------------------------------

    # Informa quantos estados apresentaram divergência
    # em relação ao total de estados comparados.
    print(
        f"{len(alterados)} de {len(comparado)} "
        "estados tiveram a população alterada."
    )

    # Retorna somente as colunas necessárias para a próxima etapa.
    # A operação não altera o banco de dados.
    return alterados[
        [
            "id",
            "sigla",
            "nome",
            "regiao",
            "populacao_2026"
        ]
    ].copy()


# ============================================================
# 4. ATUALIZAR CONTROLE DO ETL
# ============================================================

def avancar_controle(engine):

    # Abre uma transação no banco de dados.
    # engine.begin() gerencia automaticamente o commit
    # caso tudo ocorra corretamente ou rollback em caso de erro.
    with engine.begin() as conn:

        # Executa um UPDATE na tabela de controle do ETL.
        #
        # Atualiza a data da última carga e identifica
        # qual pipeline realizou o processamento.
        #
        # :nome é um parâmetro vinculado (bind parameter),
        # preenchido pelo dicionário abaixo.
        conn.execute(
            text("""
                INSERT INTO dw_populacao.controle_etl (
                    nome_pipeline,
                    ultima_carga
                )
                VALUES (
                    :nome,
                    now()
                )
            """),
            {"nome": NOME_PIPELINE}
        )


# ============================================================
# 5. EXECUÇÃO PRINCIPAL DO PIPELINE
# ============================================================

if __name__ == "__main__":

    # Cria a conexão com o PostgreSQL.
    engine = create_engine(CONEXAO_POSTGRES)

    # ETAPA DE EXTRAÇÃO
    # --------------------------------------------------------

    # Extrai os dados populacionais de 2010 a partir de um CSV.
    populacao_2010 = (
        transformar.extrair_fontes.extrair_populacao_2010_csv()
    )

    # Extrai os dados cadastrais dos estados pela API.
    estados = transformar.extrair_fontes.extrair_estados_api()

    # Extrai os dados populacionais mais recentes da Wikipedia.
    populacao = (
        transformar.extrair_fontes.extrair_populacao_wikipedia()
    )

    # ETAPA DE TRANSFORMAÇÃO
    # --------------------------------------------------------

    # Integra as três fontes de dados em um único DataFrame.
    df_unificado = transformar.juntar_fontes(
        estados,
        populacao,
        populacao_2010
    )

    # ETAPA DE COMPARAÇÃO
    # --------------------------------------------------------

    # Compara os dados extraídos com os registros vigentes
    # no banco e retorna somente os estados com divergências.
    alterados = estados_com_populacao_alterada(
        df_unificado,
        engine
    )

    # Exibe a quantidade de estados com alterações.
    print(
        f"\n{len(alterados)} estado(s) com população alterada para {ANO_ESTIMATIVA}:"
    )

    # Exibe os estados identificados.
    print(
        alterados[
            ["sigla", "nome", "populacao_2026"]
        ]
    )

    # Orientação para a próxima etapa do exercício.
    print(
        "\nAgora use esses estados em sql/02_scd_tipo2_populacao.sql (Etapa 6) para fechar a versão 2022 e abrir a versão 2026."
    )

    # IMPORTANTE:
    # A função avancar_controle(engine) NÃO foi chamada aqui.
    # Ela executa um UPDATE no banco e, portanto,
    # deve ser utilizada somente na etapa apropriada do ETL.
