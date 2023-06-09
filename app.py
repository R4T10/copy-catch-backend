from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson.json_util import dumps
from nltk import PorterStemmer, word_tokenize
from nltk.corpus import stopwords
import io
import zipfile
import json
import re
import pandas as pd
from models.question import Question
import pickle
from BM25 import BM25
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import sparse
import pickle
from spellchecker import SpellChecker

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

app.config["MONGO_URI"] = "mongodb://localhost:27017/Copy-Catch"
mongo = PyMongo(app)
db = mongo.db

spellchecker = SpellChecker(language='en')

# Path to the coding_words.txt file
coding_words_file = 'assets/coding_words.txt'

# Open the coding_words.txt file
with open(coding_words_file, 'r') as file:
    # Read the file line by line
    for line in file:
        # Remove leading/trailing whitespaces and newline characters
        word = line.strip()

        # Add the word to the spellchecker's internal dictionary
        spellchecker.word_frequency.load_words([word])


def perform_spell_correction(text):
    corrected_text = []
    words = text.split()
    for word in words:
        corrected_word = spellchecker.correction(word)
        corrected_text.append(corrected_word)
    spell_corr = list(filter(None, corrected_text))
    return ' '.join(spell_corr)


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file and file.content_type == 'application/x-zip-compressed':
        file_stream = io.BytesIO(file.stream.read())

        with zipfile.ZipFile(file_stream, 'r') as zip_file:
            for file_name in zip_file.namelist():
                if '/' in file_name:
                    folder_names = file_name.split('/', 1)[0]
                    folder_names = folder_names.replace('.', '').replace(' ', '')
                    if folder_names.startswith('Q'):
                        student_id = file_name.split('/')[1].split()[0]
                        name_parts = file_name.split("-")
                        if len(name_parts) >= 3:
                            student_name = name_parts[2].strip()
                        if student_id != 'Question' and 'Attempt1_textresponse' in file_name:
                            text_response = zip_file.read(file_name).decode('utf-8')
                            text_response = text_response.lower()
                            if 'any text entered here will be displayed in the response input box when a new attempt ' \
                               'at the question starts.' in text_response:
                                text_response = text_response.replace('any text entered here will be displayed in the '
                                                                      'response input box when a new attempt at the '
                                                                      'question starts.', '')
                                text_response = text_response.strip()
                                if text_response == '':
                                    text_response = 'null'
                            if "'s" in text_response:
                                text_response = text_response.replace("'s", '')
                            if "don't" in text_response:
                                text_response = text_response.replace("don't", 'do not')
                            text_response = re.sub(r'[^a-zA-Z0-9 ]', ' ', text_response)
                            text_response = perform_spell_correction(text_response)
                            question = Question(course_id=3, question=folder_names, student_name=student_name,
                                                student_id=student_id, answer=text_response)
                            question_dict = question.to_dict()
                            db.Question.insert_one(question_dict)
                    else:
                        return 'This file is not in the right format'
        return 'Successfully upload the files'
    else:
        return 'Invalid file type. Only zip file are allowed.'


@app.route('/get_data', methods=['GET'])
def get_data():
    data = db.Question.find({'course_id': 3})
    df = pd.DataFrame(data, columns=['_id', 'course_id', 'question', 'student_id', 'student_name', 'answer'])

    question = df['question']
    list_q = list(set(question))
    list_q = sorted(list_q, key=lambda x: int(x.split('-')[0][1:]))

    for check in list_q:
        keep = df[df['question'] == check]
        df_question = pd.DataFrame(data=keep)
        keep_id = keep['student_id']
        keep_id = sorted(keep_id, key=lambda x: (int(x[:2]), int(x[2:])))
        for student_id in keep_id:
            print(check)
            data_for_id = df_question[df_question['student_id'] == student_id]
            answer = data_for_id['answer'].iloc[0]
            print(answer)

            test = BM25()
            test.fit(df_question['answer'])
            score = test.transform(answer)
            df_bm = pd.DataFrame(data=df_question)
            df_bm['bm25'] = list(score)
            df_bm['rank'] = df_bm['bm25'].rank(ascending=False)
            df_bm = df_bm.nlargest(columns='bm25', n=3)
            print(df_bm.iloc[:, 4:7])
            keep = df_bm.to_dict('records')

    #     print(check)
    #     # print(keep)
    #     print(keep_id)
    #     keep_id = sorted(keep_id, key=lambda x: (int(x[:2]), int(x[2:])))
    #     for answer_c in keep_id:

    return 'se'


if __name__ == '__main__':
    app.run(debug=True)
