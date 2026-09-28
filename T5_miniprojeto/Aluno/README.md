# Mini-Projeto Avaliativo (M1S07) — Análise Exploratória da base Varejo

Projeto resolvido do curso **Análise de Dados com Python** (SENAI / LAB365), Turma T5, Módulo 1, Semana 07.
É uma Análise Exploratória de Dados (AED) da base **Varejo**, com 830 mil itens de compras reais, feita em Python com `csv` e Pandas: carregar, diagnosticar, limpar, validar, resumir e concluir.

## O que tem nesta pasta

| Arquivo | O que é |
|---|---|
| `notebook_colab_aluno.ipynb` | o projeto resolvido, passo a passo, com explicação antes e depois de cada célula |
| `dataset/varejo.csv` | a base Varejo (fonte: [Kaggle — Base Varejo](https://www.kaggle.com/datasets/namespaiva/base-varejo/data)) |
| `df_limpo.csv` | **não vem pronto**: é criado quando você executa o notebook (Passo 13) |

## Como executar

**No VS Code (recomendado)**

1. Baixe o repositório da turma (botão **Code → Download ZIP** no GitHub) e descompacte.
2. No VS Code: **File → Open Folder** → escolha a pasta `T5_miniprojeto/Aluno`.
3. Abra `notebook_colab_aluno.ipynb`, clique em **Select Kernel** e escolha o Python 3 instalado.
4. Clique em **Run All**. O notebook todo leva cerca de 1 minuto.

A primeira célula instala as bibliotecas. Se preferir fazer isso pelo terminal:

```bash
pip install pandas matplotlib
```

**No Google Colab**

1. Abra o `notebook_colab_aluno.ipynb` no Colab (**Arquivo → Fazer upload de notebook**).
2. Execute a célula do Passo 0.2 e envie o arquivo `dataset/varejo.csv` quando a janela abrir.
3. Execute as outras células, de cima para baixo.

## As etapas do projeto

| Passo | Etapa |
|---|---|
| 1 | leitura nativa com `csv.DictReader`: colunas, registros e categorias vazias |
| 2 | leitura com Pandas: formato, colunas e tipos (`info()`) |
| 3 | diagnóstico: nulos por coluna, duplicatas e `#N/D` |
| 4 | remoção das 4 colunas 100% vazias (`dropna(axis=1, how="all")`) |
| 5 | categoria vazia vira `"Sem Categoria"` com uma função `if/else` |
| 6 | remoção de 96.553 linhas duplicadas (`drop_duplicates()`) |
| 7 | data de texto para data com o módulo `datetime` (`strptime`) |
| 8 | regra de negócio: cada `CO_ID` é 1 compra, de 1 cliente, em 1 data |
| 9 | estatísticas do número de filhos (`CL_FHL`), calculadas por cliente |
| 10 a 12 | agrupamentos por gênero, categoria (com gráfico) e ano |
| 13 | gravação e conferência do `df_limpo.csv` |
| 14 | relatório final e conclusões geradas pelo código |

## Reflexão: ETL e qualidade de dados

Uma AED é a primeira parte de um processo de **ETL** (*Extract, Transform, Load*): o dado é **extraído** da fonte (o CSV), **transformado** (limpo, tipado e validado) e **carregado** num destino confiável (o `df_limpo.csv`, pronto para um banco de dados ou para o Power BI). A qualidade do resultado depende da qualidade dessa transformação.

Esta base mostra por que o diagnóstico vem antes da limpeza. O `isna()` diz que as colunas reais não têm nenhum nulo, mas 3.650 itens têm a categoria `#N/D`, um texto que a planilha de origem usou para "não disponível". Sem olhar os valores, esse problema passaria despercebido, e um `fillna()` não trataria nada. O mesmo vale para as duplicatas: sem uma coluna de quantidade, não há como saber se uma linha repetida é erro ou uma segunda unidade do produto. Toda decisão de limpeza precisa ser registrada, porque ela muda o resultado da análise.

## Conclusões

1. **ALIMENTOS** é a categoria mais vendida, com 52,4% dos itens: é o carro-chefe do varejo.
2. O gênero **F** fez mais compras no total, mas também tem mais clientes; por cliente, a frequência é quase igual (F = 18,5 e M = 18,4 compras).
3. O cliente típico **não tem filhos**: 52,7% dos 1.000 clientes têm 0 filho (mediana 0, moda 0); a média de 1,14 fica acima porque poucos clientes têm 3 ou 4 filhos.
4. O movimento por dia **cresceu**: de 50,9 compras por dia em 2019 para 62,5 em 2022. Comparar totais por ano engana, porque cada ano tem uma quantidade diferente de dias registrados.
5. Cada `CO_ID` é uma compra com 1 cliente e 1 data (18.471 compras, média de 39,7 itens): contar linhas é contar itens, e não compras.
6. **Problemas remanescentes:** não há coluna de quantidade nem de valor, as datas não cobrem todos os dias do ano, e 3.228 itens continuam "Sem Categoria" até o cadastro de produtos ser corrigido na origem.

---
*Prof. Especialista Cláudio F. Neves*
