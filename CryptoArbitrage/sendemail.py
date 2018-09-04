import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import SENDER_ADDRESS, SENDER_PASSWORD, SENDER_SMTP_HOST, SENDER_SMTP_PORT, RECIPIENT_ADDRESS

def send_email(subject, body):
	# connect to server and log in
	server = smtplib.SMTP(SENDER_SMTP_HOST, SENDER_SMTP_PORT)
	server.starttls()
	server.login(SENDER_ADDRESS, SENDER_PASSWORD)

	# set message information
	msg = MIMEMultipart()
	msg['From'] = SENDER_ADDRESS
	msg['To'] = RECIPIENT_ADDRESS
	msg['Subject'] = subject
	msg.attach(MIMEText(body, 'plain'))

	# send
	server.send_message(msg)

# test
#send_email("Test", "body")