# app/routes.py
from flask import render_template, jsonify, request
from app import app
import pandas as pd
import random
import os
from .model.emotion_predictor import get_emotion_from_text
from .helper import select_best_matching_song

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_random_track', methods=['GET'])
def get_random_track():
    csv_path = os.path.join(app.root_path, '..', 'data', 'songs.csv')
    df = pd.read_csv(csv_path)
    random_track_id = random.choice(df['Track_ID'].dropna().tolist())
    return jsonify(track_id=random_track_id)

@app.route('/get_emotion_based_song', methods=['POST'])
def get_emotion_based_song():
    data = request.json
    text = data.get('text', '')

    if text:
        predicted_emotions = get_emotion_from_text(text)
        track_id = select_best_matching_song(predicted_emotions)
        return jsonify(track_id=track_id)  
    else:
        return jsonify({"error": "No text provided"}), 400