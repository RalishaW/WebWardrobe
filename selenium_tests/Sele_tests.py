import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os 

class TestFashanizeFlow(unittest.TestCase):

    def setUp(self):
        broweser = os.getenv('BROWSER', 'chrome').lower()

        if broweser == 'firefox':
            self.driver = webdriver.Firefox()
        elif broweser == 'safari':
            self.driver = webdriver.Safari()
        elif broweser == 'edge':
            self.driver = webdriver.Edge()
        else:
            self.driver = webdriver.Chrome()

        
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)

    def test_signup(self):
        driver =self.driver 
        self.driver.get("http://127.0.0.1:5000/signup")

        driver.find_element(By.ID, 'username').send_keys("dummyuser")
        driver.find_element(By.ID, 'firstname').send_keys('dummy')
        driver.find_element(By.ID, 'lastname').send_keys('user')
        driver.find_element(By.ID, 'email').send_keys('dummyuser@exmaple.com')
        driver.find_element(By.ID, 'password').send_keys('dummypassword123')
        driver.find_element(By.ID, 'confirm_password').send_keys('dummypassword123')
        driver.find_element(By.ID, 'submit').click()

        driver.find_element(By.CLASS_NAME, 'btn').click()
        time.sleep(2)
        
        self.assertIn("login", driver.current_url.lower())
        print("[PASS] Signup successful and redirected to login")

    def test_login(self):
        driver = self.driver
        self.driver.get("http://127.0.0.1:5000/login")

        driver.find_element(By.ID, 'email').send_keys('dummyuser@exmaple.com')
        driver.find_element(By.ID, 'password').send_keys('dummypassword123')
        driver.find_element(By.TAG_NAME, 'form').submit()

        time.sleep(2)
        self.assertIn("wardrobe", driver.current_url.lower() or driver.page.source.lower())
        print("[PASS] Login successful and redirected to wardrobe")


    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()