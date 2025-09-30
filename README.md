# autoU_email_ai_project

## 📌 Objetivo do Projeto
Este projeto foi desenvolvido como parte de um desafio técnico para a **AutoU**.  
O objetivo é automatizar a **leitura, classificação e sugestão de respostas** para e-mails recebidos por uma empresa do setor financeiro, que lida diariamente com um alto volume de mensagens.

Com isso, a equipe de suporte ganha tempo, evitando gastar esforço humano em e-mails repetitivos, improdutivos ou sem necessidade de ação imediata.

---

## ⚙️ Funcionalidades
1. **Upload ou inserção de texto de e-mails** (`.txt` ou `.pdf`).
2. **Classificação automática** dos e-mails em:
   - **Produtivo** → requerem uma ação/resposta (ex.: solicitações de suporte, dúvidas).
   - **Improdutivo** → não requerem ação imediata (ex.: felicitações, agradecimentos).
3. **Sugestão de resposta automática**, gerada pela IA em português.
4. **Fallback local** caso a API de IA não esteja disponível.
5. **Interface Web simples e intuitiva**, construída com Flask + Bootstrap.

---

## 🏗️ Arquitetura do Projeto
```
autoU_email_ai_project/
│── app.py              # Backend Flask: define rotas e integra lógica
│── utils.py            # Integração com Google GenAI (classificação + resposta)
│── templates/
│   ├── index.html      # Página inicial com formulário de upload/inserção
│   └── result.html     # Exibição da categoria e resposta sugerida
│── static/
│   └── style.css       # Estilo da interface
│── requirements.txt    # Dependências do projeto
```

## 🔹 Diagrama da Arquitetura

```
erDiagram
    APP ||--o{ ROUTES : registra
    ROUTES ||--o{ UTILS : chama
    ROUTES ||--o{ TEMPLATES : renderiza
    UTILS ||--o{ GENAI : chama_api

    APP {
        string app.py
        int MAX_CONTENT_LENGTH
        bool debug
    }
    ROUTES {
        string main_routes.py
        string /
        string /process
    }
    UTILS {
        string utils.py
        func allowed_file()
        func extract_text_from_file()
        func generate_response()
    }
    GENAI {
        string client GenAI
        string model_name
        float confidence
        string reply
    }
    TEMPLATES {
        string index.html
        string result.html
    }

```
---

### 🔹 Fluxo de funcionamento
1. Usuário acessa a **página inicial** e envia um e-mail (texto ou arquivo).
2. O backend (`app.py`) processa o conteúdo:
   - Extrai o texto (`utils.py`).
   - Usa o **Google GenAI (Gemini)** como classificador simples inicial.
   - Envia o texto para o `generate_response()` (`utils.py`), que consulta a **Google GenAI (Gemini)**.
3. A resposta e classificação retornam e são exibidas no `result.html`.

---

## 🚀 Como Executar Localmente
### 1. Clonar o repositório
```bash
git clone https://github.com/Gabriel1000000/autoU_email_ai_project.git
cd autoU_email_ai_project
```

### 2. Criar ambiente virtual e instalar dependências
- criar a venv
```bash
python -m venv venv
```
- Ativar a venv no windows
```bash
venv\Scripts\activate   # Windows
```
- Ativar a venv no Linux/Mac
```bash
source venv/bin/activate  # Linux/Mac
```

- Instalação das dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variável de ambiente da API
Obtenha uma chave no [Google AI Studio](https://aistudio.google.com/).  
Depois configure:

-  Windows
```bash
set GEMINI_API_KEY="sua_api_key_aqui"   # Windows
```

- Linux/Mac
```bash
export GEMINI_API_KEY="sua_api_key_aqui" # Linux/Mac
```

### 4. Rodar a aplicação
```bash
python app.py
```

Acesse no navegador: [http://localhost:5000](http://localhost:5000)

---

## 🌐 Deploy na Nuvem
O projeto está hospedado em um serviço gratuito como:
- **Render** acesse no navegador: [https://autou-email-ai-project.onrender.com/](https://autou-email-ai-project.onrender.com/)

---

## 📊 Tecnologias Utilizadas
- **Python 3.11**
- **Flask** (backend web)
- **Bootstrap 5** (frontend responsivo)
- **Google Generative AI (Gemini)** para classificação e resposta
- **PyPDF2** (extração de texto de PDFs)

---

## 🎯 Conclusão
Este projeto demonstra uma **prova de conceito** de como Inteligência Artificial pode ser aplicada para **automatizar a triagem e resposta de e-mails corporativos**.  
Ele combina **classificação automática** + **resposta sugerida** em português, permitindo maior eficiência no atendimento e liberando a equipe para tarefas mais estratégicas.

---
👨‍💻 Desenvolvido para o processo seletivo da **AutoU**.