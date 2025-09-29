import os
import json
import re
from PyPDF2 import PdfReader

# -----------------------------
# Tentativa de importar SDK GenAI
# -----------------------------
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except Exception as e:
    print("[utils] google.genai não disponível:", e)
    GENAI_AVAILABLE = False

# -----------------------------
# Configurações gerais
# -----------------------------
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

# -----------------------------
# Funções de arquivo
# -----------------------------
def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_file(file):
    """
    Recebe um FileStorage (upload) e retorna string do conteúdo do arquivo.
    Suporta .txt e .pdf
    """
    ext = os.path.splitext(file.filename)[1].lower()
    file.stream.seek(0)

    if ext == ".txt":
        return file.read().decode("utf-8", errors="ignore")
    elif ext == ".pdf":
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()

    return ""

# -----------------------------
# Funções GenAI
# -----------------------------
def _get_genai_client():
    """
    Retorna um client genai configurado.
    Procura GEMINI_API_KEY ou GOOGLE_API_KEY no ambiente; se não houver, tenta ADC.
    """
    if not GENAI_AVAILABLE:
        return None

    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    try:
        if key:
            client = genai.Client(api_key=key)
            print("[utils] genai.Client criado com chave de API")
        else:
            client = genai.Client()
            print("[utils] genai.Client criado sem chave (ADC ou defaults)")
        return client
    except Exception as e:
        print("[utils] erro ao criar genai.Client:", e)
        return None


# Cria client GenAI uma vez
GENAI_CLIENT = _get_genai_client()


# -----------------------------
# Fallback local (quando GenAI não disponível)
# -----------------------------
def _local_fallback_reply(category_hint=None):
    """Retorna resposta pré-definida quando GenAI não está disponível."""
    if category_hint == 'Produtivo':
        return ("Produtivo",
                0.8,
                "Obrigado pelo contato. Recebemos sua mensagem e iremos analisar o caso. Se necessário, entraremos em contato solicitando informações adicionais.",
                False)
    else:
        return ("Improdutivo",
                0.7,
                "Agradecemos sua mensagem! No momento não é necessária nenhuma ação adicional. Se precisar de suporte, por favor abra um chamado específico pelo canal de atendimento.",
                False)


# -----------------------------
# Função principal de geração de resposta
# -----------------------------
def generate_response(text, category_hint=None):
    """
    Retorna (category: str, confidence: float, reply: str, ai_used: bool)
    Usa Google GenAI (Gemini) se disponível; caso contrário, retorna fallback local.
    """
    if not text or text.strip() == "":
        return _local_fallback_reply(category_hint)

    if GENAI_CLIENT is None:
        print("[generate_response] GenAI client não disponível — usando fallback local")
        return _local_fallback_reply(category_hint)

    try:
        print("[generate_response] Chamando Google Generative AI (genai)")

        prompt = f"""
Você é um classificador e gerador de respostas para e-mails corporativos em português.

REGRAS (use somente estas definições):
- Produtivo: email que REQUER UMA AÇÃO OU RESPOSTA ESPECÍFICA (ex.: solicitação de suporte técnico, pedido de atualização sobre um caso, solicitação de documentos, dúvida técnica que exige retorno).
- Improdutivo: email que NÃO REQUER AÇÃO IMEDIATA (ex.: felicitações, agradecimentos, mensagens informais sem pedido).

TAREFA:
1) Classifique o EMAIL abaixo em exatamente 'Produtivo' ou 'Improdutivo' conforme as regras.
2) Gere UMA resposta breve e profissional em português adequada à categoria (caso seja Improdutivo, a resposta pode ser uma confirmação curta ou sugestão de abrir chamado).
3) Retorne APENAS um JSON válido com os campos:
   {{
     "category": "Produtivo" | "Improdutivo",
     "confidence": número entre 0 e 1,
     "reply": "texto da resposta"
   }}

EXEMPLOS:
EMAIL: "Anexo o contrato. Favor validar e assinar." -> Produtivo
EMAIL: "Preciso de uma atualização sobre o chamado #456" -> Produtivo
EMAIL: "Feliz Natal! Obrigado pelo suporte." -> Improdutivo
EMAIL: "Obrigado pelo atendimento, sem mais." -> Improdutivo

EMAIL:
\"\"\"{text}\"\"\"
"""  # mantém o prompt igual

        model_name = os.environ.get("GOOGLE_GENAI_MODEL") or os.environ.get("GEMINI_MODEL") or "gemini-2.5-flash"

        # Config thinking_budget=0 para reduzir custo/tempo
        try:
            cfg = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        except Exception:
            cfg = None

        # Chamada ao GenAI
        resp = GENAI_CLIENT.models.generate_content(model=model_name, contents=prompt, config=cfg) if cfg else GENAI_CLIENT.models.generate_content(model=model_name, contents=prompt)

        # Extrair texto do GenAI
        generated = getattr(resp, "text", None) or str(resp)

        # Tenta extrair JSON da resposta
        m = re.search(r'(\{.*\})', generated, re.S)
        js_text = m.group(1) if m else generated

        try:
            out = json.loads(js_text)
        except json.JSONDecodeError:
            # heurística se não for JSON
            lower = generated.lower()
            category = "Produtivo" if "produtivo" in lower else "Improdutivo"
            confidence = 0.0
            reply = generated
            return category, confidence, reply, True

        category = out.get("category") or category_hint or "Improdutivo"
        confidence = float(out.get("confidence", 0.0))
        reply = out.get("reply", "").strip()

        return category, confidence, reply, True

    except Exception as e:
        print(f"[generate_response] GenAI error: {e}")
        return _local_fallback_reply(category_hint)
