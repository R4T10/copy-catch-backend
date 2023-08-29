from flask import Blueprint
from controllers.compareController import CompareController


class CompareBlueprint:
    compare_bp = Blueprint('compare_bp', __name__)
    compare_bp.route('/comparing_student', methods=['GET'])(CompareController.getComparingStudentAnswer)
    compare_bp.route('/search_google', methods=['GET'])(CompareController.getSearchGoogle)
