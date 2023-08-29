from flask import Blueprint
from controllers.studentController import StudentController


class StudentBlueprint:
    student_bp = Blueprint('student_bp', __name__)
    student_bp.route('/get_student_list', methods=['GET'])(StudentController.getStudentList)
    student_bp.route('/update_email', methods=['POST'])(StudentController.updateEmail)