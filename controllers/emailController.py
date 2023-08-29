from services.email_service import EmailService


class EmailController:
    @staticmethod
    def sendEmail():
        email_service = EmailService()
        response_data, status_code = email_service.send_email()
        return response_data, status_code
