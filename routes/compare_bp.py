from flask import Blueprint
from controllers.compareController import CompareController


class CompareBlueprint:
    compare_bp = Blueprint('compare_bp', __name__, url_prefix='/compare')
    compare_bp.route('/comparing_student', methods=['GET'])(CompareController.comparingStudentAnswer())
    compare_bp.route('/search_google', methods=['GET'])(CompareController.searchGoogle())
