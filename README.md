# 🤖 Análise de Sentimento Híbrida em Comentários de Clientes

## 🌟 Visão Geral do Projeto

Este projeto demonstra um pipeline completo de **Web Scraping**, **Análise de Sentimento** e **Geração de Relatórios** para monitorar a percepção dos usuários sobre um serviço ou produto.

O objetivo principal é capturar comentários de um website de reclamações (ou similar), analisar o sentimento (positivo, negativo, neutro) expresso e, em seguida, gerar um relatório detalhado em PDF com resumos e uma visão gráfica da distribuição dos sentimentos.

## 🚀 Funcionalidades

* **Web Scraping Automático:** Captura dados de comentários (descrição e autor) de uma página web específica (`https://projas.onrender.com/complaints`) utilizando a biblioteca `BeautifulSoup`.
* **Análise de Sentimento Híbrida:** Utiliza o poder da biblioteca `Hugging Face Transformers` com dois modelos de Processamento de Linguagem Natural (PLN) de última geração para classificação de sentimento:
    * **Modelo de Texto (`nlptown/bert-base-multilingual-uncased-sentiment`):** O modelo principal, ideal para textos mais longos.
    * **Modelo de Emoji (`cardiffnlp/twitter-roberta-base-sentiment-latest`):** Usado como fallback em casos de comentários muito curtos (ex: "👍") ou puramente emoji, onde a análise textual é limitada.
* **Geração de Relatório em PDF:** Emite um relatório profissional utilizando `ReportLab`, contendo:
    * Título, Logomarca e informações do projeto.
    * Um **Gráfico de Setores** (Pizza) que exibe a distribuição percentual dos sentimentos (Positivo, Negativo, Neutro).
    * Uma **Tabela de Resumo** com contagens e percentuais.
    * Uma **Tabela Detalhada** com cada comentário original, o sentimento predito e o score de confiança.

## 🛠️ Tecnologias Utilizadas

* **Python:** Linguagem de programação principal.
* **Web Scraping:** `requests`, `BeautifulSoup` (para extração dos dados).
* **Análise de Dados:** `pandas` (para manipulação e processamento de dados).
* **PLN/Análise de Sentimento:** `Hugging Face Transformers` (para carregamento e uso dos modelos pré-treinados).
* **Geração de PDF/Gráficos:** `ReportLab` (para criação do relatório e visualização de dados).
* **Web Framework:** `Flask` (Usado para a aplicação que hospeda os comentários e o frontend do relatório).

## 📂 Estrutura do Projeto
├── app.py # Aplicação Flask (Frontend/Backend do site de reclamações) 
├── Web Scraping.py # Script para Web Scraping 
├── entrada_saida_grafico_.py # Script principal de Análise de Sentimento e Geração de PDF 
├── complaints.json # Arquivo de armazenamento dos comentários (usado pelo Flask) 
├── analise_sentimento_alimentos.csv # Exemplo de arquivo de entrada (se usado localmente) 
├── logo_soulcare.png # Logomarca para o relatório 
├── DejaVuSans.ttf # Fonte com suporte a Emojis para o PDF (necessária para ReportLab) 
├── quotes.csv # CSV gerado pelo Web Scraping 
  └── README.md # Este arquivo

## ⚙️ Como Executar

### Pré-requisitos

1.  **Python 3.x** instalado.
2.  Crie um ambiente virtual (recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    .\venv\Scripts\activate   # Windows
    ```

### Instalação de Dependências

Instale todas as bibliotecas necessárias.
**Pacote completo**
pip install -r requirements.txt

**Ou manualmente:**
```bash
pip install pandas transformers requests beautifulsoup4 reportlab pillow zoneinfo-py flask
