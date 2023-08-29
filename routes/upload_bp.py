from flask import Blueprint
from controllers.uploadController import UploadController


class UploadBlueprint:
    upload_bp = Blueprint('upload_bp', __name__)
    upload_bp.route('/upload', methods=['POST'])(UploadController.fileUpload)
    upload_bp.route('/reupload', methods=['POST'])(UploadController.fileReUpload)