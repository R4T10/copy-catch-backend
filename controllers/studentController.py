from flask import request, redirect, jsonify
from bson import ObjectId
from app import db


class StudentController:
    @staticmethod
    def get_student_list():
        course_id = request.args.get('id')
        course_id = ObjectId(course_id)
        data = db.Student.find({'course_id': course_id})

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
        print(students)  # Print the list before returning
        return jsonify(students), 200


