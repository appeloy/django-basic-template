from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from dotenv import load_dotenv
load_dotenv()


import threading

import random
import os
import hashlib


def __host_send_mail(subject, username, email_to, message, link, link_name):
    subject = subject
    html_message = render_to_string("users/email.html", {"username": username, "message": message, "link": link, "link_name": link_name})
    plain_message = strip_tags(html_message)
    at_from = os.getenv("EMAIL_HOST_USER")
    send_mail(subject, plain_message, at_from, [email_to], html_message=html_message)

def send_email_link(subject,username, email_to, message, link, link_name):
    task = threading.Thread(target=__host_send_mail, args=(subject,username, email_to, message, link, link_name))    
    task.start()

def token_generator(length):
    alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    token = []
    for _ in range(length):
        token.append(alpha[random.randint(0, len(alpha)-1)])
    return "".join(token)

def hashes_string(*args):
    string = ""
    for s in args:
        string += str(s)
    return hashlib.sha256(string.encode()).hexdigest()

