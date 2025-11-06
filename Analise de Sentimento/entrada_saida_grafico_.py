
import pandas as pd
from transformers import pipeline
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from zoneinfo import ZoneInfo
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import re
import emoji

# --- Configurações ---
## Arquivo CSV retirado localmente
NOME_ARQUIVO_CSV = 'analise_sentimento_alimentos.csv'
COLUNA_AVALIACOES = 'Comentário_Consumidor'

""" ## Retirada do arquivo pelo Google Drive
NOME_ARQUIVO_CSV = '/content/drive/MyDrive/quotes2.csv'  # Troque pelo nome real do seu arquivo
COLUNA_AVALIACOES = 'Quote'     # Troque pelo nome real da coluna com o texto
"""

# --- Geração Dinâmica do Nome do Arquivo PDF ---
try:
    fuso_horario_sp = ZoneInfo("America/Sao_Paulo")
    agora_com_fuso = datetime.now(fuso_horario_sp)
except Exception:
    agora_com_fuso = datetime.now()

timestamp = agora_com_fuso.strftime("%d-%m-%Y_%H-%M")
NOME_ARQUIVO_PDF = f'relatorio_sentimento_{timestamp}.pdf'

# --- Configurações da Logomarca ---
CAMINHO_LOGOMARCA = 'logo_soulcare.png'  # Atualize com o caminho correto da logomarca

""" ----- Logomarca online (Google Drive) -----
CAMINHO_LOGOMARCA = '/content/drive/MyDrive/cachorro.jpeg' #Alterado / carlos
LARGURA_LOGOMARCA = 100  # Largura em pontos (ajuste conforme necessário)
ALTURA_LOGOMARCA = 40    # Altura em pontos (ajuste conforme necessário)
"""

LARGURA_LOGOMARCA = 40
ALTURA_LOGOMARCA = 40

# ###############################################################
# --- REGISTRO DE FONTE COM SUPORTE A EMOJI ---
# ###############################################################

"""--- Emoji fonte do Google Drive ---
CAMINHO_FONTE_EMOJI = '/content/drive/MyDrive/DejaVuSans.ttf'
FONTE_PADRAO = 'Helvetica'
FONTE_PADRAO_NEGRITO = 'Helvetica-Bold'
"""

CAMINHO_FONTE_EMOJI = 'DejaVuSans.ttf'
FONTE_PADRAO = 'Helvetica'
FONTE_PADRAO_NEGRITO = 'Helvetica-Bold'

try:
    if os.path.exists(CAMINHO_FONTE_EMOJI):
        pdfmetrics.registerFont(TTFont('DejaVuSans', CAMINHO_FONTE_EMOJI))
        FONTE_PADRAO = 'DejaVuSans'
        FONTE_PADRAO_NEGRITO = 'DejaVuSans'
        print(f"Fonte com suporte a emoji '{FONTE_PADRAO}' registrada com sucesso.")
    else:
        print(f"!!!!!!!!!!!!!! AVISO !!!!!!!!!!!!!!")
        print(f"Fonte de emoji em '{CAMINHO_FONTE_EMOJI}' NÃO FOI ENCONTRADA.")
        print("Por favor, baixe 'DejaVuSans.ttf' e faça upload para seu Google Drive.")
        print("Rodando com fontes padrão. Emojis NÃO serão exibidos no PDF.")
except Exception as e:
    print(f"AVISO: Erro ao registrar fonte de emoji: {e}")
# ###############################################################


# --- Configurações para os DOIS Modelos Transformers ---
MODELO_TEXTO_NOME = "nlptown/bert-base-multilingual-uncased-sentiment"
MODELO_EMOJI_NOME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Carrega Modelo 1 (Para Texto)
print(f"Carregando o modelo de TEXTO: {MODELO_TEXTO_NOME}...")
pipeline_texto = pipeline(
    "sentiment-analysis",
    model=MODELO_TEXTO_NOME,
    tokenizer=MODELO_TEXTO_NOME,
    device=-1
)
print("Modelo de TEXTO carregado.")

# Carrega Modelo 2 (Para Emojis)
print(f"Carregando o modelo de EMOJI: {MODELO_EMOJI_NOME}...")
pipeline_emoji = pipeline(
    "sentiment-analysis",
    model=MODELO_EMOJI_NOME,
    tokenizer=MODELO_EMOJI_NOME,
    device=-1
)
print("Modelo de EMOJI carregado.")


# 1. Leitura do Arquivo CSV
try:
    df = pd.read_csv(NOME_ARQUIVO_CSV, engine='python', on_bad_lines='skip', sep=None)
    texts_to_analyze = df[COLUNA_AVALIACOES].astype(str).tolist()
    print(f"Arquivo '{NOME_ARQUIVO_CSV}' lido com sucesso. Total de {len(df)} avaliações.")
except FileNotFoundError:
    print(f"ERRO: Arquivo '{NOME_ARQUIVO_CSV}' não encontrado.")
    exit()
except KeyError:
    print(f"ERRO: A coluna '{COLUNA_AVALIACOES}' não foi encontrada no arquivo CSV.")
    exit()

# 2. Aplicação da Análise de Sentimento (AMBOS OS MODELOS)
print("Iniciando a análise de sentimento com AMBOS os modelos...")
texts_to_analyze = [str(text) for text in texts_to_analyze]
resultados_texto = pipeline_texto(texts_to_analyze)
resultados_emoji = pipeline_emoji(texts_to_analyze)
print("Análise de sentimento concluída.")

# 3. Processamento dos Resultados e Inserção no DataFrame

# --- Função 1: Para o modelo 'nlptown' (Texto) ---
def formatar_nlptown(resultado):
    label = resultado['label']
    score = resultado['score']
    try:
        estrelas = int(label.split(' ')[0])
    except ValueError:
        estrelas = 3

    if estrelas >= 4: sentimento = 'Positivo'
    elif estrelas <= 2: sentimento = 'Negativo'
    else: sentimento = 'Neutro'
    return sentimento, estrelas, score

# --- Função 2: Para o modelo 'cardiffnlp' (Emoji) ---
def formatar_cardiffnlp(resultado):
    label = resultado['label'].lower()
    score = resultado['score']
    if label == 'positive':
        sentimento, estrelas = 'Positivo', 5
    elif label == 'negative':
        sentimento, estrelas = 'Negativo', 1
    else: # 'neutral'
        sentimento, estrelas = 'Neutro', 3
    return sentimento, estrelas, score

# Processa resultados do Modelo 1 (Texto)
df_res_texto = pd.DataFrame(resultados_texto)
df_res_texto[['Sentimento_Texto', 'Estrelas_Texto', 'Confianca_Texto']] = df_res_texto.apply(
    lambda row: pd.Series(formatar_nlptown(row)), axis=1
)

# Processa resultados do Modelo 2 (Emoji)
df_res_emoji = pd.DataFrame(resultados_emoji)
df_res_emoji[['Sentimento_Emoji', 'Estrelas_Emoji', 'Confianca_Emoji']] = df_res_emoji.apply(
    lambda row: pd.Series(formatar_cardiffnlp(row)), axis=1
)

# Junta tudo no DataFrame principal
df = pd.concat([
    df,
    df_res_texto[['Sentimento_Texto', 'Estrelas_Texto', 'Confianca_Texto']],
    df_res_emoji[['Sentimento_Emoji', 'Estrelas_Emoji', 'Confianca_Emoji']]
], axis=1)

# ###############################################################
# --- NOVO: LÓGICA DE DECISÃO (Emoji vs Texto) ---
# ###############################################################
# ... (Presumindo que seu DataFrame 'df' e a 'COLUNA_AVALIACOES' já existem) ...

def escolher_melhor_analise(row):
    texto = str(row[COLUNA_AVALIACOES])
    contagem_emoji = emoji.emoji_count(texto)
    comprimento_texto = len(texto)

    # Nova lógica:
    # Usa o modelo de TEXTO (nlptown) se:
    # 1. NÃO houver emojis (contagem_emoji == 0)
    #    OU
    # 2. O texto tiver 3 ou mais caracteres (comprimento_texto >= 3)
    if (contagem_emoji == 0) or (comprimento_texto >= 3):
        # Se NÃO tem emoji, OU se o texto é longo o suficiente,
        # usa o resultado do modelo 'nlptown'
        return pd.Series([
            row['Sentimento_Texto'],
            row['Estrelas_Texto'],
            row['Confianca_Texto'],
            'M_Texto (nlptown)' # Modelo escolhido
        ])
    else:
        # Caso contrário (ou seja, TEM emoji E o texto é MUITO CURTO < 3),
        # usa o resultado do modelo 'cardiffnlp' (casos como "👍", "😞")
        return pd.Series([
            row['Sentimento_Emoji'],
            row['Estrelas_Emoji'],
            row['Confianca_Emoji'],
            'M_Emoji (Cardiff)' # Modelo escolhido
        ])

# Aplica a lógica para criar as colunas FINAIS
df[['Sentimento', 'Estrelas_Preditas', 'Confianca', 'Modelo_Escolhido']] = df.apply(
    escolher_melhor_analise, axis=1
)

# Aplica a lógica para criar as colunas FINAIS
df[['Sentimento', 'Estrelas_Preditas', 'Confianca', 'Modelo_Escolhido']] = df.apply(
    escolher_melhor_analise, axis=1
)
# ###############################################################


# 4. Exibição da Contagem de Sentimentos (agora baseada na coluna final)
contagem_sentimentos = df['Sentimento'].value_counts(normalize=True).mul(100).round(2).astype(str) + '%'
print("\n--- Distribuição de Sentimentos (Resultado Final) ---")
print(contagem_sentimentos)
print("\n--- Modelos Usados ---")
print(df['Modelo_Escolhido'].value_counts(normalize=True).mul(100).round(2).astype(str) + '%')

# 5. Preparação e Exportação para PDF (ReportLab)

# (Funções myFirstPage e myLaterPages não mudam, elas já usam as variáveis FONTE_PADRAO)
def myFirstPage(canvas, doc):
    canvas.saveState()
    page_width, page_height = A4
    canvas.setFont(FONTE_PADRAO_NEGRITO, 10)
    header_text = f"Soulcare - Grupo 4"
    
    # Configurando e desenhando a logomarca no cabeçalho
    try:
        header_picture = Image(CAMINHO_LOGOMARCA, width=50, height=50)
        header_picture.drawOn(canvas, doc.leftMargin, page_height - 0.75 * inch)  # Posiciona a logo
    except Exception as e:
        print(f"Aviso: Não foi possível carregar a logo no cabeçalho: {e}")
    
    canvas.drawCentredString(page_width / 2, page_height - 0.5 * inch, header_text)
    canvas.line(doc.leftMargin, page_height - 0.7 * inch, page_width - doc.rightMargin, page_height - 0.7 * inch)
    canvas.setFont(FONTE_PADRAO, 8)
    #footer_text = "Página %d" % doc.page ## O numero da página no rodapé não exibe
    footer_lines = ["R. Dois, 2877 - Vila Operaria, Rio Claro - SP, 13504-090",  
    "e-mail: soulcare.fatecrc@gmail.com"] #endereço no rodapé
    ## footer_text = "Página %d" % doc.page, f"R. Dois, 2877 - Vila Operaria, Rio Claro - SP, 13504-090"
    for i, line in enumerate(footer_lines):
        canvas.drawCentredString(page_width / 2, 0.5 * inch - i * 10, line)
    canvas.line(doc.leftMargin, 0.7 * inch, page_width - doc.rightMargin, 0.7 * inch)
    canvas.restoreState()

def myLaterPages(canvas, doc):
    canvas.saveState()
    page_width, page_height = A4
    canvas.setFont(FONTE_PADRAO_NEGRITO, 10)
    header_text = f"Relatório de Análise de Sentimento"
    canvas.drawCentredString(page_width / 2, page_height - 0.5 * inch, header_text)
    canvas.line(doc.leftMargin, page_height - 0.7 * inch, page_width - doc.rightMargin, page_height - 0.7 * inch)
    canvas.setFont(FONTE_PADRAO, 8)
    footer_text = "Página %d" % doc.page ## rodapé com numeração
    canvas.drawCentredString(page_width / 2, 0.5 * inch, footer_text)
    canvas.line(doc.leftMargin, 0.7 * inch, page_width - doc.rightMargin, 0.7 * inch)
    canvas.restoreState()


print(f"\nGerando o arquivo PDF '{NOME_ARQUIVO_PDF}'...")

doc = SimpleDocTemplate(
    NOME_ARQUIVO_PDF,
    pagesize=A4,
    topMargin=1.0 * inch,
    bottomMargin=1.0 * inch
)
elements = []
styles = getSampleStyleSheet()

# Aplica a fonte padrão aos estilos
styles['Title'].fontName = FONTE_PADRAO
styles['h2'].fontName = FONTE_PADRAO
styles['Normal'].fontName = FONTE_PADRAO

try:
    logomarca = Image(CAMINHO_LOGOMARCA, width=LARGURA_LOGOMARCA, height=ALTURA_LOGOMARCA)
    logomarca.hAlign = 'RIGHT'
    elements.append(logomarca)
    elements.append(Spacer(1, 6))
except Exception as e:
    print(f"AVISO: Erro ao carregar a logomarca: {e}")

# Título do Relatório (atualizado)
elements.append(Paragraph("Relatório de análise de sentimento", styles['Title']))
# elements.append(Paragraph("Relatório de Análise de Sentimento (Híbrido)", styles['Title']))
# elements.append(Paragraph(f"Modelo de Texto: {MODELO_TEXTO_NOME}", styles['Normal'])) ## ocultando essa informação
# elements.append(Paragraph(f"Modelo de Emoji: {MODELO_EMOJI_NOME}", styles['Normal'])) ## ocultando essa informação
elements.append(Paragraph(f"Total de avaliações analisadas: {len(df)}", styles['Normal']))
elements.append(Spacer(1, 12))



# (Tabela de Resumo e Gráfico de Pizza não mudam, já usam a coluna 'Sentimento')
contagem_absoluta = df['Sentimento'].value_counts().sort_index()
# ... (código do gráfico e tabela de resumo) ...
# Tabela de Resumo (Contagem)
resumo_data = [['Sentimento', 'Contagem', 'Percentual']]
for sent in contagem_absoluta.index:
    count = contagem_absoluta[sent]
    percent = df['Sentimento'].value_counts(normalize=True).mul(100).round(2).loc[sent]
    resumo_data.append([sent, count, f"{percent}%"])

t_resumo = Table(resumo_data)
t_resumo.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6A5ACD')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTNAME', (0, 0), (-1, 0), FONTE_PADRAO_NEGRITO),
    ('FONTNAME', (0, 1), (-1, -1), FONTE_PADRAO),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Centralizando todas as células
    ('ALIGN', (0, 1), (0, -1), 'LEFT'),     # Mantendo primeira coluna alinhada à esquerda
]))

# --- Geração do Gráfico de Pizza ---
drawing = Drawing(400, 200)
pie = Pie()
pie.x = -20
pie.y = -150
pie.width = 300
pie.height = 300
pie.data = contagem_absoluta.values.tolist()
pie.labels = [f'{s}: {v}' for s, v in contagem_absoluta.items()]
pie.sideLabels = True
pie.slices.strokeWidth = 0.5
pie.slices.popout = 5

color_map = {
    'Positivo': colors.darkgreen,
    'Negativo': colors.darkred,
    'Neutro': colors.darkblue
}
for i, label in enumerate(contagem_absoluta.index):
    pie.slices[i].fillColor = color_map.get(label, colors.grey)

legend = Legend()
legend.x = 220
legend.y = pie.y
legend.alignment = 'left'
legend.colorNamePairs = list(zip([color_map.get(l, colors.grey) for l in contagem_absoluta.index], contagem_absoluta.index))
legend.fontName = FONTE_PADRAO
legend.fontSize = 8

resumo_grafico_data = [
    [t_resumo], [drawing]
]

resumo_grafico_table = Table(resumo_grafico_data, colWidths=[250, 250])  # Distribuição igual do espaço
resumo_grafico_table.hAlign = 'CENTER'  # Centraliza a tabela na página

drawing.add(pie)
drawing.add(legend)




# Também vamos centralizar o título
styles['h2'].alignment = 1  # 1 = TA_CENTER (centralizado)

elements.append(Paragraph("Resumo e distribuição de sentimentos", styles['h2']))
elements.append(resumo_grafico_table)
elements.append(Spacer(1, 24))


elements.append(PageBreak()) # Quebra de página antes da tabela detalhada

# --- Tabela Detalhada (MODIFICADA para incluir a coluna 'Modelo_Escolhido') --
comment_style = ParagraphStyle(
    name='CommentStyle',
    parent=styles['Normal'],
    fontName=FONTE_PADRAO,
    fontSize=7,
    leading=9,
    alignment=TA_LEFT,
)

# Seleciona as colunas para o PDF, incluindo a nova 'Modelo_Escolhido'
# df_pdf = df[[COLUNA_AVALIACOES, 'Sentimento', 'Estrelas_Preditas', 'Confianca', 'Modelo_Escolhido']]
df_pdf = df[[COLUNA_AVALIACOES, 'Sentimento', 'Estrelas_Preditas', 'Confianca']]

# Define os estilos dos Parágrafos
header_style = ParagraphStyle(name='HeaderStyle', parent=styles['Normal'], fontName=FONTE_PADRAO_NEGRITO, fontSize=8, alignment=TA_CENTER)
cell_style = ParagraphStyle(name='CellStyle', parent=styles['Normal'], fontName=FONTE_PADRAO, fontSize=7, alignment=TA_CENTER)
center_cell_style = ParagraphStyle(name='CenterCellStyle', parent=cell_style, alignment=TA_CENTER)

# Cabeçalho (Modificado)
header = [
    Paragraph(COLUNA_AVALIACOES, header_style),
    Paragraph('Sentimento', header_style),
    Paragraph('Estrelas', header_style),
    Paragraph('Confiança', header_style),
    #Paragraph('Modelo Usado', header_style) # Nova Coluna
]

data_rows = []
for row in df_pdf.values.tolist():
    comment_text = str(row[0])
    comment = Paragraph(comment_text, comment_style) # Suporta emojis

    data_rows.append([
        comment,
        Paragraph(str(row[1]), cell_style),
        Paragraph(str(row[2]), center_cell_style),
        Paragraph(f"{float(row[3]):.2f}", center_cell_style),
        #Paragraph(str(row[4]), cell_style) # Nova Coluna
    ])

data_list = [header] + data_rows

# Define as larguras das colunas (Modificado)
doc_width = A4[0] - 2 * doc.leftMargin
# col_widths = [doc_width * 0.40, doc_width * 0.15, doc_width * 0.10, doc_width * 0.10, doc_width * 0.25]
col_widths = [doc_width * 0.40, doc_width * 0.15, doc_width * 0.10, doc_width * 0.15,]

table = Table(data_list, colWidths=col_widths)

style = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E90FF')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
])
table.setStyle(style)

elements.append(Paragraph("Detalhes da Análise por Avaliação", styles['h2']))
elements.append(table)

# Constrói o PDF
try:
    doc.build(
        elements,
        onFirstPage=myFirstPage,
        onLaterPages=myLaterPages
    )
    print(f"Sucesso! Relatório exportado para '{NOME_ARQUIVO_PDF}'.")
except Exception as e:
    print(f"\n--- ERRO AO GERAR O PDF ---")
    print(f"ERRO: {e}")
    print("Verifique se o arquivo 'DejaVuSans.ttf' está no local correto no seu Google Drive.")
