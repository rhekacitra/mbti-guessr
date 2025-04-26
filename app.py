from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
import re
from itertools import product

vectorizer = joblib.load('vectorizer.pkl')
models = {
    'IE': joblib.load('IE_model.pkl'),
    'NS': joblib.load('NS_model.pkl'),
    'FT': joblib.load('FT_model.pkl'),
    'JP': joblib.load('JP_model.pkl')
}

introvert_patterns = [r"don't like to party", r"rather stay in", r"prefer being alone", r"avoid people", r"need time alone", r"drained after socializing", r"enjoy solitude", r"quiet reflection"]
extrovert_patterns = [r"love to party", r"enjoy going out", r"love being around people", r"need to socialize", r"gain energy from people", r"talk to everyone", r"center of attention", r"crowd loving"]

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/main')
def main_page():
    return render_template('main.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    text = data.get("text", "")

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    vec = vectorizer.transform([text])
    text_lower = text.lower()
    boost_factor = 1.2

    proba_IE = models['IE'].predict_proba(vec)[0]
    proba_NS = models['NS'].predict_proba(vec)[0]
    proba_FT = models['FT'].predict_proba(vec)[0]
    proba_JP = models['JP'].predict_proba(vec)[0]

    if any(re.search(p, text_lower) for p in introvert_patterns):
        proba_IE[0] *= boost_factor
    elif any(re.search(p, text_lower) for p in extrovert_patterns):
        proba_IE[1] *= boost_factor

    letters = {d: models[d].classes_ for d in ['IE', 'NS', 'FT', 'JP']}
    all_types = list(product(letters['IE'], letters['NS'], letters['FT'], letters['JP']))

    mbti_probs = []
    for mbti in all_types:
        prob = (
            proba_IE[list(letters['IE']).index(mbti[0])] *
            proba_NS[list(letters['NS']).index(mbti[1])] *
            proba_FT[list(letters['FT']).index(mbti[2])] *
            proba_JP[list(letters['JP']).index(mbti[3])]
        )
        mbti_probs.append((''.join(mbti), prob))

    top_3 = sorted(mbti_probs, key=lambda x: x[1], reverse=True)[:3]
    return jsonify({mbti: round(prob, 2) for mbti, prob in top_3})

if __name__ == '__main__':
    app.run(debug=True)
