from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson.json_util import dumps
from nltk import PorterStemmer, word_tokenize

from utils.cleanData import clean_data
from nltk.corpus import stopwords
import io
import zipfile
import json
import re
import pandas as pd
from models.question import Question
from spellchecker import SpellChecker
import pickle

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import sparse
import pickle

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

app.config["MONGO_URI"] = "mongodb://localhost:27017/Copy-Catch"
mongo = PyMongo(app)
db = mongo.db

spell = SpellChecker(language='en')


def perform_spell_correction(text):
    spell = SpellChecker(language='en')
    corrected_text = []
    words = text.split()
    for word in words:
        corrected_word = spell.correction(word)
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
                            text_response = re.sub(r'[^a-zA-Z0-9 ]', ' ', text_response)

                            # spell_corr = [spell.correction(w) for w in text_response.split()]
                            # spell_corr = list(filter(None, spell_corr))
                            # text_response = ' '.join(spell_corr)
                            text_response = perform_spell_correction(text_response)

                            question = Question(course_id=3, question=folder_names, student_name=student_name,
                                                student_id=student_id, answer=text_response)
                            question_dict = question.to_dict()
                            db.Question.insert_one(question_dict)
                    else:
                        return 'This file is not in the right format'
                    #     # folder_names.append(folder_name)
                    #     keeps = file_name.split('/')[1].split()[0]
                    #     print(keeps)
                    #     if keeps != 'Question' and 'Attempt1_textresponse' in file_name:
                    #         text_response = zip_file.read(file_name).decode('utf-8')
                    #         text_response = text_response.lower()
                    #         if 'any text entered here will be displayed in the response input box when a new attempt ' \
                    #            'at the question starts.' in text_response:
                    #             text_response = text_response.replace('any text entered here will be displayed in the '
                    #                                                   'response input box when a new attempt at the '
                    #                                                   'question starts.', '')
                    #             text_response = text_response.strip()
                    #             if text_response == '':
                    #                 text_response = 'null'
                    #         text_response = re.sub(r'[^a-zA-Z0-9 ]', '', text_response)
                    # if folder_name not in text_responses:
                    #     text_responses[folder_name] = {'students': {}}
                    # text_responses[folder_name]['students'][keeps] = text_response
                    # count = db.Question.count_documents({})
                    # print(count)
                    # else:
                    #     folder_names = ''
                    #     return 'This file is not in the right format'

        # folder_names = list(set(folder_names))
        # print(folder_names)
        # sub_questions = []
        # for folder_name in folder_names:
        #     sub_question = {'question': folder_name, 'students': text_responses[folder_name]['students']}
        #     sub_questions.append(sub_question)
        #
        # question = Question(course_id=1, all_question=sub_questions)
        #
        # question_dict = question.to_dict()
        #
        # db.Question.insert_one(question_dict)

        return 'Successfully upload the files'
    else:
        return 'Invalid file type. Only x-zip-compressed files are allowed.'


@app.route('/get_data', methods=['GET'])
def get_data():
    data = db.Question.find({'course_id': 3})
    df = pd.DataFrame(data, columns=['_id', 'course_id', 'question', 'student_id', 'student_name', 'answer'])

    question = df['question']
    list_q = list(set(question))
    list_q = sorted(list_q, key=lambda x: int(x.split('-')[0][1:]))
    # print(list_q)

    for check in list_q:
        keep = df[df['question'] == check]
        # print(check)
        df_question = pd.DataFrame(data=keep)
        # print(df_question.iloc[:,4:6])
        keep_id = keep['student_id']
        keep_id = sorted(keep_id, key=lambda x: (int(x[:2]), int(x[2:])))
        # print(keep_id)
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
    #

    # create_df = pd.DataFrame(columns=list_q)
    # print(create_df)
    # print(list_q)
    # collections = db.Question
    # cursor = collections.find({})
    # with open('collection.json', 'w') as file:
    #     file.write('[')
    #     with open('collection.json', 'w') as file:
    #         json.dump(json.loads(dumps(cursor)), file)
    # df = pd.read_json('D:/Compo-work/copy-catch-backend/collection.json')
    # print(df)

    # df = pd.read_json('D:/Compo-work/copy-catch-backend/collection.json', orient='records')
    # df = df.drop(columns='_id')
    # print(df)
    # pickle.dump(df, open('D:/Compo-work/copy-catch-backend/parsed_data.pkl', 'wb'))

    # parsed_data = pickle.load(open('D:/Compo-work/copy-catch-backend/parsed_data.pkl', 'rb'))
    # answer = BM25()
    # answer.fit(parsed_data['answer'])
    # pickle.dump(answer, open('D:/Compo-work/copy-catch-backend/answer.pkl', 'wb'))
    #
    # query = 'the 0 0 0 0 means that any ip and then the 2379 is the port that you will allow  need to enter to enter the specific part of the website network   e g  if you enter 1 2 3 4 only it will show a page says hello world  but if you enter 1 2 3 4 2379 it will show the page of the pizza website that you have make   in summary 0 0 0 0 means ip and the 2379 is the port that allows to push  pull visit the information that is in that said ip whether it s internal or external depends on the settting'
    # spell_corr = [spell.correction(w) for w in query.split()]
    # spell_corr = list(filter(None, spell_corr))
    # spell_corr = " ".join(spell_corr)
    # answer = pickle.load(open('D:/Compo-work/copy-catch-backend/answer.pkl', 'rb'))
    # score = answer.transform(spell_corr)
    # # print(score)
    # df_bm = pd.DataFrame(data=parsed_data)
    # df_bm['bm25'] = list(score)
    # df_bm['rank'] = df_bm['bm25'].rank(ascending=False)
    # df_bm = df_bm.nlargest(columns='bm25', n=17)
    # keep = df_bm.to_dict('records')
    # print(keep)

    return 'se'


class BM25(object):
    def __init__(self, b=0.75, k1=1.6):
        self.vectorizer = TfidfVectorizer(norm=None, smooth_idf=False, ngram_range=(1, 3))
        self.b = b
        self.k1 = k1

    def fit(self, X):
        """ Fit IDF to documents X """
        self.vectorizer.fit(X)
        y = super(TfidfVectorizer, self.vectorizer).transform(X)
        self.X = y
        self.avdl = y.sum(1).mean()

    def transform(self, q):
        """ Calculate BM25 between query q and documents X """
        b, k1, avdl = self.b, self.k1, self.avdl

        len_X = self.X.sum(1).A1

        q, = super(TfidfVectorizer, self.vectorizer).transform([q])

        assert sparse.isspmatrix_csr(q)
        X = self.X.tocsc()[:, q.indices]
        denom = X + (k1 * (1 - b + b * len_X / avdl))[:, None]
        idf = self.vectorizer._tfidf.idf_[None, q.indices] - 1.
        numer = X.multiply(np.broadcast_to(idf, X.shape)) * (k1 + 1)
        return (numer / denom).sum(1).A1


if __name__ == '__main__':
    app.run(debug=True)
