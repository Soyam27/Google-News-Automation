import os
from dotenv import load_dotenv
import time
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

load_dotenv()

search_query = os.environ.get("SEARCH_QUERY", "Python")
recipient_email = os.environ.get("RECIPIENT_EMAIL")
sender_email = os.environ.get("SENDER_EMAIL")
sender_password = os.environ.get("SENDER_PASSWORD")

if not all([recipient_email, sender_email, sender_password]):
    raise ValueError("Set SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL in environment variables")

chrome_options = Options()
if os.name == "nt":  # Windows
    chrome_options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    chrome_driver_path = r"C:\tools\chromedriver-win64\chromedriver.exe"
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
else:  # Linux (Render)
    chrome_options.binary_location = "/usr/bin/chromium"
    chrome_driver_path = "/usr/bin/chromedriver"
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
driver.get("https://news.google.com/")
time.sleep(2)

search_box = driver.find_element(
    By.XPATH, "//input[@aria-label='Search for topics, locations & sources']"
)
search_box.send_keys(search_query)
search_box.send_keys(Keys.RETURN)
time.sleep(3)

soup = BeautifulSoup(driver.page_source, "lxml")
driver.quit()
data = soup.get_text()

msg = MIMEText(data)
msg['Subject'] = f"Google News Results for '{search_query}'"
msg['From'] = sender_email
msg['To'] = recipient_email

try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_email, msg.as_string())
    server.quit()
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
