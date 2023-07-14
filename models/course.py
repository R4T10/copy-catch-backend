class Course:
    def __init__(self, course_id, course_name, year, examination, professor,file, ):
        self.course_id = course_id
        self.course_name = course_name
        self.year = year
        self.examination = examination
        self.professor = professor
        self.file = file

    def to_dict(self):
        return {
            'course_id': self.course_id,
            'course_name': self.course_name,
            'year': self.year,
            'examination': self.examination,
            'professor': self.professor,
            'file': self.file
        }
