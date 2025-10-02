import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

# --- Environment variables ---
search_query = os.environ.get("SEARCH_QUERY", "Python")
recipient_email = os.environ.get("RECIPIENT_EMAIL")
sender_email = os.environ.get("SENDER_EMAIL")
sender_password = os.environ.get("SENDER_PASSWORD")  # Gmail App Password

if not all([recipient_email, sender_email, sender_password]):
    raise ValueError("Set SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL in environment variables")

# --- Fetch Google News search results ---
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/140.0.7339.185 Safari/537.36"
}

search_url = f"https://news.google.com/search?q={search_query}"
response = requests.get(search_url, headers=headers)
response.raise_for_status()  # Raise error if request failed

soup = BeautifulSoup(response.text, "lxml")

# --- Scrape headlines and links ---
articles = soup.select("a.DY5T1d")  # Headlines
news_list = []

for article in articles[:20]:  # Top 20 articles
    title = article.get_text(strip=True)
    link = article.get("href", "")
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
