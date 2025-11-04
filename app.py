import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

# Configuração básica do Flask
app = Flask(__name__, static_folder='static', template_folder='templates')
# Chave em variável de ambiente, conforme boas práticas 12 factors
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

# Caminho absoluto do arquivo de dados (importante para o Render)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "complaints.json")


# -----------------------------
# Funções auxiliares
# -----------------------------
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


# -----------------------------
# Rotas
# -----------------------------
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


@app.route('/complaints')
def complaints():
    complaints = sorted(load_complaints(), key=lambda x: x['created_at'], reverse=True)
    return render_template('complaints.html', complaints=complaints)

@app.route('/api/complaints')
def api_complaints():
    return jsonify(load_complaints())

@app.route("/report")
def relatorio():

    '''
    Página de relatório de análise de sentimento.
    Renderiza o arquivo 'templates/report.html'.
    '''
    

    return render_template("relatorio.html")



# -----------------------------
# Execução
# -----------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render define a porta automaticamente
    app.run(host='0.0.0.0', port=port)
