from flask import Flask, request, jsonify, blueprints
from flask_cors import CORS
from flask_pymongo import PyMongo
import io
import zipfile
import json
import re
import pandas as pd
from BM25 import BM25
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from googleapiclient.discovery import build
from spellchecker import SpellChecker
from models.question import Question

# from routes.compare_bp import CompareBlueprint
from routes.upload_bp import UploadBlueprint

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})
app.config["MONGO_URI"] = "mongodb://localhost:27017/Copy-Catch"
mongo = PyMongo(app)
db = mongo.db

spellchecker = SpellChecker(language='en')

coding_words_file = 'assets/coding_words.txt'

with open(coding_words_file, 'r') as file:
    for line in file:
        word = line.strip()
        spellchecker.word_frequency.load_words([word])

class FlaksApp:
    app.register_blueprint(UploadBlueprint.upload_bp)
    # app.register_blueprint(CompareBlueprint.compare_bp)


if __name__ == '__main__':
    app.run(debug=True)
