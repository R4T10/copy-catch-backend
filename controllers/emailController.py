from flask import request, redirect, jsonify
from flask_mail import Mail, Message
from app import mail
from app import db


class EmailController:
    @staticmethod
    def send_email():
        try:
            sender_email = 'copy_catch@hotmail.com'
            receive_name = request.form['receiver_name']

            student = db.Student.find_one({'student_name': receive_name})

            if student:
                student_email = student.get('student_mail')
                if student_email != 'None':
                    subject = 'SE331 PJ'
                    message = 'THis is from Krit'

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
