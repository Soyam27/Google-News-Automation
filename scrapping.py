import os
import time
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# --- Environment variables ---
search_query = os.environ.get("SEARCH_QUERY", "Python")
recipient_email = os.environ.get("RECIPIENT_EMAIL")
sender_email = os.environ.get("SENDER_EMAIL")
sender_password = os.environ.get("SENDER_PASSWORD")  # Gmail App Password

if not all([recipient_email, sender_email, sender_password]):
    raise ValueError("Set SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL in environment variables")

# --- Set up headless Chrome ---
options = uc.ChromeOptions()
options.headless = True
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

driver = uc.Chrome(options=options)

# --- Open Google News and search ---
driver.get("https://news.google.com/")
time.sleep(2)

search_box = driver.find_element(By.XPATH, "//input[@aria-label='Search for topics, locations & sources']")
search_box.send_keys(search_query)
search_box.send_keys(Keys.RETURN)
time.sleep(3)

# --- Scrape page ---
soup = BeautifulSoup(driver.page_source, "lxml")
driver.quit()
data = soup.get_text()

# --- Send email ---
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
