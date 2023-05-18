from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson.json_util import dumps
from utils.cleanData import clean_data
from nltk import PorterStemmer, word_tokenize
from nltk.corpus import stopwords
import io
import zipfile
import json
import re
import pandas as pd
from models.question import Question

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

app.config["MONGO_URI"] = "mongodb://localhost:27017/Copy-Catch"
mongo = PyMongo(app)
db = mongo.db


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file and file.content_type == 'application/x-zip-compressed':
        file_stream = io.BytesIO(file.stream.read())

        with zipfile.ZipFile(file_stream, 'r') as zip_file:
            folder_names = []
            text_responses = {}
            for file_name in zip_file.namelist():
                if '/' in file_name:
                    folder_name = file_name.split('/', 1)[0]
                    if folder_name.startswith('Q'):
                        folder_names.append(folder_name)
                        keeps = file_name.split('/')[1].split()[0]
                        if keeps != 'Question' and 'Attempt1_textresponse' in file_name:
                            text_response = zip_file.read(file_name).decode('utf-8')
                            text_response = text_response.lower()
                            text_response = re.sub(r"[^a-zA-Z0-9 ]", "", text_response)
                            if 'any text entered here will be displayed in the response input box when a new attempt ' \
                               'at the question starts.' in text_response:
                                text_response = text_response.replace('any text entered here will be displayed in the '
                                                                      'response input box when a new attempt at the '
                                                                      'question starts.', '')
                                text_response = text_response.strip()
                                if text_response == '':
                                    text_response = '-'
                            if folder_name not in text_responses:
                                text_responses[folder_name] = {'students': {}}
                            text_responses[folder_name]['students'][keeps] = text_response
                    else:
                        folder_names.clear()
                        return 'This file is not in the right format'

        folder_names = list(set(folder_names))

        sub_questions = []
        for folder_name in folder_names:
            sub_question = {'question': folder_name, 'students': text_responses[folder_name]['students']}
            sub_questions.append(sub_question)

        question = Question(course_id=1, all_question=sub_questions)

        question_dict = question.to_dict()

        db.Question.insert_one(question_dict)

        return 'Successfully upload the files'
    else:
        return 'Invalid file type. Only x-zip-compressed files are allowed.'


@app.route('/get_data', methods=['GET'])
def get_data():
    # collections = db.Question
    # cursor = collections.find({})
    # with open('collection.json', 'w') as file:
    #     file.write('[')
    #     with open('collection.json', 'w') as file:
    #         json.dump(json.loads(dumps(cursor)), file)
    df = pd.read_json('D:/Compo-work/copy-catch-backend/collection.json')
    print(df)
    return 'se'


if __name__ == '__main__':
    app.run(debug=True)
