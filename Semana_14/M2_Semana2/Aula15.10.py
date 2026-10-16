import pandas as pd
import math
import matplotlib.pyplot as plt

df = pd.read_csv('vendas.csv')

print('--Duplicatas--')
print(df[df.duplicated(keep=False)]) #mostrar as linhas repetidas, keep=false para mostrar as duas cópias

print('\n--Valores faltantes no desconto ou na avaliacao--')
print(df[df['desconto_pct'].isna() | df['avaliacao_cliente'].isna()]) #verificando as linhas que tem valores faltantes tanto no quesito dewsconto, quanto no avaliação
faltantes = df[df['desconto_pct'].isna() | df['avaliacao_cliente'].isna()]
print(f'Total de valores faltantes: {len(faltantes)}')

print("\n--Outlier valor>2000--")
print(df[df['valor_venda']>2000])

print('\n1. Raio-x do dataset')
print(f'Linhas: {df.shape[0]}  |  Colunas: {df.shape[1]}')
df.info()

print('\n2. Valores faltando por coluna')
nulos = df.isna().sum()
print(nulos[nulos > 0])

print('\n3. Linhas duplicadas')
df.duplicated().sum()
print(f'Quantidade: {df.duplicated().sum()}')
print(df[df.duplicated(keep=False)])

print('\n4. Maiores vendas')
print(df.sort_values('valor_venda', ascending=False).head(25))

valores = [1,5,5,2,4]
media = sum(valores)/len(valores)
print(f'\nMédia: {media}')

print(df['quantidade'].mean())
print(df['valor_venda'].mean())
print(df['valor_venda'].median())
print(df['valor_venda'].std())
print(df['valor_venda'].quantile(0.25))
print(df['valor_venda'].quantile(0.75))
print(df['valor_venda'].describe().round(2))

Q1 = df['valor_venda'].quantile(0.25)
Q3 = df['valor_venda'].quantile(0.75)
IQR = Q3 - Q1
print(f'\nIQR: {IQR}')

limite_superior = Q3 + 1.5 * IQR
df[df['valor_venda'] > limite_superior].shape[0]
print(f'\nLimite Superior: {limite_superior}')

#df.boxplot(column='valor_venda')
#df.boxplot(column='valor_venda', vert=False)
#plt.show()

df['valor_venda'].hist(bins=36)
plt.show()