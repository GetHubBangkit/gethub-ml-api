import pickle
import string

import numpy as np
import pandas as pd
from pytesseract import pytesseract
from starlette.responses import JSONResponse
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

from app.controllers import sentiment_controller
from app.helpers.handler import show_model

def cleanText(txt):
    whitespace = string.whitespace
    punctuation = "!#$%&\'()*+:;<=>?[\\]^`{|}~"
    tableWhitespace = str.maketrans('', '', whitespace)
    tablePunctuation = str.maketrans('', '', punctuation)
    text = str(txt)
    # text = text.lower()
    removewhitespace = text.translate(tableWhitespace)
    removepunctuation = removewhitespace.translate(tablePunctuation)

    return str(removepunctuation)

def post(text: str) -> JSONResponse:
    with open('data/fraud/tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    # Load the model for prediction
    loaded_model = load_model('data/fraud/model.h5')

    sequences = tokenizer.texts_to_sequences([text])
    padded_sequences = pad_sequences(sequences, maxlen=100)  # Use the same maxlen as in training
    predictions = loaded_model.predict(padded_sequences)
    predicted_class_index = np.argmax(predictions)
    class_labels = ['fraud_project_job', 'real_project_job']
    predicted_class_label = class_labels[predicted_class_index]

    # Calculate accuracy of the predicted class label
    accuracy = float(predictions[0][predicted_class_index])  # Convert numpy.float32 to float

    data = {
        "prediction": predicted_class_label,
        "accuracy": accuracy
    }

    return show_model(0, "Successfully Get Data", data)

def scan(image) :
    ocr_text = pytesseract.image_to_data(image)
    # convert into dataframe
    list_of_text = list(map(lambda x: x.split('\t'), ocr_text.split('\n')))
    df = pd.DataFrame(list_of_text[1:], columns=list_of_text[0])
    df.dropna(inplace=True)  # drop missing values
    df['text'] = df['text'].apply(cleanText)

    # convet data into content
    df_clean = df.query('text != "" ')
    content = " ".join([w for w in df_clean['text']])
    return predict(content)

def predict(content: str) -> JSONResponse:
    # Ubah setiap baris menjadi array kata-kata
    words_array = []
    lines = content.split()
    for i in range(0, len(lines), 20):
        words_array.append(" ".join(lines[i:i + 20]))

    with open('data/fraud/tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    # Load the model for prediction
    loaded_model = load_model('data/fraud/model.h5')

    # Tokenisasi setiap array kata-kata
    sequences = tokenizer.texts_to_sequences(words_array)
    padded_sequences = pad_sequences(sequences, maxlen=100)  # Use the same maxlen as in training

    # Prediksi kelas untuk setiap array kata-kata
    predictions = loaded_model.predict(padded_sequences)
    predicted_class_indices = [np.argmax(pred) for pred in predictions]
    class_labels = ['fraud_project_job', 'real_project_job']

    # Hitung akurasi untuk setiap prediksi
    accuracies = [float(pred[idx]) for pred, idx in zip(predictions, predicted_class_indices)]

    # Gabungkan hasil prediksi, akurasi, dan jumlah fraud/real job
    results = []
    total_fraud = 0
    total_real_job = 0
    total_netral = 0
    total_positif = 0
    total_negatif = 0

    for i, (idx, acc) in enumerate(zip(predicted_class_indices, accuracies)):
        prediction = class_labels[idx]
        text = words_array[i]

        predicted_class, accuracy = sentiment_controller.predict_sentiment(text)
        sentiment_labels = {0: "Netral", 1: "Positif", 2: "Negatif"}
        sentiment = sentiment_labels.get(predicted_class, "Unknown")
        results.append({
            "prediction": prediction,
            "accuracy": acc,
            "text": text,
            "sentiment": sentiment,
            "sentiment_accuracy": accuracy
        })

        if prediction == "fraud_project_job":
            total_fraud += 1
        elif prediction == "real_project_job":
            total_real_job += 1

        if sentiment == "Netral":
            total_netral += 1
        elif sentiment == "Positif":
            total_positif += 1
        elif sentiment == "Negatif":
            total_negatif += 1

    totals = {
        "total_fraud": total_fraud,
        "total_real_job": total_real_job,
        "total_netral": total_netral,
        "total_positif": total_positif,
        "total_negatif": total_negatif
    }

    return show_model(0, "Successfully Predict Data",
                      {
                          "results": results,
                          "totals": totals,
                          "contents": content})