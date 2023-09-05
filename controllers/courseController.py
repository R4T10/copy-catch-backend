from services.course_service import CourseService


class CourseController:
    @staticmethod
    def getCourseList():
        course_service = CourseService()
        response_data, status_code = course_service.get_course_list()
        return response_data, status_code

    @staticmethod
    def addCourse():
        course_service = CourseService()
        try:
            response_data, status_code = course_service.adding_course()
            return response_data, status_code
        except ValueError as e:
            return str(e), 409

    @staticmethod
    def deleteCourse():
        course_service = CourseService()
        try:
            response_data, status_code = course_service.delete_course()
            return response_data, status_code
        except Exception as e:
            return str(e), 409

    @staticmethod
    def editCourse():
        course_service = CourseService()
        try:
            response_data, status_code = course_service.edit_course()
            return response_data, status_code
        except ValueError as e:
            return str(e), 409
        except Exception as e:
            return str(e), 409
