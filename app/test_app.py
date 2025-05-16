import io
import os
import unittest
from app import create_app, db
from app.config import TestingConfig
from app.models import ClothingItem, Outfit, SharedOutfit, User
from werkzeug.security import generate_password_hash
from app.utils import generate_reset_token, verify_reset_token


class UnitTest(unittest.TestCase):
    def setUp(self):
        # Create app and test client
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()

        # Push context for db and routing
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create all tables in-memory
        db.create_all()

        default = User(
            username='testuser',
            firstname='Test',
            lastname='User',
            email='test@gmail.com',
            password=generate_password_hash('password')
        )
        db.session.add(default)
        db.session.commit()

    def tearDown(self):
        # Remove session and drop all tables
        db.session.remove()
        db.drop_all()

        # Pop app context
        self.app_context.pop()
    
    def test_home_page(self):
        response = self.client.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome to Fashanise", response.data)
    
    def test_signup_successful(self):
        response = self.client.post(
            "/signup",
            data={
                "username":  "newuser",
                "firstname": "New",
                "lastname":  "User",
                "email":     "new@example.com",
                "password":  "password",
                "confirm_password":   "password",
                "terms": "y"
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful! Please login.', response.data)
    
    def test_signup_email_existed(self):
        # Test signup on the email again
        response = self.client.post('/signup', data={
            'username':'uniqueuser',
            'firstname':'Test',
            'lastname':'User',
            'email':'test@gmail.com',  # Existing email
            'password':'password',
            'confirm_password':'password',
            'terms':'y'
        }, 
        follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email already exists. Please use another email.',
                       response.data)
    
    def test_signup_username_existed(self):
        # Test signup on the username again
        response = self.client.post('/signup', data={
            'username':'testuser',
            'firstname':'Test',
            'lastname':'User',
            'email':'unique@gmail.com',  # Another email
            'password':'password',
            'confirm_password':'password',
            'terms':'y'
        }, 
        follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Username already taken. Please choose another one.', 
            response.data)

    def test_login_successful(self):
        response = self.client.post(
            "/login",
            data={
                "email": "test@gmail.com", 
                "password": "password"
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"MyWardrobe", response.data)
    
    def test_login_wrong_password(self):
        response = self.client.post(
            "/login",
            data={
                "email": "test@gmail.com", 
                "password": "wrong"
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"Login unsuccessful. Please check your username or password.", 
            response.data)
    
    def test_login_null_user(self):
        response = self.client.post(
            "/login",
            data={
                "email": "noone@example.com", 
                "password": "anything"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"Login unsuccessful. Please check your username or password.", 
            response.data)

    
    def test_log_out(self):
        # first log in
        self.client.post(
            "/login",
            data={"email": "test@gmail.com", "password": "password"},
            follow_redirects=True
        )
        # then log out
        response = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"Your Online Closet", 
            response.data)  
    

    ### CLOTHING ITEM TEST CASES
    def test_add_clothing_item(self):
        self.client.post("/login", data={"email":"test@gmail.com","password":"password"}, follow_redirects=True)
        fixture_path = os.path.join(
            self.app.root_path, 'static', 'test_uploads', 'mock-hoodie.jpg'
        )
        # read file into BytesIO so it's not closed prematurely
        with open(fixture_path, 'rb') as f:
            img_bytes = f.read()
        data = {
            'item_name': 'Test Shirt',
            'type': 'Shirt',
            'color': 'Red',
            'season': 'Summer',
            'occasion': 'Casual',
            'image': (io.BytesIO(img_bytes), 'mock-hoodie.jpg')
        }
        response = self.client.post(
            '/wardrobe/add', data=data,
            content_type='multipart/form-data', follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Item added successfully!', 
            response.data)
        
    def test_remove_clothing_item(self):
        self.client.post("/login", 
                data={
                    "email":"test@gmail.com",
                    "password":"password"}, 
                follow_redirects=True)
        item = ClothingItem(user_id=1,item_name='Del',type='Pants',color='Blue',season='Winter',occasion='Casual',image_path='del.jpg')
        db.session.add(item)
        db.session.commit()
        response = self.client.post(f'/wardrobe/delete/{item.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Item deleted successfully', 
            response.data)
    
    def test_add_invalid_size_clothing_item(self):
        self.client.post("/login", data={"email":"test@gmail.com","password":"password"}, follow_redirects=True)
        fixture_path = os.path.join(
            self.app.root_path, 'static', 'test_uploads', 'mock-size-exceed.png'
        )
        with open(fixture_path, 'rb') as f:
            img_bytes = f.read()
        data = {
            'item_name': 'BadSize',
            'type': 'Hat',
            'color': 'Black',
            'season': 'Fall',
            'occasion': 'Formal',
            'image': (io.BytesIO(img_bytes), 'mock-size-exceed.png')
        }
        response = self.client.post(
            '/wardrobe/add', data=data,
            content_type='multipart/form-data', follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid file type or file size exceeds limit.', response.data)
    
    def test_add_invalid_file_clothing_item(self):
        self.client.post("/login", data={"email":"test@gmail.com","password":"password"}, follow_redirects=True)
        data = {
            'item_name': 'BadType',
            'type': 'Hat',
            'color': 'Black',
            'season': 'Fall',
            'occasion': 'Formal',
            'image': (io.BytesIO(b"data"), 'file.pdf')
        }
        response = self.client.post('/wardrobe/add', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Invalid file type or file size exceeds limit.', 
            response.data)
    

    ### OUTFITS TEST CASES 
    def test_save_outfit(self):
        self.client.post(
            "/login", data={"email":"test@gmail.com","password":"password"}, follow_redirects=True
        )
        items = [ClothingItem(user_id=1,item_name=f'I{i}',type='T',color='C',season='S',occasion='O',image_path=f'i{i}.jpg') for i in (1,2)]
        db.session.add_all(items)
        db.session.commit()
        response = self.client.post(
            '/save_outfit', data={'outfit_name':'O1','occasion':'O','season':'S'}, follow_redirects=True
        )
        # ensure route completes successfully
        self.assertEqual(response.status_code, 200)
    
    def test_delete_outfit(self):
        self.client.post("/login", data={"email":"test@gmail.com","password":"password"}, follow_redirects=True)
        of = Outfit(outfit_name='D1',occasion='O',season='S',user_id=1)

        db.session.add(of); db.session.commit()

        response = self.client.post(f'/outfits/delete/{of.id}', follow_redirects=True)

        self.assertIsNone(db.session.get(Outfit, of.id))
    
    ### SOCIAL TEST CASES
    def test_share_outfit(self):
        self.client.post('/login', data={'email':'test@gmail.com','password':'password'}, follow_redirects=True)
        u2 = User(username='u2',firstname='U',lastname='Two',
                  email='u2@example.com',password=generate_password_hash('pw'))
        of = Outfit(outfit_name='S1',occasion='O',season='S',user_id=1)

        db.session.add_all([u2,of])
        db.session.commit()

        response = self.client.post('/outfits/share', data={'outfit_id':of.id,'username':'u2'}, follow_redirects=True)

        self.assertIsNotNone(SharedOutfit.query.filter_by(outfit_id=of.id).first())
    
    def test_deleted_shared_outfit(self):
        self.client.post('/login', data={'email':'test@gmail.com','password':'password'}, follow_redirects=True)
        u2 = User(username='u2',firstname='U',lastname='Two',
                  email='u2@example.com',password=generate_password_hash('pw'))
        of = Outfit(outfit_name='S2',occasion='O',season='S',user_id=1)

        db.session.add_all([u2,of])
        db.session.commit()

        so = SharedOutfit(outfit_id=of.id,sender_id=1,receiver_id=u2.id)
        db.session.add(so)
        db.session.commit()

        response = self.client.post(
            f'/social/delete/{so.id}', 
            follow_redirects=True)
        
        self.assertIsNone(db.session.get(SharedOutfit, so.id))
    
    ### CHANGE PASSWORD TEST CASE
    def test_change_password(self):
        # Generate token
        token = generate_reset_token(1)
        
        response = self.client.get(f'/reset_password/token={token}', follow_redirects=True)
        self.assertIn(b'Reset Password', response.data)
        response = self.client.post(
            f'/reset_password/token={token}',
            data={
                'password':'newpass',
                'confirm_password':'newpass'},
            follow_redirects=True)
        
        self.assertIn(b'Log-In', response.data)
        response = self.client.post(
            '/login', data={
            'email':'test@gmail.com',
            'password':'newpass'}, 
            follow_redirects=True)
        self.assertIn(
            b'MyWardrobe', 
            response.data)

    def test_change_password_invalid_token(self):
        # Invalid token
        token = '138951385asfugasfihaqw'
        response = self.client.get(f'/reset_password/token={token}', follow_redirects=True)
        self.assertIn(b'Invalid or expired token. Please try again.', response.data)


if __name__ == '__main__':
    unittest.main()
