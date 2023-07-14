from flask import Blueprint
from controllers.courseController import CourseController


class CourseBlueprint:
    course_bp = Blueprint('course_bp', __name__)
    course_bp.route('/get_course_list', methods=['GET'])(CourseController.get_course_list)
    course_bp.route('/adding_course', methods=['POST'])(CourseController.adding_course)
    course_bp.route('/delete_course', methods=['POST'])(CourseController.delete_course)
    course_bp.route('/edit_course', methods=['POST'])(CourseController.edit_course)
