from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from dotenv import load_dotenv
load_dotenv()


import threading

import random
import os

def __host_send_mail(username, email_to, link):
    subject = "Email Verification"
    html_message = render_to_string("users/email_verification.html", {"username": username, "link": link})
    plain_message = strip_tags(html_message)
    at_from = os.getenv("EMAIL_HOST_USER")
    send_mail(subject, plain_message, at_from, [email_to], html_message=html_message)

def send_email_verification_link(username, email_to, link):
    task = threading.Thread(target=__host_send_mail, args=(username, email_to, link))    
    task.start()

def token_generator(length):
    alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    token = []
    for _ in range(length):
        token.append(alpha[random.randint(0, len(alpha)-1)])
    return "".join(token)



