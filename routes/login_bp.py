from flask import Blueprint
from controllers.loginController import LoginController


class LoginBlueprint:
    login_bp = Blueprint('login_bp', __name__)
    login_bp.route('/login', methods=['GET'])(LoginController.navigateLogin)
    login_bp.route('/callback', methods=['POST'])(LoginController.codeCallback)
    login_bp.route('/userinfo')(LoginController.getUserInfo)
