from services.login_service import LoginService


class LoginController:
    @staticmethod
    def navigateLogin():
        login_service = LoginService()
        response_data, status_code = login_service.login()
        return response_data, status_code

    @staticmethod
    def codeCallback():
        login_service = LoginService()
        response = login_service.callback()
        return response.data, response.status_code

    @staticmethod
    def getUserInfo():
        login_service = LoginService()
        response = login_service.userinfo()
        return response.data, response.status_code
