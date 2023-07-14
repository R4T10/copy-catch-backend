from flask import Flask, request, jsonify, blueprints
from flask_cors import CORS
from flask_pymongo import PyMongo

from spellchecker import SpellChecker


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


if __name__ == '__main__':
    from routes.upload_bp import UploadBlueprint
    app.register_blueprint(UploadBlueprint.upload_bp)
    from routes.compare_bp import CompareBlueprint
    app.register_blueprint(CompareBlueprint.compare_bp)
    from routes.course_bp import CourseBlueprint
    app.register_blueprint(CourseBlueprint.course_bp)
    app.run(debug=True)