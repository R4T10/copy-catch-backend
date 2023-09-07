from flask import request, redirect, jsonify
from flask_mail import Mail, Message
from app import mail
from app import db


class EmailService:
    @staticmethod
    def send_email():
        sender_email = 'copy_catch@hotmail.com'
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        course_name = request.form['course_name']
        examination = request.form['examination']
        student = db.Student.find_one({'student_id': student_id})
        if not student:
            raise Exception('Student not found')
        student_email = student.get('student_mail')
        student_name = student.get('student_name')
        if student_email == 'None':
            raise Exception('Student email not found')

        subject = 'Copy-Catch detected plagiarism from your answer'
        message = f'Dear {student_name}, \n\n' \
                  f'Copy-Catch detected plagiarism from your answer of {course_id} {course_name} {examination} exam.\n\n' \
                  f'You are asked to contact the professor to discuss this matter.\n\n' \
                  'Yours sincerely,'

        msg = Message(subject, recipients=[student_email], sender=sender_email)
        msg.body = message

        mail.send(msg)

        return jsonify({'message': 'Email sent successfully'}), 200
