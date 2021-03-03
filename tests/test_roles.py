import requests

perm_url = 'http://localhost:5000/perm'


class TestRoles:
    main_url = 'http://localhost:5000/role'

    def test_create_role(self):
        res = requests.post(self.main_url, json={})
        assert res.status_code == 400
        res = requests.post(self.main_url, json={'name': 'user'})
        assert res.status_code == 201
        res = requests.post(self.main_url, json={'name': 'user'})
        assert res.status_code == 400

    def test_change_role(self):
        res = requests.put(self.main_url, json={'old_name': 'user', 'new_name': 'my_user'})
        assert res.status_code == 200

    def test_get_roles(self):
        res = requests.get(self.main_url)
        assert len(res.json()) == 1
        assert res.json()[0]['name'] == 'my_user'
        assert res.status_code == 200

    def test_add_permission(self):
        res = requests.post('http://localhost:5000/role/add_perm', json={'role': 'my_user', 'permission': 'readonly'})
        #assert res.status_code == 200
        assert res.json() == {"message":"Add permission to role"}
        res = requests.post('http://localhost:5000/role/del_perm', json={'role': 'my_user', 'permission': 'readonly'})
        assert res.status_code == 200

    def test_delete_role(self):
        res = requests.delete(self.main_url, json={'name': 'my_user'})
        assert res.status_code == 200



class Permissions:

    main_url = 'http://localhost:5000/perm'

    def test_create_perm(self):
        res = requests.post(self.main_url, json={'name': 'readonly'})
        assert res.status_code == 201

    def test_change_role(self):
        res = requests.put(self.main_url, json={'old_name': 'readonly', 'new_name': 'read_only'})
        assert res.status_code == 200

    def test_get_roles(self):
        res = requests.get(self.main_url)
        assert len(res.json()) == 1
        assert res.json()[0]['name'] == 'read_only'
        assert res.status_code == 200

    def test_delete_role(self):
        res = requests.delete(self.main_url, json={'name': 'read_only'})
        assert res.status_code == 200

