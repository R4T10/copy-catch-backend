import re
import pandas as pd
from bson import ObjectId
from flask import request

from BM25 import BM25
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from googleapiclient.discovery import build
from app import spellchecker, mongo

# my_api_key = "AIzaSyCkAsCqOzds-oFWnasdQlrx2ql2s2RtjWk"
# my_cse_id = "042a0393f912b4ffa"
# my_api_key = "AIzaSyCmRvHOP1wJM5rUF9JMlpHgOA8yaaytae0"
# my_cse_id = "03082958736eb4b86"
my_api_key = "AIzaSyCK2TB3yEzihRCiH9h17xUSbIZbR8nWbEk"
my_cse_id = "a454c0eb1bb48467b"
# my_api_key = "AIzaSyAIusN4eOqS_GDypfgwtfT5TLC7DB96Ksk"
# my_cse_id = "9605d29e4a84e43e6"
# my_api_key = "AIzaSyB8gaMkDkbAT-NTRXw346rFGNjeiGdWW88"
# my_cse_id = "02d90ac65942f44f3"

db = mongo.db


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']


def perform_spell_correction(text):
    corrected_text = []
    words = text.split()
    for word in words:
        corrected_word = spellchecker.correction(word)
        corrected_text.append(corrected_word)
    spell_corr = list(filter(None, corrected_text))
    return ' '.join(spell_corr)


def comparingStudentAnswer():
    global keep_id, sorted_data_return, new_dict, df_bm
    course_id = request.args.get('id')
    course_id = ObjectId(course_id)
    print(course_id)
    data = db.Question.find({'course_id': course_id})
    df = pd.DataFrame(data, columns=['_id', 'course_id', 'question', 'question_text', 'student_id', 'student_name',
                                     'answer'])
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
    df_bm_dict = {}
    prev_student_names = {}
    for question in list_q:
        keep = df[df['question'] == question]
        question_text = keep['question_text'].iloc[0]
        print(question_text)
        df_question = pd.DataFrame(data=keep)
        print(df_question)
        keep_id = keep['student_id']
        keep_id = sorted(keep_id, key=lambda x: x[:2] + x[2:])
        for student_id in keep_id:
            data_for_id = df_question[df_question['student_id'] == student_id]
            answer = data_for_id['answer'].iloc[0]
            student_name = data_for_id['student_name'].iloc[0]
            if answer != 'null':
                test = BM25()
                test.fit(df_question['answer'])
                score = test.transform(answer)
                df_bm = pd.DataFrame(data=df_question)
                df_bm['bm25'] = list(score)
                df_bm['rank'] = df_bm['bm25'].rank(ascending=False)
                df_bm = df_bm.nlargest(columns='bm25', n=4)
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
                student_name = prev_student_names.get(student_id, None)

            if student_id not in temp:
                temp[student_id] = {'student_id': student_id, 'answers': []}

            if student_name:
                temp[student_id]['student_name'] = student_name
                comparison_data = df_bm[['student_name', 'question_text', 'answer', 'student_id']].to_dict(
                    orient='records')
                temp[student_id]['answers'].append({
                    'question': question,
                    'answer': answer,
                    'comparison_data': [entry for entry in comparison_data if
                                        entry['student_name'] != student_name],
                    'percentage': percentage,
                    'question_text': question_text
                })

            prev_student_names[student_id] = student_name

            if not student_name and 'student_name' in temp[student_id]:
                temp[student_id]['student_name'] = prev_student_names[student_id]

            if not student_name:
                temp[student_id]['answers'].append({
                    'question': question,
                    'percentage': percentage
                })
            df_bm_dict[question] = df_bm

    response_data = {
        'question': list_q,
        'data': list(temp.values())
    }

    return response_data, 200


def searchGoogle():
    global results, df_bm
    course_id = request.args.get('id')
    course_id = ObjectId(course_id)
    data = db.Question.find({'course_id': course_id})
    df = pd.DataFrame(data,
                      columns=['_id', 'course_id', 'question', 'question_text', 'student_id', 'student_name', 'answer'])
    question = df['question']
    list_q = list(set(question))
    list_q = sorted(list_q, key=lambda x: int(x.split('-')[0][1:]))
    temp = {}
    df_bm_dict = {}
    prev_student_names = {}
    vectorizer = TfidfVectorizer()
    corpus = df['answer'].tolist()
    vectorizer.fit(corpus)
    for question in list_q:
        keep = df[df['question'] == question]
        question_text = keep['question_text'].iloc[0]
        print(question_text)
        df_question = pd.DataFrame(data=keep)
        keep_id = keep['student_id']
        keep_id = sorted(keep_id, key=lambda x: x[:2] + x[2:])
        for student_id in keep_id:
            data_for_id = df_question[df_question['student_id'] == student_id]
            answer = data_for_id['answer'].iloc[0]
            student_name = data_for_id['student_name'].iloc[0]

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

            # Retrieve the previous student name
            prev_name = prev_student_names.get(student_id, None)
            if prev_name:
                temp[student_id]['student_name'] = prev_name

            temp[student_id]['answers'].append({
                'question': question,
                'answer': answer,
                'comparison_data': df_bm[['snippet', 'link']].to_dict(orient='records'),
                'percentage': percentage,
                'question_text': question_text
            })

            prev_student_names[student_id] = student_name

            if not student_name and 'student_name' in temp[student_id]:
                temp[student_id]['student_name'] = prev_student_names[student_id]

            if not student_name:
                temp[student_id]['answers'].append({
                    'question': question,
                    'percentage': percentage
                })
            df_bm_dict[question] = df_bm

    response_data = {
        'question': list_q,
        'data': list(temp.values())
    }

    return response_data, 200
