
import pandas as pd
import requests
from bs4 import BeautifulSoup

url = 'https://www.adorocinema.com/filmes/numero-cinemas/'

headers = {
    'User-agent':(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36'
    )
}

response = requests.get(url, headers=headers)
response.encoding= 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')
filmes = soup.find_all ('div', attrs={'class': 'card entity-card entity-card-list cf'})


dados = []

for filme in filmes:
    titulo_tag = filme.find('a', attrs={'class': 'meta-title-link'})
    genero_tag = filme.find('span', attrs={'class': 'dark-grey-link'})
    direcao_tag = filme.find('div', attrs={'class': 'meta-body-direction'})

    titulo = titulo_tag.text.strip() if titulo_tag else 'Título não encontrado'
    genero = genero_tag.text.strip() if genero_tag else 'Genero não encontrado'
    direcao = direcao_tag.text.strip() if direcao_tag else 'Direção não encontrado'

    print(f"Titulo: {titulo} | Gênero: {genero} | Direção: {direcao}")

    dados.append({
        'titulo': titulo,
        'genero': genero,
        'direcao': direcao
    } )

df = pd.DataFrame(dados)
df.to_excel('filmes.xlsx', index=False)
print(df)
print(f'{len(df)} filmes exportados')