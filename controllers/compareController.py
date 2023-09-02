from flask import request
from services.compare_service import CompareService


class CompareController:
    @staticmethod
    def getComparingStudentAnswer():
        compare_service = CompareService()
        try:
            response_data, status_code = compare_service.comparingStudentAnswer()
            return response_data, status_code
        except Exception as e:
            print(e)
            return str(e), 404

    @staticmethod
    def getSearchGoogle():
        compare_service = CompareService()
        # try:
        response_data, status_code = compare_service.searchGoogle()
        return response_data, status_code
        # # except Exception as e:
        #     print(e)
        #     return str(e), 404
