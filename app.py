import os
from flask import Flask, render_template, request
from utils import generate_response, allowed_file, extract_text_from_file

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8 MB

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    text = ""
    if request.form.get('email_text'):
        text = request.form['email_text'].strip()

    file = request.files.get('email_file')
    if file and file.filename != '':
        if not allowed_file(file.filename):
            return "Formato de arquivo não permitido. Use .txt ou .pdf", 400
        try:
            text = extract_text_from_file(file)
        except Exception as e:
            return f"Erro ao extrair texto do arquivo: {e}", 500

    if not text:
        return "Nenhum texto recebido para processar.", 400
    
    category_hint = 0.0

    result = generate_response(text, category_hint=category_hint)
    if isinstance(result, tuple) and len(result) == 4:
        category, score, suggestion, ai_used = result
    elif isinstance(result, tuple) and len(result) == 3:
        category, score, suggestion = result
        ai_used = False
    elif isinstance(result, dict):
        category = result.get('category', category_hint or 'Improdutivo')
        score = result.get('confidence', 0.0)
        suggestion = result.get('reply', '')
        ai_used = result.get('ai_used', False)
    else:
        category, score, suggestion, ai_used = (category_hint or "Improdutivo", 0.0, str(result), False)

    return render_template('result.html',
                           text=text,
                           category=category,
                           score=score,
                           suggestion=suggestion,
                           ai_used=ai_used)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
