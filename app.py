import subprocess
import pandas as pd
import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from analise.entrada import analise_sentimento

# Configuração básica do Flask
app = Flask(__name__, static_folder='static', template_folder='templates')
# Chave em variável de ambiente, conforme boas práticas 12 factors
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

# Caminho absoluto do arquivo de dados (importante para o Render)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "complaints.json")


# Funções auxiliares
def load_complaints():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_complaints(complaints):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(complaints, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar complaints: {e}")


# Rotas
@app.route('/')
def index():
    return render_template('index.html')

    

@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form.get('nome', '').strip()
    email = request.form.get('email', '').strip()
    descricao = request.form.get('descricao', '').strip()

    if not nome or not email or not descricao:
        flash('Preencha todos os campos obrigatórios!', 'danger')
        return redirect(url_for('index'))

    complaint = {
        "id": int(datetime.utcnow().timestamp() * 1000),
        "nome": nome,
        "email": email,
        "descricao": descricao,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    complaints = load_complaints()
    complaints.append(complaint)
    save_complaints(complaints)

    flash('Reclamação enviada com sucesso!', 'success')
    return redirect(url_for('index'))


#  Endpoint para o ESP8266
@app.route('/api/submit-esp', methods=['POST'])
def submit_esp():
    data = request.get_json()

    if not data or "nome" not in data or "descricao" not in data:
        return jsonify({"erro": "Campos obrigatórios: nome, descricao"}), 400

    complaint = {
        "id": int(datetime.utcnow().timestamp() * 1000),
        "nome": data["nome"],
        "email": "esp8266@device",  # opcional — apenas para manter compatibilidade
        "descricao": data["descricao"],
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    complaints = load_complaints()
    complaints.append(complaint)
    save_complaints(complaints)

    return jsonify({"status": "ok", "recebido": complaint}), 200



@app.route('/complaints')
def complaints():
    complaints = sorted(load_complaints(), key=lambda x: x['created_at'], reverse=True)
    return render_template('complaints.html', complaints=complaints)

@app.route('/api/complaints')
def api_complaints():
    return jsonify(load_complaints())


#rota scraping/analise

RESULTADOS = []   # variável global para o front-end acessar
RESULTADOS_PDF = [] # variável global para o front-end acessar

@app.route("/admin/run-analysis", methods=["GET","POST"])
@app.route("/admin/run-analysis/", methods=["GET","POST"])
def run_analysis():
    try:
        # 1. Rodar o Web Scraping (um script externo)
        result = subprocess.run(
            ["python", "analise/webscraping.py"],
            check=True,
            capture_output=True,
            text=True
        )
        print("WEB SCRAPING:", result.stdout)

    except subprocess.CalledProcessError as e:
        return jsonify({
            "success": False,
            "error": "Erro ao executar webscraping.py",
            "details": e.stderr
        }), 500
    try:
        
        # 2. Rodar a análise de sentimento (função Python interna)
        pdf_path, df = analise_sentimento()
        global RESULTADOS_PDF
        RESULTADOS_PDF = pdf_path

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro na função analise_sentimento()",
            "details": str(e)
        }), 500
    try:
        # 3. Converter para dicionário para enviar ao front-end
        global RESULTADOS
        RESULTADOS = df.to_dict(orient="records")

        return jsonify({
            "success": True,
            "pdf": pdf_path,
            "total_registros": len(RESULTADOS)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro ao preparar dados para o front-end",
            "details": str(e)
        }), 500


@app.route("/relatorio")
def relatorio():
    return render_template("relatorio.html")

@app.route("/api/relatorio-data")
def relatorio_data():
    return jsonify({"items": RESULTADOS}) 

@app.route("/download-pdf")
def download_pdf():
    pdf_dir = os.getcwd()
    pdf_file = RESULTADOS_PDF  # variável global salva após análise

    if not os.path.exists(os.path.join(pdf_dir, pdf_file)):
        return "Arquivo PDF não encontrado.", 404

    return send_from_directory(
        pdf_dir,
        pdf_file,
        as_attachment=True
    )

    

# Execução
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render define a porta automaticamente
    app.run(host='0.0.0.0', port=port)
