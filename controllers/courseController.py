from bson import ObjectId
from flask import jsonify, request

from app import db
from models.course import Course


class CourseController:
    @staticmethod
    def get_course_list():
        professor = request.form['name']
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

    @staticmethod
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

    @staticmethod
    def delete_course():
        course_id = request.form.get('id')
        db.Courses.delete_one({'_id': ObjectId(course_id)})
        db.Question.delete_many({'course_id': ObjectId(course_id)})
        return 'Delete success', 200

    @staticmethod
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
