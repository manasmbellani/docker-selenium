from tempfile import mkdtemp
import logging
import sys
import os
from faker import Faker
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException, NoSuchWindowException


language_list = ['en']

#This part make logging work locally when testing and in lambda cloud watch
if logging.getLogger().hasHandlers():
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)


#Function that setup the browser parameters and return browser object.
def open_browser():
    fake_user_agent = Faker()
    options = webdriver.ChromeOptions()
    options.binary_location = '/opt/chrome/chrome'
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-first-run')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-client-side-phishing-detection')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-web-security')
    options.add_argument('--lang=' + random.choice(language_list))
    options.add_argument('--user-agent=' + fake_user_agent.user_agent())
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")
    chrome = webdriver.Chrome("/opt/chromedriver", options=options)

    return chrome

#Our main Lambda function
def lambda_handler(event, context):
    try:

        # Open browser
        browser = open_browser()

        # Clean cookies
        browser.delete_all_cookies()
        browser.set_page_load_timeout(60)

        # Open web
        logging.info("Opening web: https://www.cnn.com")
        browser.get("https://www.cnn.com")

        #get text from google
        return_val = browser.title

        #browser.close() might not be required since the container is destroyed anyway after done.
        browser.close()
        return {
            "return": return_val
        }

    except AssertionError as msg:
        logging.error(msg)
        browser.close()
        sys.exit()
    except TimeoutException:
        logging.error('Request Time Out')
        browser.close()
        sys.exit()
    except WebDriverException:
        logging.error('------------------------ WebDriver-Error! ---------------------', exc_info=True)
        logging.error('------------------------ WebDriver-Error! END ----------------')
        browser.close()
        sys.exit()
    except NoSuchWindowException:
        logging.error('Window is gone, somehow...- NoSuchWindowException')
        sys.exit()
    except NoSuchElementException:
        logging.error('------------------------ No such element on site. ------------------------', exc_info=True)
        logging.error('------------------------ No such element on site. END ------------------------')
        browser.close()
        sys.exit()
