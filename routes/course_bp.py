from flask import Blueprint
from controllers.courseController import CourseController


class CourseBlueprint:
    course_bp = Blueprint('course_bp', __name__)
    course_bp.route('/get_course_list', methods=['POST'])(CourseController.getCourseList)
    course_bp.route('/adding_course', methods=['POST'])(CourseController.addCourse)
    course_bp.route('/delete_course', methods=['POST'])(CourseController.deleteCourse)
    course_bp.route('/edit_course', methods=['POST'])(CourseController.editCourse)
