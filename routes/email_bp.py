from flask import Blueprint
from controllers.emailController import EmailController


class EmailBlueprint:
    email_bp = Blueprint('email_bp', __name__)
    email_bp.route('/send_email', methods=['POST'])(EmailController.sendEmail)
