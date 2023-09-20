from bson import ObjectId
from flask import jsonify, request

from app import db
from models.course import Course


class CourseService:
    @staticmethod
    def get_course_list():
        professor_email = request.form['professor_email']
        data = db.Courses.find({'professor_email': professor_email})
        courses = []

        for course in data:
            courses.append({
                'id': str(course['_id']),
                'course_id': course['course_id'],
                'course_name': course['course_name'],
                'year': course['year'],
                'examination': course['examination'],
                'professor_email': course['professor_email'],
                'file': course['file']
            })
        courses = courses[::-1]
        return jsonify(courses), 200

    @staticmethod
    def adding_course():
        course_id = request.form['course_id']
        course_name = request.form['course_name']
        year = request.form['year']
        examination = request.form['examination']
        professor_email = request.form['professor_email']
        file = False
        existing_course = db.Courses.find_one({
            'course_id': course_id,
            'year': year,
            'examination': examination
        })

        if existing_course:
            raise ValueError("Duplicate course found in the database")
        course = Course(course_id=course_id, course_name=course_name, year=year,
                        examination=examination, professor_email=professor_email, file=file)
        question_dict = course.to_dict()
        db.Courses.insert_one(question_dict)
        added_course = db.Courses.find_one({
            'course_id': course_id,
            'course_name': course_name,
            'year': year,
            'examination': examination
        })
        if added_course:
            added_course['_id'] = str(added_course['_id'])
        return jsonify(added_course), 200

    @staticmethod
    def delete_course():
        course_id = request.form.get('id')
        id = ObjectId(course_id)
        existing_course = db.Courses.find_one({
            '_id': id,
        })
        if not existing_course:
            raise Exception("Course not found")

        db.Courses.delete_one({'_id': ObjectId(course_id)})
        db.Question.delete_many({'course_id': ObjectId(course_id)})
        return jsonify({'message': 'Delete success'}), 200

    @staticmethod
    def edit_course():
        id = request.form.get('id')
        id = ObjectId(id)
        course_id = request.form['course_id']
        course_name = request.form['course_name']
        year = request.form['year']
        examination = request.form['examination']
        professor_email = request.form['professor_email']
        check_id = db.Courses.find_one({
            '_id': id,
        })
        if not check_id:
            raise Exception("Can't find this Object ID in database")
        existing_course = db.Courses.find_one({
            'course_id': course_id,
            'year': year,
            'examination': examination
        })

        if existing_course:
            raise ValueError("Duplicate course found in the database")

        db.Courses.update_one(
            {'_id': id},
            {'$set': {
                'course_id': course_id,
                'course_name': course_name,
                'year': year,
                'examination': examination,
                'professor_email': professor_email
            }}
        )

        after_add = db.Courses.find_one({
            'course_id': course_id,
            'course_name': course_name,
            'year': year,
            'examination': examination,
            'professor_email': professor_email
        })

        if after_add:
            after_add['_id'] = str(after_add['_id'])

        return jsonify(after_add), 200
