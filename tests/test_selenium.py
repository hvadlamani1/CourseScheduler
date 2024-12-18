import pytest

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from time import sleep

@pytest.fixture
def browser():
    CHROME_PATH = "C:\\Webdriver\\chromedriver-win64"
    print(CHROME_PATH)

    service = Service(executable_path = CHROME_PATH + '\\chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(8)
    
    yield driver

    # For cleanup, quit the driver
    driver.quit()

def test_register_instructor(browser):
    browser.get('https://localhost:5000/register_instructor')

    browser.find_element(By.NAME, "Email").send_keys("mzlin@wpi.edu")

    assert 200 == 200