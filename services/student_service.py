from flask import request, redirect, jsonify
from bson import ObjectId
from app import db


class StudentService:
    @staticmethod
    def get_student_list():
        course_id = request.args.get('id')
        course_id = ObjectId(course_id)
        check_course = db.Courses.find_one({'_id': course_id})
        if not check_course:
            raise Exception("Can't find this Object ID in database")

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
        sorted_students = sorted(students, key=lambda x: (x['student_id'][:2], x['student_id'][-3:]))
        return jsonify(sorted_students), 200

    @staticmethod
    def update_email():
        student_id = request.form['student_id']
        mail = request.form['mail']
        result = db.Student.update_many(
            {'student_id': student_id},
            {'$set': {'student_mail': mail}}
        )
        if result.modified_count > 0:
            return jsonify({'message': 'Update success'}), 200
        else:
            raise Exception('Student not found')
