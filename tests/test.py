import unittest

from flask_mail import Mail
import io
import zipfile
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
        return str(e), 409


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

        expected_message = b'Duplicate course found in the database'
        self.assertEqual(response.data, expected_message)

        print(response.data)

    def test_edit_course_success(self):
        course = {
            'id': '64f98bba3e3e7824b9af475e',
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

        expected_message = b"Can't find this Object ID in database"
        self.assertEqual(response.data, expected_message)
        print(response.data)

    def test_edit_course_unsuccess_course_duplicated(self):
        course = {
            'id': '64f98bba3e3e7824b9af475e',
            'course_id': '890012',
            'course_name': 'TEST',
            'year': '2021',
            'examination': 'Final',
            'professor_email': 'krit_tipnuan@cmu.ac.th'
        }

        response = self.app.post('/edit_course', data=course)

        self.assertEqual(response.status_code, 409)

        expected_message = b"Duplicate course found in the database"
        self.assertEqual(response.data, expected_message)
        print(response.data)

    def test_delete_course_success(self):
        course = {
            'id': '64f989c804fc9f0939ee940c',
        }

        response = self.app.post('/delete_course', data=course)

        self.assertEqual(response.status_code, 200)

        response_data = response.get_json()
        expected_message = {'message': 'Delete success'}
        self.assertEqual(response_data, expected_message)
        print(response.data)

    def test_delete_course_unsuccess_course_not_found(self):
        course = {
            'id': '64f989c804fc9f0939ee940c',
        }

        response = self.app.post('/delete_course', data=course)

        self.assertEqual(response.status_code, 409)

        expected_message = b'Course not found'
        self.assertEqual(response.data, expected_message)
        print(response.data)

    def test_send_email_success(self):
        data = {
            'student_id': '522115001',
            'course_id': '890012',
            'course_name': 'TEST',
            'examination': 'Final',
        }

        response = self.app.post('/send_email', data=data)

        self.assertEqual(response.status_code, 200)

        response_data = response.get_json()
        expected_message = {'message': 'Email sent successfully'}
        self.assertEqual(response_data, expected_message)
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
        expected_message = b'Student not found'
        self.assertEqual(response.data, expected_message)
        print(response.data)

    def test_send_email_unsuccess_student_email_not_found(self):
        data = {
            'student_id': '522115002',
            'course_id': '890012',
            'course_name': 'TEST',
            'examination': 'Final',
        }

        response = self.app.post('/send_email', data=data)

        self.assertEqual(response.status_code, 409)

        expected_message = b'Student email not found'
        self.assertEqual(response.data, expected_message)
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

        expected_message = b"Can't find this Object ID in database"
        self.assertEqual(response.data, expected_message)
        print(response.data)

    def test_update_student_email_success(self):
        student_id = {'student_id': '632115001',
                      'mail': 'test@cmu.ac.th'}
        response = self.app.post('/update_email', data=student_id)

        self.assertEqual(response.status_code, 200)

        response_data = response.get_json()
        expected_message = {'message': 'Update success'}
        self.assertEqual(response_data, expected_message)
        print(response.data)

    def test_update_student_email_unsuccess_cant_find_student_id(self):
        student_id = {'student_id': '682115001',
                      'mail': 'test@cmu.ac.th'}
        response = self.app.post('/update_email', data=student_id)
        self.assertEqual(response.status_code, 409)

        expected_message = b"Student not found"
        self.assertEqual(response.data, expected_message)
        print(response.data)

    def test_reupload_success(self):
        with open('../utils/Dev-test.zip', 'rb') as zip_file:
            zip_content = zip_file.read()

        data = {
            'file': (io.BytesIO(zip_content), 'Dev-test.zip'),
            'id': '64f6d3283f8065124d93d61b'
        }

        response = self.app.post('/reupload', data=data)

        self.assertEqual(response.status_code, 200)

        response_data = response.get_json()
        expected_message = {'message': 'Upload success'}
        self.assertEqual(response_data, expected_message)
        print(response.data)
        print(response.data)

    def test_reupload_unsuccess_wrong_format(self):
        with open('../utils/student_answer.zip', 'rb') as zip_file:
            zip_content = zip_file.read()

        data = {
            'file': (io.BytesIO(zip_content), 'student_answer.zip'),
            'id': '64f6d3283f8065124d93d61b'
        }

        response = self.app.post('/reupload', data=data)

        self.assertEqual(response.status_code, 400)

        expected_message = b"Invalid file format"
        self.assertEqual(response.data, expected_message)
        print(response.data)

    def test_reupload_unsuccess_wrong_type(self):
        with open('../utils/student_answer.pdf', 'rb') as zip_file:
            zip_content = zip_file.read()

        data = {
            'file': (io.BytesIO(zip_content), 'student_answer.pdf'),
            'id': '64f6d3283f8065124d93d61b'
        }

        response = self.app.post('/reupload', data=data)

        self.assertEqual(response.status_code, 400)

        expected_message = b"Invalid file type"
        self.assertEqual(response.data, expected_message)
        print(response.data)


if __name__ == '__main__':
    unittest.main()
