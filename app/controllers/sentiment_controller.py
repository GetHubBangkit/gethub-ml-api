import pickle

import numpy as np
from starlette.responses import JSONResponse
from app.helpers.handler import show_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

# Load tokenizer and model
def load_tokenizer_and_model(tokenizer_path, model_path):
    with open(tokenizer_path, 'rb') as handle:
        tokenizer = pickle.load(handle)
    model = load_model(model_path)
    return tokenizer, model

def preprocess_sentence(sentence, tokenizer, padding, truncating, maxlen):
    tokens = tokenizer.texts_to_sequences([sentence])
    pad_trunc_seq = pad_sequences(tokens, padding=padding, truncating=truncating, maxlen=maxlen)
    return pad_trunc_seq[0]


def predict_sentiment(sentence):
    tokenizer, model = load_tokenizer_and_model('data/sentiment/tokenizer.pickle',
                                                'data/sentiment/model.keras')

    PADDING = 'post'
    TRUNCATING = 'post'
    MAXLEN = 200

    preprocessed_sentence = preprocess_sentence(sentence, tokenizer, PADDING, TRUNCATING, MAXLEN)
    prediction = model.predict(np.expand_dims(preprocessed_sentence, axis=0))
    predicted_class = prediction.argmax(axis=1)[0]

    # Get the predicted class probability
    class_prob = prediction[0][predicted_class]

    # Calculate accuracy percentage
    accuracy = class_prob * 100

    return predicted_class, accuracy

def post(text: str) -> JSONResponse:
    predicted_class, accuracy = predict_sentiment(text)
    # Map the predicted class to sentiment labels
    sentiment_labels = {0: "Netral", 1: "Positif", 2: "Negatif"}
    sentiment = sentiment_labels.get(predicted_class, "Unknown")
    data = {
        "sentiment": sentiment,
        "accuracy": accuracy
    }
    return show_model(0, "Successfully Get Data", data)
