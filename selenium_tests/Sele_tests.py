import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import os 
from app import create_app, db
from app.config import TestingConfig
import threading

def run_flask_app(app):
    app.run(port=5000, use_reloader=False)

class TestFashanizeFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app(config_object=TestingConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all() 

        # Start Flask app in a background thread
        cls.server_thread = threading.Thread(target=run_flask_app, args=(cls.app,))
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(3)  # wait for server to start

        browser = os.getenv('BROWSER', 'chrome').lower()

        if browser == 'firefox':
            cls.driver = webdriver.Firefox()
        elif browser == 'safari':
            cls.driver = webdriver.Safari()
        elif browser == 'edge':
            cls.driver = webdriver.Edge()
        else:
            cls.driver = webdriver.Chrome()

        cls.driver.maximize_window()
        cls.driver.implicitly_wait(5)


        
    def setUp(self):
        self.driver = self.__class__.driver

    def do_login(self):
        self.driver.get("http://127.0.0.1:5000/login")
        self.driver.find_element(By.NAME, 'email').send_keys('dummyuser@example.com')
        self.driver.find_element(By.NAME, 'password').send_keys('dummypassword123')
        self.driver.find_element(By.TAG_NAME, 'form').submit()
        time.sleep(2)

    def test_1_signup(self):
        self.driver.get("http://127.0.0.1:5000/signup")
        self.driver.find_element(By.ID, 'username').send_keys("dummyuser")
        self.driver.find_element(By.ID, 'firstname').send_keys('dummy')
        self.driver.find_element(By.ID, 'lastname').send_keys('user')
        self.driver.find_element(By.ID, 'email').send_keys('dummyuser@example.com')
        self.driver.find_element(By.ID, 'password').send_keys('dummypassword123')
        self.driver.find_element(By.ID, 'confirm_password').send_keys('dummypassword123')
        self.driver.find_element(By.ID, 'terms').click()
        self.driver.find_element(By.CLASS_NAME, 'btn').click()
        time.sleep(2)

        self.assertTrue(
        "login" in self.driver.current_url.lower() or "signup" in self.driver.current_url.lower())
        print("[PASS] Signup successful")

    def test_2_login(self):
        self.do_login()
        self.assertIn("wardrobe", self.driver.current_url.lower() or self.driver.page_source.lower())
        print("[PASS] Login successful")

    def test_3_upload_item(self):
        self.do_login()
        base_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../app/static/selenium_uploads"))

        clothing_items = [
            {
                "name": "Running Club Hoodie",
                "type": "Hoodie",
                "color": "Blue",
                "season": "Winter",
                "occasion": "Casual",
                "image":  os.path.join(base_path, "hoodie.png")
            },
            {
                "name": "Butter Tshirt",
                "type": "T-Shirt",
                "color": "Brown",
                "season": "All Season",
                "occasion": "Casual",
                "image": os.path.join(base_path, "Tshirt1.webp")
            },
            {
                "name": "H&M Pants",
                "type": "Pants",
                "color": "Gray",
                "season": "All Season",
                "occasion": "Causal",
                "image": os.path.join(base_path, "pants.png")
            },
            {
                "name": "Nike Shoes",
                "type": "Shoes",
                "color": "White",
                "season": "All Season",
                "occasion": "Causal",
                "image": os.path.join(base_path, "nike.jpg")
            }
        ]

        for item in clothing_items:
    # Click "+ Add Item" to open the form
            self.driver.find_element(By.XPATH, '//button[contains(text(), "+ Add Item")]').click()
            time.sleep(1)

            self.driver.find_element(By.NAME, "image").send_keys(item["image"])
            self.driver.find_element(By.NAME, "item_name").send_keys(item["name"])
            self.driver.find_element(By.NAME, "type").send_keys(item["type"])
            self.driver.find_element(By.NAME, "color").send_keys(item["color"])
            self.driver.find_element(By.NAME, "season").send_keys(item["season"])
            self.driver.find_element(By.NAME, "occasion").send_keys(item["occasion"])

            self.driver.find_element(By.ID, "submit-btn").click()
            time.sleep(2)

            self.assertIn("Item added successfully", self.driver.page_source)
            print("[PASS] Clothing item uploaded successfully")
    
    def test_4_generate_outfit(self):
        self.do_login()
        self.driver.get("http://127.0.0.1:5000/outfits")
        time.sleep(1)

        # Show the create outfit form
        self.driver.find_element(By.XPATH, '//button[contains(text(), "+ Create Outfit")]').click()
        time.sleep(1)

        # Fill and submit the form
        self.driver.find_element(By.NAME, 'occasion').send_keys('Casual')
        self.driver.find_element(By.NAME, 'season').send_keys('Winter')
        self.driver.find_element(By.XPATH, '//form[@action="/preview_outfit"]//button[@type="submit"]').click()
        time.sleep(2)

        self.assertIn("Outfit Preview", self.driver.page_source)
        print("[PASS] Outfit preview generated successfully")


    def test_4_save_outfit(self):
        self.driver.get("http://127.0.0.1:5000/outfits")

        # Save Winter Outfit
        self.driver.find_element(By.XPATH, '//button[contains(text(), "+ Create Outfit")]').click()
        time.sleep(1)
        Select(self.driver.find_element(By.NAME, 'occasion')).select_by_visible_text('Casual')
        Select(self.driver.find_element(By.NAME, 'season')).select_by_visible_text('Winter')
        self.driver.find_element(By.XPATH, '//form[@action="/preview_outfit"]//button[@type="submit"]').click()

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "preview-container"))
        )
        self.driver.find_element(By.NAME, 'outfit_name').send_keys("Test Winter Fit")
        self.driver.find_element(By.XPATH, '//form[@action="/save_outfit"]//button[@type="submit"]').click()
        time.sleep(2)
        self.assertIn("Outfit saved", self.driver.page_source)
        print("[PASS] Winter outfit saved successfully")

        # Save Summer Outfit
        self.driver.find_element(By.XPATH, '//button[contains(text(), "+ Create Outfit")]').click()
        time.sleep(1)
        Select(self.driver.find_element(By.NAME, 'occasion')).select_by_visible_text('Casual')
        Select(self.driver.find_element(By.NAME, 'season')).select_by_visible_text('Summer')
        self.driver.find_element(By.XPATH, '//form[@action="/preview_outfit"]//button[@type="submit"]').click()

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "preview-container"))
        )
        self.driver.find_element(By.NAME, 'outfit_name').send_keys("Test Summer Fit")
        self.driver.find_element(By.XPATH, '//form[@action="/save_outfit"]//button[@type="submit"]').click()
        time.sleep(2)
        self.assertIn("Outfit saved", self.driver.page_source)
        print("[PASS] Summer outfit saved successfully")

    def test_6_delete_winter_outfit(self):
        self.do_login()
        self.driver.get("http://127.0.0.1:5000/outfits")
        time.sleep(2)
        outfits = self.driver.find_elements(By.CLASS_NAME, "outfit-item")
        for outfit in outfits:
            season = outfit.get_attribute("data-season")
            name_element = outfit.find_element(By.TAG_NAME, "h4")
            if season.lower() == "winter" and "Winter Fit" in name_element.text:
                delete_btn = outfit.find_element(By.CLASS_NAME, "delete-btn")
                delete_btn.click()
                self.driver.switch_to.alert.accept()  # Handle confirmation dialog if JS alert is used
                time.sleep(2)
                break
            
        # Confirm it's no longer on the page
        self.assertNotIn("Winter Fit", self.driver.page_source)
        print("[PASS] Winter outfit deleted successfully")

    def test_delete_clothing_item(self):
        self.do_login()
        self.driver.get("http://127.0.0.1:5000/wardrobe")
        time.sleep(2)

        items = self.driver.find_elements(By.CLASS_NAME, "wardrobe-item")

        for item in items:
            name = item.find_element(By.TAG_NAME, "p").text
            if name == "Running Club Hoodie":  # Replace with the exact item name you want to delete
                delete_btn = item.find_element(By.TAG_NAME, "button")
                delete_btn.click()
                self.driver.switch_to.alert.accept()  # Confirm deletion if JS confirm() is used
                time.sleep(2)
                break

        # Assert the item is no longer present
        self.assertNotIn("Running Club Hoodie", self.driver.page_source)
        print("[PASS] Clothing item deleted successfully")





    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
        cls.driver.quit()


if __name__ == "__main__":
    unittest.main()