# classifier.py (substitua o conteúdo atual por este)
import re
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

SAMPLE_DATA = [
    ("Preciso de uma atualização sobre o chamado #123, quando será resolvido?", "Produtivo"),
    ("Enviei os documentos solicitados. Por favor, confirme o recebimento.", "Produtivo"),
    ("O sistema está apresentando erro 500 ao salvar a nota fiscal.", "Produtivo"),
    ("Bom dia, gostaria de saber o status do processo.", "Produtivo"),
    ("Feliz Natal e um ótimo ano novo!", "Improdutivo"),
    ("Obrigado pela ajuda!", "Improdutivo"),
    ("Parabéns pelo projeto — excelente trabalho!", "Improdutivo"),
    ("Sorte e sucesso no próximo ano!", "Improdutivo"),
    ("Anexo o relatório solicitado. Aguardo retorno.", "Produtivo"),
    ("Tem alguém para conversar sobre contratação?", "Produtivo"),
    ("Só passando para desejar um bom fim de semana", "Improdutivo"),
    ("Reunião cancelada. Obrigado.", "Improdutivo"),
]

def simple_preprocess(text):
    text = text.lower()
    text = re.sub(r'https?:\/\/\S+',' ',text)
    text = re.sub(r'[^a-z0-9à-ú\s]',' ', text)
    text = re.sub(r'\s+',' ',text).strip()
    return text

class EmailClassifier:
    def __init__(self):
        texts = [simple_preprocess(t) for t,_ in SAMPLE_DATA]
        labels = [l for _,l in SAMPLE_DATA]
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1,2), max_features=2000)),
            ('clf', LogisticRegression(max_iter=500))
        ])
        self.pipeline.fit(texts, labels)

    def predict(self, text):
        """
        Retorna (categoria: 'Produtivo'|'Improdutivo', score: float)
        Regras:
         - Se o texto for muito curto (menos de 30 chars ou menos de 5 palavras),
           considera 'Improdutivo' para evitar falsos positivos.
         - Caso contrário, usa o modelo treinado.
        """
        ptext = simple_preprocess(text)

        # regra de tamanho mínimo
        char_count = len(ptext)
        word_count = len(ptext.split())
        MIN_CHARS = 30
        MIN_WORDS = 5

        # Se muito curto, tratar como Improdutivo (baixa confiança)
        if char_count < MIN_CHARS or word_count < MIN_WORDS:
            # Ainda podemos consultar o modelo para obter probabilidades,
            # mas preferimos marcar como Improdutivo para evitar alarmes.
            try:
                probs = self.pipeline.predict_proba([ptext])[0]
                # pega prob max apenas para informar score, mas reduzimos a confiança
                score = float(max(probs)) * 0.6
            except Exception:
                score = 0.5
            return "Improdutivoss", score

        # caso normal: usar o classificador
        pred = self.pipeline.predict([ptext])[0]
        probs = self.pipeline.predict_proba([ptext])[0]
        score = float(max(probs))
        return pred, score
