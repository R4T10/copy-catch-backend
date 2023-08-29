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
        response_data, status_code = course_service.adding_course()
        return response_data, status_code

    @staticmethod
    def deleteCourse():
        course_service = CourseService()
        response_data, status_code = course_service.delete_course()
        return response_data, status_code

    @staticmethod
    def editCourse():
        course_service = CourseService()
        response_data, status_code = course_service.edit_course()
        return response_data, status_code
