import os
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Environment variables ---
search_query = os.environ.get("SEARCH_QUERY", "Python")
recipient_email = os.environ.get("RECIPIENT_EMAIL")
sender_email = os.environ.get("SENDER_EMAIL")
sender_password = os.environ.get("SENDER_PASSWORD")  # Gmail App Password

if not all([recipient_email, sender_email, sender_password]):
    raise ValueError("Set SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL in environment variables")

# --- Headless Chrome setup ---
options = uc.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.7339.185 Safari/537.36"
)

# --- Use ChromeDriver compatible with GitHub Actions Chrome version (140) ---
driver = uc.Chrome(version_main=140, options=options)

try:
    # --- Navigate directly to Google News search results ---
    search_url = f"https://news.google.com/search?q={search_query}"
    driver.get(search_url)

    # Wait until at least one headline is present
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.DY5T1d"))
    )

    # --- Scrape headlines and links ---
    soup = BeautifulSoup(driver.page_source, "lxml")

finally:
    driver.quit()

articles = soup.select("a.DY5T1d")  # Headlines
news_list = []

for article in articles[:20]:  # Top 20 articles
    title = article.get_text(strip=True)
    link = article['href']
    if link.startswith("."):
        link = "https://news.google.com" + link[1:]
    news_list.append(f"- {title}\n  {link}")

if not news_list:
    news_list = ["No news found."]

# --- Prepare email content ---
email_content = "\n\n".join(news_list)
msg = MIMEText(email_content)
msg['Subject'] = f"Google News: '{search_query}'"
msg['From'] = sender_email
msg['To'] = recipient_email

# --- Send email ---
try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_email, msg.as_string())
    server.quit()
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
