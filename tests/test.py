import unittest

from flask_mail import Mail

from services.course_service import CourseService
from bson import ObjectId
from flask import jsonify, request
from flask import Flask  # Import Flask

from services.email_service import EmailService
from services.student_service import StudentService
from services.upload_service import UploadService

# Create a Flask app (you might need to adjust this import based on your project structure)
app = Flask(__name__)
mail = Mail(app)
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


@app.route('/send_email', methods=['POST'])
def sendEmail():
    email_service = EmailService()
    try:
        response_data, status_code = email_service.send_email()
        return response_data, status_code
    except Exception as e:
        return str(e), 409


@app.route('/get_student_list', methods=['GET'])
def getStudentList():
    student_service = StudentService()
    try:
        response_data, status_code = student_service.get_student_list()
        return response_data, status_code
    except Exception as e:
        return str(e), 409


@app.route('/update_email', methods=['POST'])
def updateEmail():
    student_service = StudentService()
    try:
        response_data, status_code = student_service.update_email()
        return response_data, status_code
    except Exception as e:
        return str(e), 409


@app.route('/reupload', methods=['POST'])
def fileReUpload():
    upload_service = UploadService()
    try:
        response_data, status_code = upload_service.reupload()
        return response_data, status_code
    except TypeError as e:
        return str(e), 400
    except ValueError as e:
        return str(e), 400


class TestApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_get_course_list(self):
        professor_email = {'professor_email': 'krit_tipnuan@cmu.ac.th'}

        response = self.app.post('/get_course_list', data=professor_email)

        self.assertEqual(response.status_code, 200)

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

        response = self.app.post('/adding_course', data=course)

        self.assertEqual(response.status_code, 200)

        response_data = response.get_json()
        print(response_data)

    def test_add_course_unsuccess_course_duplicated(self):
        course = {
            'course_id': '890012',
            'course_name': 'TEST',
            'year': '2021',
            'examination': 'Midterm',
            'professor_email': 'krit_tipnuan@cmu.ac.th'
        }

        response = self.app.post('/adding_course', data=course)

        self.assertEqual(response.status_code, 409)
        print(response.data)

    def test_edit_course_success(self):
        course = {
            'id': '64f87ddc8944a81671419f40',
            'course_id': '890012',
            'course_name': 'TEST',
            'year': '2021',
            'examination': 'Final',
            'professor_email': 'krit_tipnuan@cmu.ac.th'
        }

        response = self.app.post('/edit_course', data=course)

        self.assertEqual(response.status_code, 200)
        print(response.data)

    def test_edit_course_unsuccess_wrong_object_id(self):
        course = {
            'id': '74f37dd289f4ae1671419f40',
            'course_id': '890012',
            'course_name': 'TEST',
            'year': '2021',
            'examination': 'Final',
            'professor_email': 'krit_tipnuan@cmu.ac.th'
        }

        response = self.app.post('/edit_course', data=course)

        self.assertEqual(response.status_code, 409)
        print(response.data)

    def test_edit_course_unsuccess_course_duplicated(self):
        course = {
            'id': '64f87ddc8944a81671419f40',
            'course_id': '890012',
            'course_name': 'TEST',
            'year': '2021',
            'examination': 'Final',
            'professor_email': 'krit_tipnuan@cmu.ac.th'
        }

        response = self.app.post('/edit_course', data=course)

        self.assertEqual(response.status_code, 409)
        print(response.data)

    def test_send_email_success(self):
        data = {
            'student_id': '622115513',
            'course_id': '890012',
            'course_name': 'TEST',
            'examination': 'Final',
        }

        response = self.app.post('/send_email', data=data)

        self.assertEqual(response.status_code, 200)
        print(response.data)

    def test_send_email_unsuccess_student_not_found(self):
        data = {
            'student_id': '662115501',
            'course_id': '890012',
            'course_name': 'TEST',
            'examination': 'Final',
        }

        response = self.app.post('/send_email', data=data)

        self.assertEqual(response.status_code, 409)
        print(response.data)

    def test_send_email_unsuccess_student_email_not_found(self):
        data = {
            'student_id': '632115501',
            'course_id': '890012',
            'course_name': 'TEST',
            'examination': 'Final',
        }

        response = self.app.post('/send_email', data=data)

        self.assertEqual(response.status_code, 409)
        print(response.data)

    def test_get_student_list_success(self):
        course_id = '64f87ddc8944a81671419f40'
        response = self.app.get(f'/get_student_list?id={course_id}')
        self.assertEqual(response.status_code, 200)
        print(response.data)

    def test_get_student_list_unsuccess_wrong_object_id(self):
        course_id = '74f37dd289f4ae1671419f40'
        response = self.app.get(f'/get_student_list?id={course_id}')
        self.assertEqual(response.status_code, 409)
        print(response.data)

    def test_update_student_email_success(self):
        student_id = {'student_id': '632115001',
                      'mail': 'test@cmu.ac.th'}
        response = self.app.post('/update_email', data=student_id)
        self.assertEqual(response.status_code, 200)
        print(response.data)

    def test_update_student_email_unsuccess_cant_find_student_id(self):
        student_id = {'student_id': '682115001',
                      'mail': 'test@cmu.ac.th'}
        response = self.app.post('/update_email', data=student_id)
        self.assertEqual(response.status_code, 409)
        print(response.data)

    def test_reupload_success(self):
        response = self.app.post('/reupload', data=data)
        self.assertEqual(response.status_code, 409)
        print(response.data)


if __name__ == '__main__':
    unittest.main()
