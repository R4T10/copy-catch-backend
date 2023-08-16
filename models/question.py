class Question:
    def __init__(self, course_id, question, question_text, student_id, student_name, answer):
        self.course_id = course_id
        self.question = question
        self.question_text = question_text
        self.student_id = student_id
        self.student_name = student_name
        self.answer = answer

    def to_dict(self):
        return {
            'course_id': self.course_id,
            'question': self.question,
            'question_text': self.question_text,
            'student_id': self.student_id,
            'student_name': self.student_name,
            'answer': self.answer
        }
