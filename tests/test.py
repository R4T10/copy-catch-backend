import unittest
from services.course_service import CourseService
from bson import ObjectId
from flask import jsonify, request
from flask import Flask  # Import Flask

# Create a Flask app (you might need to adjust this import based on your project structure)
app = Flask(__name__)

from app import db
from models.course import Course


@app.route('/get_course_list', methods=['POST'])
def getCourseList():
    course_service = CourseService()
    response_data, status_code = course_service.get_course_list()
    return response_data, status_code


@app.route('/adding_course', methods=['POST'])
def addCourse():
    course_service = CourseService()
    try:
        response_data, status_code = course_service.adding_course()
        return response_data, status_code
    except Exception as e:
        return str(e), 409


@app.route('/delete_course', methods=['POST'])
def deleteCourse():
    course_service = CourseService()
    try:
        response_data, status_code = course_service.delete_course()
        return response_data, status_code
    except Exception as e:
        return str(e), 404


@app.route('/edit_course', methods=['POST'])
def editCourse():
    course_service = CourseService()
    try:
        response_data, status_code = course_service.edit_course()
        return response_data, status_code
    except Exception as e:
        return str(e), 409


class TestApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_get_course_list(self):
        professor_email = 'krit_tipnuan@cmu.ac.th'

        # Use the test client to make a POST request to the route
        response = self.app.post('/get_course_list', data={'professor_email': professor_email})

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # You can also check the content of the response if needed
        response_data = response.get_json()
        print(response_data)

    def test_add_course_success(self):
        course = {
            'course_id': '890012',
            'course_name': 'TEST',
            'year': '2021',
            'examination': 'Midterm',
            'professor_email': 'krit_tipnuan@cmu.ac.th'
        }
        # Use the test client to make a POST request to the route
        response = self.app.post('/adding_course', data=course)

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # You can also check the content of the response if needed
        response_data = response.get_json()
        print(response_data)

    def test_add_course_unsuccess(self):
        course = {
            'course_id': '890012',
            'course_name': 'TEST',
            'year': '2021',
            'examination': 'Midterm',
            'professor_email': 'krit_tipnuan@cmu.ac.th'
        }
        # Use the test client to make a POST request to the route
        response = self.app.post('/adding_course', data=course)

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 409)
        print(response.data)


if __name__ == '__main__':
    unittest.main()
