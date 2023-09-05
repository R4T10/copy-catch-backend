from services.student_service import StudentService


class StudentController:
    @staticmethod
    def getStudentList():
        student_service = StudentService()
        try:
            response_data, status_code = student_service.get_student_list()
            return response_data, status_code
        except Exception as e:
            return str(e), 409

    @staticmethod
    def updateEmail():
        student_service = StudentService()
        try:
            response_data, status_code = student_service.update_email()
            return response_data, status_code
        except Exception as e:
            return str(e), 409
