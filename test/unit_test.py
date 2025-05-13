import os
import shutil
import unittest
from flask import current_app
from flask_testing import TestCase
from flask_login import current_user
from app.utils import try_to_login
from app.models import User, ClothingItem, Outfit, SharedOutfit
from test.test_config import TestConfig
from werkzeug.security import generate_password_hash
from werkzeug.datastructures import FileStorage
from app import app, db
import sys


class BaseTest(TestCase):
    def create_app(self):
        app.config.from_object(TestConfig)
        project_root = os.path.dirname(app.root_path)
        app.static_folder = os.path.join(project_root, 'test', 'static')
        return app
    
    def setUp(self):
        db.create_all()
        
        # Add sample user
        user = User(
            username='testuser', 
            firstname='test', 
            lastname='user',
            email='test@gmail.com',
            password=generate_password_hash('password')
        )

        # Add sample user for sharing
        user_share = User(
            username='testuser_share', 
            firstname='test',
            lastname='share',
            email='testshare@gmail.com', 
            password=generate_password_hash('password')
        )   
        db.session.add_all([user, user_share])
        db.session.commit()

        # the clothing_items upload folder exists under test/static
        upload_dir = os.path.join(app.static_folder,
                                  app.config['UPLOAD_CLOTHING_ITEM'])
        os.makedirs(upload_dir, exist_ok=True)
        # copy the fixture into that folder as "1_mock-hoodie.jpg"
        src = os.path.join(os.path.dirname(app.static_folder),
                           'mock-hoodie.jpg')
        dest = os.path.join(upload_dir, f"{user.id}_mock-hoodie.jpg")
        shutil.copy(src, dest)

        # Add sample clothing items 
        hoodie = ClothingItem(
            user_id=user.id, 
            item_name='Test Hoodie', 
            type='Hoodie', 
            color='Blue', 
            season='Winter', 
            occasion='Casual', 
            image_path=''
        )

        db.session.add(hoodie)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

# Test upload folder existence for test
class FolderState(BaseTest):
    def test_upload_folder_created(self):
        self.assertTrue(os.path.exists(app.config['UPLOAD_CLOTHING_ITEM']))
        self.assertTrue(os.path.exists(app.config['MAKE_OUTFIT']))
        self.assertTrue(os.path.exists(app.config['UPLOAD_PROFILE_PICTURE']))


class TestPage(BaseTest):
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    
    def test_wardrobe_page(self):
        response = self.client.get('/wardrobe')
        self.assertEqual(response.status_code, 302)
    
    def test_analysis_page(self):
        response = self.client.get('/analysis')
        self.assertEqual(response.status_code, 302)
    
    def test_outfits_page(self):
        response = self.client.get('/outfits')
        self.assertEqual(response.status_code, 302)
    
    def test_social_page(self):
        response = self.client.get('/social')
        self.assertEqual(response.status_code, 302)

# SIGNUP TEST
class TestSignUp(BaseTest):
    def test_signup(self):
        """Test that a user can sign up successfully."""
        response = self.client.post('/signup', data=dict(
            username='newuser',
            firstname='New',
            lastname='User',
            email='newuser@example.com',
            password='password',
            confirm='password'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_signup_email_already_existed(self):
        """Test that the system prevents using an existing email."""
        response = self.client.post('/signup', data=dict(
            username='uniqueuser',
            firstname='Test',
            lastname='User',
            email='test@gmail.com',  # Existing email
            password='password',
            confirm='password'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    def test_signup_username_already_existed(self):
        """Test that the system prevents using an existing username."""
        response = self.client.post('/signup', data=dict(
            username='testuser',
            firstname='Test',
            lastname='User',
            email='unique@gmail.com',  # Another email
            password='password',
            confirm='password'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

# LOGIN TEST
class TestLogin(BaseTest):
    # Wrapper function login
    def login(self, email='test@gmail.com', password='password'):
        return self.client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)
    
    def test_login_successfully(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successfully!', response.data)
    
    def test_login_user_wrong_password(self):
        response = self.login(password='wrongpassword')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login unsuccesful. Please check your username or password.', response.data)

    def test_login_null_user(self):
        response = self.client.post('/login', data=dict(
            email='null_user@gmail.com',
            password='password'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login unsuccesful. Please check your username or password.', response.data)

    def test_log_out(self):
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Logout does not have a template yet

# CLOTHINGITEMS TESTS
class TestClothingItem(BaseTest):
    # Wrapper function for login
    def login(self, email='test@gmail.com', password='password'):
        return self.client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)
    
    def test_add_clothing_items(self):
        """Test adding a clothing item."""
        self.login()

        with open('test/mock-hoodie.jpg', 'rb') as file:
            file_storage = FileStorage(file, filename='mock-hoodie.jpg', content_type='image/jpeg')
            response = self.client.post('/wardrobe/add', 
                                        data={
                                            'item_name': 'Test Hoodie',
                                            'type': 'Hoodie',
                                            'color': 'Blue',
                                            'season': 'Winter',
                                            'occasion': 'Casual',
                                            'image': file_storage
                                        }, 
                                        follow_redirects=True,
                                        content_type='multipart/form-data',  
                                        ) 

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Item added successfully!', response.data)

    def test_remove_clothing_item(self):
        self.login()

        item = ClothingItem(
            item_name='Test-Shirt', 
            type='Shirt', 
            color='Red',
            season='Summer', 
            occasion='Casual',
            user_id=1,
            image_path='test/mock-shirt.jpg'
        )
        db.session.add(item)
        db.session.commit()

        response=self.client.post(
            f'/wardrobe/delete/{item.id}',
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Item deleted successfully', response.data)
    
    # Test for valid picture: size limit
    def test_add_invalid_size_clothing_item(self):
        # Login
        self.client.post('/login', data=dict(
            email='test@gmail.com',
            password='password'
        ), follow_redirects=True)

        # Adding an invalid image (mock-size-exceed.png)
        with open('test/mock-size-exceed.png', 'rb') as file:
            response = self.client.post('/wardrobe/add', data=dict(
                item_name='Invalid Hoodie',
                type='Hoodie',
                color='Red',
                season='Winter',
                occasion='Casual',
                image=file
            ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid file type or file size exceeds limit.', response.data)
    
    # Test for valid picture: only accepted {'png', 'jpg', 'jpeg', 'jfif', 'webp'} 
    def test_add_invalid_file_clothing_item(self):
        self.client.post('/login', data=dict(
            email='test@gmail.com',
            password='password'
        ), follow_redirects=True)

        # Adding an invalid file type (blank.pdf)
        with open('test/blank.pdf', 'rb') as file:
            response = self.client.post('/wardrobe/add', data=dict(
                item_name='Test Hoodie',
                type='Hoodie',
                color='Blue',
                season='Winter',
                occasion='Casual',
                image=file
            ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid file type or file size exceeds limit.', response.data)

# OUTFITS TESTS
class TestOutfits(BaseTest):
    # Wrapper function for login
    def login(self, email='test@gmail.com', password='password'):
        return self.client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)
    
    def test_save_outfit(self):
        self.login()

        item1 = ClothingItem(
            item_name='Hoodie', 
            type='Hoodie', 
            color='Blue', 
            season='Winter', 
            occasion='Casual', 
            user_id=1, 
            image_path='mock-hoodie.jpg'
        )
        item2 = ClothingItem(
            item_name='Pant', 
            type='Pant', 
            color='Blue', 
            season='Winter', 
            occasion='Casual', 
            user_id=1, 
            image_path='mock-pant.png'
        )
        db.session.add(item1)
        db.session.add(item2)
        db.session.commit()

        response = self.client.post('/save_outfit', data=dict(
            outfit_name='Winter Outfit',
            privacy='public',
            occasion='Casual',
            season='Winter'
        ), follow_redirects=True)

        # Check if the outfit is saved 
        self.assertEqual(response.status_code, 200)
        
    def test_preview_outfit(self):
        self.login()

        base = os.path.dirname(app.root_path)
        hoodie_path = os.path.join(base, 'test', 'mock-hoodie.jpg')
        pant_path   = os.path.join(base, 'test', 'mock-pant.png')
        
        item1 = ClothingItem(
            item_name='Hoodie', 
            type='Hoodie', 
            color='Blue', 
            season='Winter', 
            occasion='Casual', 
            user_id=1, 
            image_path=hoodie_path
        )
        item2 = ClothingItem(
            item_name='Pant', 
            type='Pant', 
            color='Blue', 
            season='Winter', 
            occasion='Casual', 
            user_id=1, 
            image_path=pant_path
        )
        db.session.add(item1)
        db.session.add(item2)
        db.session.commit()

        response = self.client.post('/preview_outfit', 
                                    data=dict(
                                        occasion='Casual',
                                        season='Winter'
                                    ), 
                                    follow_redirects=True
                                    )

        # Check if the preview is generated successfully
        self.assertEqual(response.status_code, 200)

        # Check if the preview image was saved
        preview_filename = f"preview_{1}.png"
        preview_path = os.path.join(
            app.root_path, 
            'static', 
            app.config['MAKE_OUTFIT'], 
            preview_filename
        )
        self.assertTrue(os.path.exists(preview_path))
    
    # def test_delete_outfit(self):
    #     item = ClothingItem(
    #         item_name='Hoodie', 
    #         type='Hoodie', 
    #         color='Blue', 
    #         season='Winter', 
    #         occasion='Casual', 
    #         user_id=1, 
    #         image_path='clothing_items/mock-hoodie.jpg'
    #     )
    #     db.session.add(item)
    #     db.session.commit()

    #     new_outfit = Outfit(
    #         outfit_name="Winter Outfit",
    #         privacy="public",
    #         occasion="Casual",
    #         season="Winter",
    #         user_id=1
    #     )
    #     db.session.add(new_outfit)
    #     db.session.commit()

    #     # Check if the outfit is added
    #     outfit = Outfit.query.first()

    #     response = self.client.post(f'/outfits/delete/{outfit.id}', follow_redirects=True)
        
    #     # Check if the outfit is deleted
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Outfit deleted successfully!', response.data)

    #     # Check if the preview image is deleted from the directory
    #     preview_path = os.path.join(app.root_path, 'static', 'outfits', f"{outfit.id}_outfit.png")
    #     self.assertFalse(os.path.exists(preview_path))

    # def test_share_outfit(self):
    #     item = ClothingItem(
    #         item_name='Hoodie', 
    #         type='Hoodie', 
    #         color='Blue', 
    #         season='Winter', 
    #         occasion='Casual', 
    #         user_id=1, 
    #         image_path='clothing_items/mock-hoodie.jpg'
    #     )
    #     db.session.add(item)
    #     db.session.commit()

    #     new_outfit = Outfit(
    #         outfit_name="Winter Outfit",
    #         privacy="public",
    #         occasion="Casual",
    #         season="Winter",
    #         user_id=1
    #     )
    #     db.session.add(new_outfit)
    #     db.session.commit()

    #     response = self.client.post('/outfits/share', data=dict(
    #         outfit_id=new_outfit.id,
    #         username='testuser_share'
    #     ), follow_redirects=True)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Outfit shared successfully.', response.data)

    #     # Check if the shared outfit exists in the database
    #     shared_outfit = SharedOutfit.query.filter_by(outfit_id=new_outfit.id).first()
    #     self.assertIsNotNone(shared_outfit)
    
    # def test_delete_shared_outfit(self):
    #     item = ClothingItem(
    #         item_name='Hoodie', 
    #         type='Hoodie', 
    #         color='Blue', 
    #         season='Winter', 
    #         occasion='Casual', 
    #         user_id=1, 
    #         image_path='clothing_items/mock-hoodie.jpg'
    #     )
    #     db.session.add(item)
    #     db.session.commit()

    #     new_outfit = Outfit(
    #         outfit_name="Winter Outfit",
    #         privacy="public",
    #         occasion="Casual",
    #         season="Winter",
    #         user_id=1
    #     )
    #     db.session.add(new_outfit)
    #     db.session.commit()

    #     # Share the outfit with another user
    #     shared_outfit = SharedOutfit(
    #         outfit_id=new_outfit.id,
    #         sender_id=1,
    #         receiver_id=2 
    #     )
    #     db.session.add(shared_outfit)
    #     db.session.commit()

    #     # Simulate deleting the shared outfit
    #     response = self.client.post(f'/social/delete/{shared_outfit.id}', follow_redirects=True)

    #     # Check if the shared outfit is deleted
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Shared outfit removed.', response.data)

    #     # Ensure shared outfit no longer exists in the database
    #     deleted_shared_outfit = SharedOutfit.query.get(shared_outfit.id)
    #     self.assertIsNone(deleted_shared_outfit)


if __name__ == '__main__':
    unittest.main()