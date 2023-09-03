from flask import request
from services.compare_service import CompareService


class CompareController:
    @staticmethod
    def getComparingStudentAnswer():
        compare_service = CompareService()
        response_data, status_code = compare_service.comparingStudentAnswer()
        return response_data, status_code


    @staticmethod
    def getSearchGoogle():
        compare_service = CompareService()
        response_data, status_code = compare_service.searchGoogle()
        return response_data, status_code
