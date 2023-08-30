from flask import request, redirect, jsonify
from flask_mail import Mail, Message
from app import mail
from app import db


class EmailService:
    @staticmethod
    def send_email():
        try:
            sender_email = 'copy_catch@hotmail.com'
            student_id = request.form['student_id']

            student = db.Student.find_one({'student_id': student_id})

            if student:
                student_email = student.get('student_mail')
                if student_email != 'None':
                    subject = 'Copy-Catch detected plagiarism from your answer'
                    message = ('Dear studentname, ' \
                               'Copy-Catch detected plagiarism from your answer of courseid coursename examinationtype exam.' \
                               '' \
                               'You are asked to contact Professor. professorname to discuss about this matter.' \
                               '' \
                               'Yours sincerely,')

                    msg = Message(subject, recipients=[student_email], sender=sender_email)
                    msg.body = message

                    mail.send(msg)

                    return jsonify({'message': 'Email sent successfully'}), 200

                else:
                    return jsonify({'message': 'Student email not found'}), 404
            else:
                return jsonify({'message': 'Student not found'}), 404
        except Exception as e:
            return f'Error sending email: {str(e)}', 500
