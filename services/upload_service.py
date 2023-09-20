from bson import ObjectId
from flask import Flask, request, jsonify
import io
import zipfile
import re

from app import spellchecker, mongo
from models.question import Question
from models.student import Student

db = mongo.db


def perform_spell_correction(text):
    corrected_text = []
    words = text.split()
    for word in words:
        corrected_word = spellchecker.correction(word)
        corrected_text.append(corrected_word)
    spell_corr = list(filter(None, corrected_text))
    return ' '.join(spell_corr)


class UploadService:

    @staticmethod
    def upload():
        # global question_text_dict_keep
        file = request.files.get('file')
        course_id = request.form['id']
        course_id = ObjectId(course_id)
        file_stream = io.BytesIO(file.stream.read())
        try:
            with zipfile.ZipFile(file.stream) as zip_file:
                pass
        except zipfile.BadZipFile:
            raise TypeError("Invalid file type")
        # question_text_dict_keep = ''
        question_text_dict = {}
        with zipfile.ZipFile(file_stream, 'r') as zip_file:
            student_ids = set()
            student_list = set()
            for file_name in zip_file.namelist():
                if '/' in file_name:
                    folder_names = file_name.split('/', 1)[0]
                    folder_names = folder_names.replace('.', '').replace(' ', '')
                    if folder_names.startswith('Q'):
                        student_id = file_name.split('/')[1].split()[0]
                        if student_id == 'Question':
                            inside_question = zip_file.read(file_name).decode('utf-8')
                            inside_question = inside_question.lower()
                            question_text = ' '.join(inside_question.split())
                            question_text_dict[folder_names] = question_text
                        # else:
                        #     question_text_dict[folder_names] = ''
            print(question_text_dict)
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
                            # print(folder_names)
                            question_text = question_text_dict.get(folder_names, '')
                            print("QUESTION TEXT")
                            print(question_text)
                            question = Question(course_id=course_id, question=folder_names, question_text=question_text,
                                                student_name=student_name,
                                                student_id=student_id, answer=text_response)
                            question_dict = question.to_dict()
                            db.Question.insert_one(question_dict)
                            student_list.add((student_id, student_name))
                            print(student_list)
                    else:
                        raise ValueError("Invalid file format")
            all_questions = db.Question.distinct('question')

            for student_p in student_list:
                student_id_p = student_p[0]
                student_name_p = student_p[1]
                check_student = db.Student.find_one({'student_id': student_id_p})
                if check_student:
                    student_mail = check_student.get('student_mail')
                    student = Student(course_id=course_id, student_id=student_id_p, student_name=student_name_p,
                                      student_mail=student_mail)
                else:
                    student = Student(course_id=course_id, student_id=student_id_p, student_name=student_name_p,
                                      student_mail='None')
                student_dict = student.to_dict()
                db.Student.insert_one(student_dict)

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
                            'question_text': question_text,
                            'student_name': 'null',
                            'student_id': student_id,
                            'answer': 'null'
                        }
                        db.Question.insert_one(question_data)
            db.Courses.update_one(
                {'_id': ObjectId(course_id)},
                {'$set': {'file': True}}
            )

        return jsonify({'message': 'Upload success'}), 200

    @staticmethod
    def reupload():
        file = request.files.get('file')
        course_id = request.form['id']
        course_id = ObjectId(course_id)
        db.Question.delete_many({'course_id': ObjectId(course_id)})
        db.Student.delete_many({'course_id': ObjectId(course_id)})
        file_stream = io.BytesIO(file.stream.read())

        try:
            with zipfile.ZipFile(file.stream) as zip_file:
                pass
        except zipfile.BadZipFile:
            raise TypeError("Invalid file type")
        question_text_dict = {}
        with zipfile.ZipFile(file_stream, 'r') as zip_file:
            student_ids = set()
            student_list = set()
            for file_name in zip_file.namelist():
                if '/' in file_name:
                    folder_names = file_name.split('/', 1)[0]
                    folder_names = folder_names.replace('.', '').replace(' ', '')
                    if folder_names.startswith('Q'):
                        student_id = file_name.split('/')[1].split()[0]
                        if student_id == 'Question':
                            inside_question = zip_file.read(file_name).decode('utf-8')
                            inside_question = inside_question.lower()
                            question_text = inside_question.strip()
                            question_text_dict[folder_names] = question_text
                            print(question_text)
                        # else:
                        #     question_text_dict[folder_names] = ''
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
                            question_text = question_text_dict.get(folder_names, '')
                            question = Question(course_id=course_id, question=folder_names, question_text=question_text,
                                                student_name=student_name,
                                                student_id=student_id, answer=text_response)
                            question_dict = question.to_dict()
                            student_list.add((student_id, student_name))
                            db.Question.insert_one(question_dict)
                    else:
                        raise ValueError("Invalid file format")
            all_questions = db.Question.distinct('question')
            for student_p in student_list:
                student_id_p = student_p[0]
                student_name_p = student_p[1]
                check_student = db.Student.find_one({'student_id': student_id_p})
                if check_student:
                    student_mail = check_student.get('student_mail')
                    student = Student(course_id=course_id, student_id=student_id_p, student_name=student_name_p,
                                      student_mail=student_mail)
                else:
                    student = Student(course_id=course_id, student_id=student_id_p, student_name=student_name_p,
                                      student_mail='None')
                student_dict = student.to_dict()
                db.Student.insert_one(student_dict)

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
                            'question_text': question_text,
                            'student_name': 'null',
                            'student_id': student_id,
                            'answer': 'null'
                        }
                        db.Question.insert_one(question_data)
            db.Courses.update_one(
                {'_id': ObjectId(course_id)},
                {'$set': {'file': True}}
            )
        return jsonify({'message': 'Upload success'}), 200
