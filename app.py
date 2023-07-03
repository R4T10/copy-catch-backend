from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
import io
import zipfile
import re
import pandas as pd
from bson import ObjectId
from models.course import Course
from models.question import Question
from BM25 import BM25
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from googleapiclient.discovery import build
from spellchecker import SpellChecker
from bson import ObjectId

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

app.config["MONGO_URI"] = "mongodb://localhost:27017/Copy-Catch"
mongo = PyMongo(app)
db = mongo.db

spellchecker = SpellChecker(language='en')

# Path to the coding_words.txt file
coding_words_file = 'assets/coding_words.txt'

# my_api_key = "AIzaSyCkAsCqOzds-oFWnasdQlrx2ql2s2RtjWk"
# my_cse_id = "042a0393f912b4ffa"
# my_api_key = "AIzaSyCmRvHOP1wJM5rUF9JMlpHgOA8yaaytae0"
# my_cse_id = "03082958736eb4b86"
# my_api_key = "AIzaSyCK2TB3yEzihRCiH9h17xUSbIZbR8nWbEk"
# my_cse_id = "a454c0eb1bb48467b"
my_api_key = "AIzaSyAIusN4eOqS_GDypfgwtfT5TLC7DB96Ksk"
my_cse_id = "9605d29e4a84e43e6"
# my_api_key = "AIzaSyB8gaMkDkbAT-NTRXw346rFGNjeiGdWW88"
# my_cse_id = "02d90ac65942f44f3"

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


def join_text(text):
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove non-alphanumeric characters
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    return cleaned_text.strip()


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']


def calculate_percentages(scores):
    ranked_scores = sorted(scores, reverse=True)
    max_score = ranked_scores[0]
    percentages = [(score / max_score) * 100 for score in scores]

    return percentages


def process_search_results(answer, snippets, vectorizer):
    answer_vector = vectorizer.transform([answer])
    result_vectors = vectorizer.transform(snippets)

    scores = cosine_similarity(answer_vector, result_vectors)

    return scores


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    course_id = request.form['id']
    course_id = ObjectId(course_id)
    file_stream = io.BytesIO(file.stream.read())
    with zipfile.ZipFile(file_stream, 'r') as zip_file:
        student_ids = set()
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
                        student_ids.add(student_id)
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
                        question = Question(course_id=course_id, question=folder_names, student_name=student_name,
                                            student_id=student_id, answer=text_response)
                        question_dict = question.to_dict()
                        db.Question.insert_one(question_dict)
                else:
                    return jsonify({'message': 'Invalid format'}), 400
        all_questions = db.Question.distinct('question')
        for question in all_questions:
            for student_id in student_ids:
                query = {
                    'question': question,
                    'student_id': student_id
                }
                if db.Question.count_documents(query) == 0:
                    question_data = {
                        'course_id': course_id,
                        'question': question,
                        'student_name': 'null',
                        'student_id': student_id,
                        'answer': 'null'
                    }
                    db.Question.insert_one(question_data)
        db.Courses.update_one(
            {'_id': ObjectId(course_id)},
            {'$set': {'file': True}}
        )
    return jsonify({'message': 'Upload successful'}), 200


@app.route('/comparing_student', methods=['GET'])
def comparingStudentAnswer():
    global keep_id, sorted_data_return, new_dict
    course_id = request.args.get('id')
    course_id = ObjectId(course_id)
    print(course_id)
    data = db.Question.find({'course_id': course_id})
    df = pd.DataFrame(data, columns=['_id', 'course_id', 'question', 'student_id', 'student_name', 'answer'])
    courses = []
    for course in data:
        courses.append({
            'course_id': course['course_id'],
            'question': course['question'],
            'student_id': course['student_id'],
            'student_name': course['student_name'],
            'answer': course['answer']
        })
    print(courses)
    question = df['question']
    list_q = list(set(question))
    list_q = sorted(list_q, key=lambda x: int(x.split('-')[0][1:]))
    temp = {}
    for question in list_q:
        keep = df[df['question'] == question]
        df_question = pd.DataFrame(data=keep)
        keep_id = keep['student_id']
        keep_id = sorted(keep_id, key=lambda x: x[:2] + x[2:])
        for student_id in keep_id:
            data_for_id = df_question[df_question['student_id'] == student_id]
            answer = data_for_id['answer'].iloc[0]
            if answer != 'null':
                # vectorizer = TfidfVectorizer()
                # vectorizer.fit_transform(df_question['answer'])
                # print(student_id)
                # score = vectorizer.transform([answer])
                # df_tfidf = pd.DataFrame(data=df_question)
                # print(score.data)
                # df_tfidf['tfidf'] = scores.data
                # df_tfidf['rank'] = df_tfidf['tfidf'].rank(ascending=False)
                # df_tfidf = df_tfidf.nlargest(columns='tfidf', n=3)
                # print(df_tfidf)
                # percentage = round((df_tfidf['tfidf'].iloc[1] / df_tfidf['tfidf'].iloc[0]) * 100, 2)
                # print(df_tfidf)
                test = BM25()
                test.fit(df_question['answer'])
                score = test.transform(answer)
                df_bm = pd.DataFrame(data=df_question)
                df_bm['bm25'] = list(score)
                df_bm['rank'] = df_bm['bm25'].rank(ascending=False)
                df_bm = df_bm.nlargest(columns='bm25', n=3)
                print(question)
                print(student_id)
                print(df_bm['student_name'] + "" + df_bm['answer'])
                print(df_bm['bm25'])
                percentage = round((df_bm['bm25'].iloc[1] / df_bm['bm25'].iloc[0]) * 100, 2)
                if percentage < 50:
                    percentage = 0
                print(percentage)
            else:
                percentage = 0
            if student_id not in temp:
                temp[student_id] = {'student_id': student_id, 'answers': []}
            temp[student_id]['answers'].append(percentage)
    response_data = {
        'question': list_q,
        'data': list(temp.values())
    }

    return response_data, 200


@app.route('/search_google', methods=['GET'])
def searchGoogle():
    global results
    data = db.Question.find({'course_id': ObjectId('64a295a45d63600866c3ced7')})
    df = pd.DataFrame(data, columns=['_id', 'course_id', 'question', 'student_id', 'student_name', 'answer'])
    question = df['question']
    list_q = list(set(question))
    list_q = sorted(list_q, key=lambda x: int(x.split('-')[0][1:]))
    temp = {}
    vectorizer = TfidfVectorizer()
    corpus = df['answer'].tolist()
    vectorizer.fit(corpus)
    for question in list_q:
        keep = df[df['question'] == question]
        df_question = pd.DataFrame(data=keep)
        keep_id = keep['student_id']
        keep_id = sorted(keep_id, key=lambda x: x[:2] + x[2:])
        for student_id in keep_id:
            data_for_id = df_question[df_question['student_id'] == student_id]
            answer = data_for_id['answer'].iloc[0]
            if answer != 'null':
                results = google_search(answer, my_api_key, my_cse_id)
                for i in range(len(results)):
                    results[i]["snippet"] = results[i]["snippet"].lower()
                    results[i]["snippet"] = re.sub(r'[^a-zA-Z0-9 ]', ' ', results[i]["snippet"])
                    results[i]["snippet"] = perform_spell_correction(results[i]["snippet"])
                df_web = pd.DataFrame(results, columns=['title', 'snippet', 'link'])
                answer_vector = vectorizer.transform([answer])
                result_vectors = vectorizer.transform(df_web['snippet'])
                scores = cosine_similarity(answer_vector, result_vectors)
                scores = scores[0]
                df_bm = pd.DataFrame(data=df_web)
                df_bm['tfidf'] = list(scores)
                df_bm['rank'] = df_bm['tfidf'].rank(ascending=False)
                df_bm = df_bm.nlargest(columns='tfidf', n=5)
                percentage = round((df_bm['tfidf'].iloc[0] * 100), 2)
                print(answer)
                print(df_bm[['snippet', 'tfidf', 'link']])
                print(percentage)

                if percentage < 50:
                    percentage = 0
                print(percentage)
            else:
                percentage = 0
            if student_id not in temp:
                temp[student_id] = {'student_id': student_id, 'answers': []}
            temp[student_id]['answers'].append(percentage)

    response_data = {
        'question': list_q,
        'data': list(temp.values())
    }

    return response_data, 200


@app.route('/get_course_list', methods=['GET'])
def get_course_list():
    professor = 'Krit'
    data = db.Courses.find({'professor': professor})
    courses = []
    for course in data:
        courses.append({
            'id': str(course['_id']),
            'course_id': course['course_id'],
            'course_name': course['course_name'],
            'year': course['year'],
            'examination': course['examination'],
            'professor': course['professor'],
            'file': course['file']
        })
    return jsonify(courses), 200


@app.route('/adding_course', methods=['POST'])
def adding_course():
    course_id = request.form['course_id']
    course_name = request.form['course_name']
    year = request.form['year']
    examination = request.form['examination']
    professor = request.form['professor']
    file = False
    course = Course(course_id=course_id, course_name=course_name, year=year,
                    examination=examination, professor=professor, file=file)
    question_dict = course.to_dict()
    db.Courses.insert_one(question_dict)
    return jsonify({'message': 'Course added successfully'}), 200


@app.route('/delete_course', methods=['POST'])
def delete_course():
    course_id = request.form.get('id')
    db.Courses.delete_one({'_id': ObjectId(course_id)})
    db.Question.delete_many({'course_id': ObjectId(course_id)})
    return 'Delete success', 200


@app.route('/edit_course', methods=['POST'])
def edit_course():
    id = request.form.get('id')
    id = ObjectId(id)
    course_id = request.form['course_id']
    course_name = request.form['course_name']
    year = request.form['year']
    examination = request.form['examination']
    professor = request.form['professor']
    db.Courses.update_one(
        {'_id': id},
        {'$set': {
            'course_id': course_id,
            'course_name': course_name,
            'year': year,
            'examination': examination,
            'professor': professor
        }}
    )
    return 'Edit success', 200


if __name__ == '__main__':
    app.run(debug=True)
