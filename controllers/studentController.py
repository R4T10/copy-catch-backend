from services.student_service import StudentService


class StudentController:
    @staticmethod
    def getStudentList():
        student_service = StudentService()
        response_data, status_code = student_service.get_student_list()
        return response_data, status_code

    @staticmethod
    def updateEmail():
        student_service = StudentService()
        response_data, status_code = student_service.update_email()
        return response_data, status_code
