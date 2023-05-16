class Question:
    def __init__(self, course_id, all_question):
        self.course_id = course_id
        self.all_question = all_question

    def to_dict(self):
        return {
            'course_id': self.course_id,
            'all_question': self.all_question
        }