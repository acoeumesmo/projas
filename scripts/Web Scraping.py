from bs4 import BeautifulSoup
import requests
from csv import writer
url = 'https://projas.onrender.com/complaints'
result = requests.get(url)
soup = BeautifulSoup(result.text, 'html.parser')


with open('quotes.csv', 'w', newline='', encoding='utf-8')as f:
    thewriter = writer(f)
    #pegando os dados
    for p in soup.find_all('p'):
        texto = p.get_text()
    for h5 in soup.find_all('h5'):
        autor = h5.get_text()
    formataçao = [ autor,  texto]
    thewriter.writerow(formataçao)
