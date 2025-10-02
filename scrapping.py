import os
import requests
from xml.etree import ElementTree
import smtplib
from email.mime.text import MIMEText




search_query = os.environ.get("SEARCH_QUERY", "Python")
recipient_email = os.environ.get("RECIPIENT_EMAIL")
sender_email = os.environ.get("SENDER_EMAIL")
sender_password = os.environ.get("SENDER_PASSWORD")

if not all([recipient_email, sender_email, sender_password]):
    raise ValueError("Set SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL in environment variables")

# --- Fetch Google News RSS ---
rss_url = f"https://news.google.com/rss/search?q={search_query}&hl=en-US&gl=US&ceid=US:en"
response = requests.get(rss_url)
response.raise_for_status()

root = ElementTree.fromstring(response.content)
items = root.findall(".//item")

news_list = []
for item in items[:20]:  # Top 20 articles
    title = item.find("title").text
    link = item.find("link").text
    news_list.append(f"- {title}\n  {link}")

if not news_list:
    news_list = ["No news found."]

# --- Prepare email ---
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
