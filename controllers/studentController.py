from flask import request, redirect, jsonify
from bson import ObjectId
from app import db


class StudentController:
    @staticmethod
    def get_student_list():
        course_id = request.args.get('id')
        course_id = ObjectId(course_id)
        data = db.Student.find({'course_id': course_id})
        print(data)
        students = []
        for student in data:
            try:
                student_data = {
                    'student_id': student['student_id'],
                    'student_name': student['student_name'],
                    'student_mail': student['student_mail']
                }
                students.append(student_data)
            except Exception as e:
                print("Error:", e)
        sorted_students = sorted(students, key=lambda x: (x['student_id'][:2], x['student_id'][-3:]))
        return jsonify(sorted_students), 200

    @staticmethod
    def update_email():
        student_id = request.form['student_id']
        student_name = request.form['student_name']
        mail = request.form['mail']
        course_id = request.form['course_id']
        course_id = ObjectId(course_id)
        print(course_id)
        print(student_name)
        print(student_id)
        print(mail)
        result = db.Student.update_many(
            {'student_id': student_id, 'student_name': student_name},
            {'$set': {'student_mail': mail}}
        )

        if result.modified_count > 0:
            return 'Update success', 200
        else:
            return 'Student not found', 404
