from BM25 import BM25
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from app import mongo, perform_spell_correction, google_search
import re
from sklearn.metrics.pairwise import cosine_similarity

db = mongo.db

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


class CompareController:

    @staticmethod
    def comparingStudentAnswer():
        global keep_id, sorted_data_return, new_dict
        data = db.Question.find({'course_id': 3})
        df = pd.DataFrame(data, columns=['_id', 'course_id', 'question', 'student_id', 'student_name', 'answer'])
        question = df['question']
        list_q = list(set(question))
        list_q = sorted(list_q, key=lambda x: int(x.split('-')[0][1:]))
        temp = {}
        # vectorizer = TfidfVectorizer()
        # corpus = df['answer'].tolist()
        # vectorizer.fit(corpus)
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
                    # answer_vector = vectorizer.transform([answer])
                    # result_vectors = vectorizer.transform(df_question['answer'])
                    # scores = cosine_similarity(answer_vector, result_vectors)
                    # scores = scores[0]
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

    @staticmethod
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


