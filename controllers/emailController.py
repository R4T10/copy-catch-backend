from services.email_service import EmailService


class EmailController:
    @staticmethod
    def sendEmail():
        email_service = EmailService()
        try:
            response_data, status_code = email_service.send_email()
            return response_data, status_code
        except Exception as e:
            return str(e), 409
