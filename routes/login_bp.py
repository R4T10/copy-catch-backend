from flask import Blueprint
from controllers.loginController import LoginController


class LoginBlueprint:
    login_bp = Blueprint('login_bp', __name__)
    login_bp.route('/login', methods=['GET'])(LoginController.login)
    login_bp.route('/callback', methods=['POST'])(LoginController.callback)
    login_bp.route('/userinfo')(LoginController.userinfo)
