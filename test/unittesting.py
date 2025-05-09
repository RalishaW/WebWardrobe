from app.utils import try_to_login
from app.models import User
from app import db

import unittest

class UnitTests(unittest.TestCase):
    # SIGNUP TEST
    ##

    # LOGIN TEST
    def test_try_to_login_dummy(self):
        user = User.query.filter_by('test').first()
        user.set_password('1234')
        db.session.add(user)
        db.session.commit()

        self.assertTrue(try_to_login(1, '1234', False))

    def test_login_user(self):
        response = self.client.post('/login', data=dict(
            email='test@gmail.com',
            password='1234'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successfull!', response.data)
    
    def test_login_user_wrong_pwd(self):
        response = self.client.post('/login', data=dict(
            email='test@gmail.com',
            password='wrongpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login unsuccessful!. Please check email and password', response.data)

    def test_login_null_user(self):
        response = self.client.post('/login', data=dict(
            email='null_user@gmail.com',
            password='1234'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login unsuccessful!. Please check email and password', response.data)

    # CORE FUNCTIONS TEST
    ##
    def test_add_clothing_items(self):
        return
    
    def test_remove_clothing_item(self):
        return
    
    def test_generate_outfit(self):
        return
    
    def test_remove_outfit(self):
        return
    
    def test_share_outfit(self):
        return
    
    def test_remove_share_outfit(self):
        return


if __name__ == '__main__':
    unittest.main()