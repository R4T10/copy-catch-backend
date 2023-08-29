from services.upload_service import UploadService


class UploadController:

    @staticmethod
    def fileUpload():
        upload_service = UploadService()
        response_data, status_code = upload_service.upload()
        return response_data, status_code

    @staticmethod
    def fileReUpload():
        upload_service = UploadService()
        response_data, status_code = upload_service.reupload()
        return response_data, status_code
