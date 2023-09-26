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


class CompareService:
    @staticmethod
    def comparingStudentAnswer():
        global keep_id, sorted_data_return, new_dict, df_bm, comparison_data
        # Request the course id from frontend
        course_id = request.args.get('id')
        # Transform it to be Object ID
        course_id = ObjectId(course_id)
        # Using Object ID to search the data regarding that course
        data = db.Question.find({'course_id': course_id})
        # Create the data frame and using the data that we get from the database
        df = pd.DataFrame(data, columns=['_id', 'course_id', 'question', 'question_text', 'student_id', 'student_name',
                                         'answer'])
        # Store the list of question list from data frame here
        question = df['question']
        # Transform the data we have to be set and to be list because what we get is still in data frame format
        list_q = list(set(question))

        # Sort the question number from the number after text "Q"
        list_q = sorted(list_q, key=lambda x: int(x.split('-')[0][1:]))
        temp = {}
        df_bm_dict = {}
        prev_student_names = {}
        # Getting Tf-idf method from lib
        vectorizer = TfidfVectorizer()
        # Get the data from data frame then make it to be list be for
        corpus = df['answer'].tolist()
        # Transform the data into TfidfVectorizer which also calculate the term frequencies (Tf) and inverse document frequencies (idf)
        vectorizer.fit(corpus)
        # Read the question number in list
        for question in list_q:
            # Match the data and get it from the data frame
            keep = df[df['question'] == question]
            # Get the question text related to the question number
            question_text = keep['question_text'].iloc[0]
            print(question_text)
            # Create the data frame using the data that we get from matching by using question number
            df_question = pd.DataFrame(data=keep)
            print(df_question)
            # Store the list of student id from data frame here
            keep_id = keep['student_id']
            # Sort the student id from the first 2 number and last 2 number
            keep_id = sorted(keep_id, key=lambda x: x[:2] + x[2:])
            # Read student id in list
            for student_id in keep_id:
                # Match the data from the student id
                data_for_id = df_question[df_question['student_id'] == student_id]
                # Get answer from that student id to be base for using to comparing
                answer = data_for_id['answer'].iloc[0]
                # Get the student name from that student id
                student_name = data_for_id['student_name'].iloc[0]
                # Check that in that question number this student have the answer or not
                if answer != 'null':
                    # Create the data frame using the data that we get from matching by using question number
                    df_bm = pd.DataFrame(data=df_question)
                    # Transform the answer into TfidfVectorizer which transform method will make it into number
                    answer_vector = vectorizer.transform([answer])
                    # Transform the list of answer into TfidfVectorizer which transform method will make it into number which mean this value will have list of number
                    result_vectors = vectorizer.transform(df_question['answer'])
                    # Use cosine method to determine how similar two documents are based on their term frequencies.
                    scores = cosine_similarity(answer_vector, result_vectors)
                    # Get list of the score
                    scores = scores[0]
                    # Store in to new column call tfidf
                    df_bm['tfidf'] = list(scores)
                    # Rank the data from tfidf column from the highest number to lowest
                    df_bm['rank'] = df_bm['tfidf'].rank(ascending=False)
                    # Showing the data only 4 data
                    df_bm = df_bm.nlargest(columns='tfidf', n=4)
                    # Find the highest number from tfidf column
                    max_score = df_bm['tfidf'].max()
                    percentage_scores = (df_bm['tfidf'] / max_score) * 100
                    percentage_scores = round(percentage_scores.apply(lambda x: 0 if x < 10 else x), 2)
                    comparison_data = []

                    for i, entry in enumerate(df_bm['student_name']):
                        comparison_data.append({
                            'student_name': entry,
                            'question_text': df_bm['question'].iloc[i],
                            'answer': df_bm['answer'].iloc[i],
                            'student_id': df_bm['student_id'].iloc[i],
                            'percentage': percentage_scores.iloc[i]
                        })

                    # Calculate the highest percentage of similarity by using the first number and second number
                    percentage = round((df_bm['tfidf'].iloc[1] / df_bm['tfidf'].iloc[0]) * 100, 2)
                    # Check if the percentage is higher than 50
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

    @staticmethod
    def searchGoogle():
        global results, df_bm, comparison_data
        course_id = request.args.get('id')
        course_id = ObjectId(course_id)
        data = db.Question.find({'course_id': course_id})
        df = pd.DataFrame(data, columns=['_id', 'course_id', 'question', 'question_text', 'student_id', 'student_name',
                                         'answer'])

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
                    comparison_data = []
                    percentage_scores = round((df_bm['tfidf'] * 100), 2)
                    for i, entry in enumerate(df_bm['snippet']):
                        comparison_data.append({
                            'snippet': entry,
                            'link': df_bm['link'].iloc[i],
                            'percentage': round(percentage_scores.iloc[i], 2)
                        })

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
                prev_name = prev_student_names.get(student_id, None)
                if prev_name:
                    temp[student_id]['student_name'] = prev_name

                temp[student_id]['answers'].append({
                    'question': question,
                    'answer': answer,
                    'comparison_data': comparison_data,
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
