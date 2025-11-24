import pandas as pd
from transformers import pipeline
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
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
#os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
#os.environ["CUDA_VISIBLE_DEVICES"] = ""
import re
import emoji

# Modularização pra poder funcionar no flask
def analise_sentimento():

    # Configurações
    ## Arquivo CSV retirado localmente 
    NOME_ARQUIVO_CSV = 'quotes.csv'
    COLUNA_AVALIACOES = 'Texto'

    # Nome dinâmico do PDF
    try:
        fuso_horario_sp = ZoneInfo("America/Sao_Paulo")
        agora_com_fuso = datetime.now(fuso_horario_sp)
    except Exception:
        agora_com_fuso = datetime.now()

    timestamp = agora_com_fuso.strftime("%d-%m-%Y_%H-%M")
    NOME_ARQUIVO_PDF = f'relatorio_sentimento_{timestamp}.pdf'

    # Logomarca
    CAMINHO_LOGOMARCA = 'logo_soulcare.png'
    LARGURA_LOGOMARCA = 40
    ALTURA_LOGOMARCA = 40

    # Fonte Emoji
    CAMINHO_FONTE_EMOJI = 'DejaVuSans.ttf'
    FONTE_PADRAO = 'Helvetica'
    FONTE_PADRAO_NEGRITO = 'Helvetica-Bold'

    if os.path.exists(CAMINHO_FONTE_EMOJI):
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', CAMINHO_FONTE_EMOJI))
            FONTE_PADRAO = 'DejaVuSans'
            FONTE_PADRAO_NEGRITO = 'DejaVuSans'
        except:
            pass

    # Modelos Transformers
    MODELO_TEXTO_NOME = "nlptown/bert-base-multilingual-uncased-sentiment"
    MODELO_EMOJI_NOME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

    pipeline_texto = pipeline(
        "sentiment-analysis",
        model=MODELO_TEXTO_NOME,
        tokenizer=MODELO_TEXTO_NOME,
        device=-1
    )

    pipeline_emoji = pipeline(
        "sentiment-analysis",
        model=MODELO_EMOJI_NOME,
        tokenizer=MODELO_EMOJI_NOME,
        device=-1
    )

    # Leitura do csv
    df = pd.read_csv(NOME_ARQUIVO_CSV, engine='python', on_bad_lines='skip', sep=None)
    texts_to_analyze = df[COLUNA_AVALIACOES].astype(str).tolist()

    # Aplica dois modelos
    resultados_texto = pipeline_texto(texts_to_analyze)
    resultados_emoji = pipeline_emoji(texts_to_analyze)

    # Formatação
    def formatar_nlptown(resultado):
        label = resultado['label']
        score = resultado['score']
        try:
            estrelas = int(label.split(' ')[0])
        except:
            estrelas = 3

        if estrelas >= 4:
            sentimento = 'Positivo'
        elif estrelas <= 2:
            sentimento = 'Negativo'
        else:
            sentimento = 'Neutro'

        return sentimento, estrelas, score

    def formatar_cardiffnlp(resultado):
        label = resultado['label'].lower()
        score = resultado['score']

        if label == 'positive':
            return 'Positivo', 5, score
        if label == 'negative':
            return 'Negativo', 1, score
        return 'Neutro', 3, score

    # Processa modelo 1
    df_res_texto = pd.DataFrame(resultados_texto)
    df_res_texto[['Sentimento_Texto', 'Estrelas_Texto', 'Confianca_Texto']] = df_res_texto.apply(
        lambda row: pd.Series(formatar_nlptown(row)), axis=1
    )

    # Processa modelo 2
    df_res_emoji = pd.DataFrame(resultados_emoji)
    df_res_emoji[['Sentimento_Emoji', 'Estrelas_Emoji', 'Confianca_Emoji']] = df_res_emoji.apply(
        lambda row: pd.Series(formatar_cardiffnlp(row)), axis=1
    )

    df = pd.concat([
        df,
        df_res_texto[['Sentimento_Texto', 'Estrelas_Texto', 'Confianca_Texto']],
        df_res_emoji[['Sentimento_Emoji', 'Estrelas_Emoji', 'Confianca_Emoji']]
    ], axis=1)

    # Lógica final
    def escolher_melhor_analise(row):
        texto = str(row[COLUNA_AVALIACOES])
        num_emojis = emoji.emoji_count(texto)

        texto_sem_emoji = emoji.replace_emoji(texto, '')
        texto_limpo = re.sub(r'[^a-zA-Z0-9]', '', texto_sem_emoji)
        num_letras = len(texto_limpo)

        if num_emojis > 0 and num_emojis > num_letras:
            return pd.Series([
                row['Sentimento_Emoji'],
                row['Estrelas_Emoji'],
                row['Confianca_Emoji'],
                "Emoji"
            ])
        else:
            return pd.Series([
                row['Sentimento_Texto'],
                row['Estrelas_Texto'],
                row['Confianca_Texto'],
                "Texto"
            ])
    # Aplica a nova lógica para criar as colunas FINAIS
    df[['Sentimento', 'Estrelas_Preditas', 'Confianca', 'Modelo_Escolhido']] = df.apply(
        escolher_melhor_analise,
        axis=1
    )

    
    # Salva pro dashboard
    df.to_csv("analise.csv", index=False, encoding="utf-8")

    # Gera o PDF
    # funções internas do PDF

    def myFirstPage(canvas, doc):
        canvas.saveState()
        page_width, page_height = A4
        canvas.setFont(FONTE_PADRAO_NEGRITO, 10)
        header_text = f"Soulcare - Grupo 4"

        try:
            header_picture = Image(CAMINHO_LOGOMARCA, width=40, height=40)
            header_picture.drawOn(canvas, doc.leftMargin, page_height - 0.75 * inch)
        except:
            pass

        canvas.drawCentredString(page_width / 2, page_height - 0.5 * inch, header_text)
        canvas.restoreState()

    def myLaterPages(canvas, doc):
        canvas.saveState()
        page_width, page_height = A4
        canvas.setFont(FONTE_PADRAO_NEGRITO, 10)
        canvas.drawCentredString(page_width / 2, page_height - 0.5 * inch,
                                 "Relatório de Análise de Sentimento")
        canvas.restoreState()

    # --- construção do PDF ---
    doc = SimpleDocTemplate(
        NOME_ARQUIVO_PDF,
        pagesize=A4,
        topMargin=1.0 * inch,
        bottomMargin=1.0 * inch
    )

    elements = []
    styles = getSampleStyleSheet()

    styles['Title'].fontName = FONTE_PADRAO

    elements.append(Paragraph("Relatório de análise de sentimento", styles['Title']))
    elements.append(Paragraph(f"Total de avaliações analisadas: {len(df)}", styles['Normal']))
    elements.append(Spacer(1, 12))

    contagem = df['Sentimento'].value_counts()

    resumo_data = [['Sentimento', 'Contagem']]
    for x, y in contagem.items():
        resumo_data.append([x, y])

    tabela = Table(resumo_data)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(tabela)
    elements.append(PageBreak())

    doc.build(elements, onFirstPage=myFirstPage, onLaterPages=myLaterPages)

    # Opcional: salva CSV consolidado para inspeção
    try:
        df.to_csv("analise.csv", index=False, encoding="utf-8")
    except Exception as e:
        print(f"AVISO: não foi possível salvar analise.csv: {e}")

    # Volta pro Flask: caminho do PDF + DataFrame
    return NOME_ARQUIVO_PDF, df
