from services.upload_service import UploadService


class UploadController:

    @staticmethod
    def fileUpload():
        upload_service = UploadService()
        try:
            response_data, status_code = upload_service.upload()
            return response_data, status_code
        except TypeError as e:
            return str(e), 400
        except ValueError as e:
            return str(e), 400

    @staticmethod
    def fileReUpload():
        upload_service = UploadService()
        try:
            response_data, status_code = upload_service.reupload()
            return response_data, status_code
        except TypeError as e:
            return str(e), 400
        except ValueError as e:
            return str(e), 400
