from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
import io
import zipfile
import json
import re
import pandas as pd
from models.question import Question
from BM25 import BM25
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from googleapiclient.discovery import build
from spellchecker import SpellChecker

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
    file_stream = io.BytesIO(file.stream.read())
    try:
        with zipfile.ZipFile(file.stream) as zip_file:
            pass
    except zipfile.BadZipFile:
        return jsonify({'message': 'Invalid file type'}), 200

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
                        question = Question(course_id=3, question=folder_names, student_name=student_name,
                                            student_id=student_id, answer=text_response)
                        question_dict = question.to_dict()
                        db.Question.insert_one(question_dict)
                else:
                    return jsonify({'message': 'Invalid format'}), 200
        all_questions = db.Question.distinct('question')
        for question in all_questions:
            for student_id in student_ids:
                query = {
                    'question': question,
                    'student_id': student_id
                }
                if db.Question.count_documents(query) == 0:
                    question_data = {
                        'course_id': 3,
                        'question': question,
                        'student_name': 'null',
                        'student_id': student_id,
                        'answer': 'null'
                    }
                    db.Question.insert_one(question_data)
    return jsonify({'message': 'Upload successful'}), 200


@app.route('/comparing_student', methods=['GET'])
def comparingStudentAnswer():
    global keep_id, sorted_data_return, new_dict
    data = db.Question.find({'course_id': 3})
    df = pd.DataFrame(data, columns=['_id', 'course_id', 'question', 'student_id', 'student_name', 'answer'])
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
    data = db.Question.find({'course_id': 3})
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
                percentage = round((df_bm['tfidf'].iloc[0] * 100),2)
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


@app.route('/search_google2', methods=['GET'])
def searchGoogle2():
    answer = "ensure security groups do not allow ingress from 0 0 0 0 0 to port 3389 eco instance does not allow inbound traffic from all to tcp port 2379"
    global keep_id, sorted_data_return, new_dict
    data = {
        "title": ["Ensure Security Groups do not allow ingress from 0.0.0.0/0 to port ...",
                  "HAProxy Network Error: cannot bind socket | DigitalOcean",
                  "Ensure Security Groups accept traffic only from ports 80 and 443"
            , "APISIX Ingress Controller the Hard Way | Apache APISIX® -- Cloud ..",
                  "https://opendev.org/openstack/osops/commit/c560cdc..."],
        "snippet": [
            "Ensure Security Groups do not allow ingress from 0.0.0.0/0 to port 3389 ... EC2 instance does not allow inbound traffic from all to TCP port 2379",
            "Nov 4, 2020 ... The issue is that only a single process can be bound to an IP address and port combination at any given time. In the second case, when HAProxy ...",
            "For HTTPS traffic, add an inbound rule on port 443 from the source address 0.0.0.0/0. These inbound rules allow traffic from IPv4 addresses. We recommend you ...",
            "In this tutorial, we will install APISIX and APISIX Ingress Controller in ... ports: - name: \"client\" port: 2379 targetPort: client - name: \"peer\"",
            "Add security rules to allow ping, ssh, docker access + 4. ... +# create a specific application layer security group that routes database port 3306 traffic, ..."],
        "formattedUrl": ["https://docs.bridgecrew.io/docs/networking_2",
                         "https://www.digitalocean.com/.../haproxy-network-error-cannot-bind-socket",
                         "https://docs.bridgecrew.io/docs/networking_11",
                         "https://apisix.apache.org/docs/ingress-controller/tutorials/the-hard-way",
                         "https://opendev.org/.../c560cdc64dcc66a92de628bd614fcd687bca4f5c.diff"]
    }
    data["snippet"] = [snippet.lower() for snippet in data["snippet"]]
    data["snippet"] = [re.sub(r'[^a-zA-Z0-9 ]', ' ', snippet) for snippet in data["snippet"]]
    data["snippet"] = [join_text(snippet) for snippet in data["snippet"]]
    print(data)
    df_web = pd.DataFrame(data, columns=['title', 'snippet', 'formattedUrl'])
    data = db.Question.find({'course_id': 3})
    df = pd.DataFrame(data, columns=['_id', 'course_id', 'question', 'student_id', 'student_name', 'answer'])
    question = df['question']
    list_q = list(set(question))
    list_q = sorted(list_q, key=lambda x: int(x.split('-')[0][1:]))
    temp = {}
    vectorizer = TfidfVectorizer()
    corpus = df_web['snippet'].tolist()
    vectorizer.fit(corpus)
    # for question in list_q:
    #     keep = df[df['question'] == question]
    #     df_question = pd.DataFrame(data=keep)
    #     keep_id = keep['student_id']
    #     keep_id = sorted(keep_id, key=lambda x: x[:2] + x[2:])
    #     for student_id in keep_id:
    #         data_for_id = df_question[df_question['student_id'] == student_id]
    #         answer = data_for_id['answer'].iloc[0]
    #         if answer != 'null':
    #             answer = answer.lower()
    # test = BM25()
    # test.fit(df_question['answer'])
    # score = test.transform(answer)
    # df_bm = pd.DataFrame(data=df_question)
    # df_bm['bm25'] = list(score)
    # df_bm['rank'] = df_bm['bm25'].rank(ascending=False)
    # df_bm = df_bm.nlargest(columns='bm25', n=3)
    # print('-----------------')
    # print(df_bm['bm25'].iloc[0])
    #
    # answer.lower()
    # answer = re.sub(r'[^a-zA-Z0-9 ]', ' ', answer)
    # test = BM25()
    # test.fit(df_web['snippet'])
    answer_vector = vectorizer.transform([answer])
    result_vectors = vectorizer.transform(df_web['snippet'])
    scores = cosine_similarity(answer_vector, result_vectors)
    scores = scores[0]
    df_bm = pd.DataFrame(data=df_web)
    df_bm['bm25'] = list(scores)
    df_bm['rank'] = df_bm['bm25'].rank(ascending=False)
    df_bm = df_bm.nlargest(columns='bm25', n=5)

    print(df_bm[['snippet', 'bm25', 'link']])
    # print(df_bm['bm25'])
    # print(df_bm['bm25'])
    # results = google_search(answer, my_api_key, my_cse_id)
    # scores = process_search_results(answer, results, vectorizer)
    # max_score = max(scores)
    # percentages = (df_bm['bm25'].iloc[0] / 100) * 100
    # print(percentages)
    #
    # print(answer)
    # print('-----------------')
    # print(f"Search Scores: {scores}")
    # print(f"Percentages: {percentages}")
    # print('-----------------')

    # if percentage < 50:
    #     percentage = 0
    # print(percentage)
    return "Success"


if __name__ == '__main__':
    app.run(debug=True)
