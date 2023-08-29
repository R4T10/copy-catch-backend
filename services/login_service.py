from flask import request, redirect, jsonify
import requests

# Replace these values with your actual client information
CLIENT_ID = 'udnnChw9fh77821R00WKBrCHNFhPs0FPuDfZJ44v'
CLIENT_SECRET = 'EHSqJjAagDayw72cMRK79UTrNvPEXcg56Ae4Jn9D'
REDIRECT_URI = 'http://localhost:3000/course_list'
API_BASE_URL = 'https://misapi.cmu.ac.th'
AUTH_ENDPOINT = 'https://oauth.cmu.ac.th/v1/Authorize.aspx'
TOKEN_ENDPOINT = 'https://oauth.cmu.ac.th/v1/GetToken.aspx'


class LoginService:
    @staticmethod
    def login():
        login_url = 'https://oauth.cmu.ac.th/v1/Authorize.aspx?response_type=code&client_id=udnnChw9fh77821R00WKBrCHNFhPs0FPuDfZJ44v&redirect_uri=http://localhost:3000/course_list&scope=cmuitaccount.basicinfo'
        return login_url, 200
    @staticmethod
    def callback():
        code = request.form['code']
        if not code:
            return 'Authorization code not received.'

        data = {
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'authorization_code',
        }

        response = requests.post(TOKEN_ENDPOINT, data=data)
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens.get('access_token')
            if access_token:
                return jsonify({'access_token': access_token})
        return jsonify({'message': 'Failed to get access token.'})

    @staticmethod
    def userinfo():
        access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not access_token:
            return 'Access token not provided.', 401

        userinfo_endpoint = 'https://misapi.cmu.ac.th/cmuitaccount/v1/api/cmuitaccount/basicinfo'

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
        }

        response = requests.get(userinfo_endpoint, headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            return jsonify(user_info)
        else:
            return jsonify({'message': 'Failed to fetch user information'}), 404
