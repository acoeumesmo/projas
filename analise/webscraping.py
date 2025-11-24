from bs4 import BeautifulSoup
import requests
from csv import writer
url = 'http://127.0.0.1:5000/complaints'  #'https://projas.onrender.com/complaints'
result = requests.get(url)
soup = BeautifulSoup(result.text, 'html.parser')

with open('quotes.csv', 'w', newline='', encoding='utf-8') as f:
    thewriter = writer(f)
    thewriter.writerow(['Autor', 'Texto'])  # cabeçalho

    # Coleta pares <h5> + <p> corretamente
    autores = soup.find_all('h5')
    textos = soup.find_all('p')

    # Faz o zip dos dois para juntar por posição
    for autor_tag, texto_tag in zip(autores, textos):
        autor = autor_tag.get_text(strip=True)
        texto = texto_tag.get_text(strip=True)
        thewriter.writerow([autor, texto])
