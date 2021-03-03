import requests


class TestLogin:

    my_login = "121"
    password = "112"
    main_url = 'http://localhost:5000/'

    def new(self):
        url = 'http://localhost:5000/new'
        result = requests.post(url, json={"login": self.my_login, "password": self.password})
        assert result.status_code == 201
        assert result.json()["message"] == 'New user created'

    def test_1login_failed(self):
        url = "".join((self.main_url, 'login'))
        result = requests.post(url, json={"password": self.password}, verify=False)
        assert result.status_code == 400
        assert result.json()["message"] == [{'login': ['Missing data for required field.']}]
        result = requests.post(url, json={"login": self.my_login}, verify=False)
        assert result.status_code == 400
        assert result.json()["message"] == [{'password': ['Missing data for required field.']}]
        result = requests.post(url, json={"login": "wrong", "password": self.password}, verify=False)
        assert result.status_code == 400
        assert result.json()["message"] == 'This login not exists'

    def test_2login_passed(self):
        result = requests.post(self.main_url + 'login', json={"login": self.my_login, "password": self.password}, verify=False)
        assert result.status_code == 200
        assert result.json()["message"] == "Please, send you pin code"

    def test_3login2_failed(self):
        result = requests.post(self.main_url + 'login2', json={"login": "zzzzzzzzzzzz", "code": "0000"})
        assert result.status_code == 400
        assert result.json()["message"] == "Not valid login"
        result = requests.post(self.main_url + 'login2', json={"login": self.my_login})
        assert result.status_code == 403
        assert result.json()["message"] == "Pin code not exist"

    def test_4login2_passed(self):
        result = requests.post(self.main_url + 'login2', json={"login": self.my_login, "code": "0000"})
        assert result.json()["message"] == "Authorization successful"
        assert result.status_code == 200
        global token
        token = result.json()["access_token"]
        assert len(result.json()["access_token"]) == 149
        global refresh_token
        refresh_token = result.json()["refresh_token"]
        assert len(result.json()["refresh_token"]) == 151

    def test_5change_failed(self):
        url = self.main_url + 'change-login'
        result = requests.post(url, json={"login": self.my_login, "password": self.password, "new_password": "000"})
        assert result.status_code == 403
        assert result.json()["message"] == 'Token not exist'
        result = requests.post(url, json={"login": self.my_login, "password": self.password, "new_password": None},
                               headers={'Authorization': token})
        assert result.status_code == 400
        assert result.json()["message"] == [{'new_password': ['Field may not be null.']}]
        result = requests.post(url, json={"login": 'my_login', "password": self.password, "new_password": "qqq"},
                               headers={'Authorization': token})
        assert result.status_code == 400
        assert result.json()["message"] == 'Not valid login'
        result = requests.post(url, json={"login": self.my_login, "password": "xxx", "new_password": "000"},
                               headers={'Authorization': token})
        assert result.status_code == 400
        assert result.json()["message"] == 'Password is not valid'

    def test_6change_login(self):
        url = self.main_url + 'change-login'
        result = requests.post(url, json={"login": self.my_login, "password": self.password, "new_password": "000"},
                               headers={'Authorization': token})
        #assert result.status_code == 201
        assert result.json()["message"] == "Login and password changed successful"

        result = requests.post(url, json={"login": self.my_login, "password": "000", "new_password": self.password},
                               headers={'Authorization': token})
        assert result.status_code == 201
        assert result.json()["message"] == "Login and password changed successful"

    def test_7logout(self):
        url = self.main_url + 'logout'
        result = requests.post(url, headers={'Authorization': token}, json={})
        assert result.status_code == 200
        assert result.json()["message"] == "Logout successful"

    def test_8login_again(self):
        import time
        time.sleep(1)
        result = requests.post(self.main_url + 'login', json={"login": self.my_login, "password": self.password})
        result = requests.post(self.main_url + 'login2', json={"login": self.my_login, "code": "0000"})
        global token
        token = result.json()["access_token"]
        assert result.status_code == 200
        global refresh_token
        refresh_token = result.json()["refresh_token"]

    def test_9sessions(self):
        result = requests.get(self.main_url + 'sessions', headers={'Authorization': token}, json={})
        assert result.status_code == 200
        assert result.json()["message"] == "Session list received"
        assert result.json()["sessions"]

    def test_10refresh_token(self):
        import time
        time.sleep(1)
        result = requests.post(self.main_url + 'refresh', headers={'Authorization': token, 'Refresh': refresh_token}, json={})
        assert result.json()["message"] == "New token created"
        assert result.status_code == 201
        assert len(result.json()["access_token"]) == 149
        assert result.json()["access_token"] != token