import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

DATA_FILE = "complaints.json"

def load_complaints():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_complaints(complaints):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(complaints, f, ensure_ascii=False, indent=2)

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

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)
