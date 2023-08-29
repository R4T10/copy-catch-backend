class Course:
    def __init__(self, course_id, course_name, year, examination, professor_email,file, ):
        self.course_id = course_id
        self.course_name = course_name
        self.year = year
        self.examination = examination
        self.professor_email = professor_email
        self.file = file

    def to_dict(self):
        return {
            'course_id': self.course_id,
            'course_name': self.course_name,
            'year': self.year,
            'examination': self.examination,
            'professor_email': self.professor_email,
            'file': self.file
        }
