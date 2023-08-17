class Student:
    def __init__(self, course_id, student_id, student_name, student_mail):
        self.course_id = course_id
        self.student_id = student_id
        self.student_name = student_name
        self.student_mail = student_mail

    def to_dict(self):
        return {
            'course_id': self.course_id,
            'student_id': self.student_id,
            'student_name': self.student_name,
            'student_mail': self.student_mail
        }
