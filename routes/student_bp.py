from flask import Blueprint
from controllers.studentController import StudentController


class StudentBlueprint:
    student_bp = Blueprint('student_bp', __name__)
    student_bp.route('/get_student_list', methods=['GET'])(StudentController.get_student_list)
