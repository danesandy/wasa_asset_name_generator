import re
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def validate_password(password):
    if len(password) < 8:
        return "Password should be at least 8 characters long"
    elif not re.search("[a-z]", password):
        return "Password should have at least one lowercase character"
    elif not re.search("[A-Z]", password):
        return "Password should have at least one uppercase character"
    elif not re.search("[0-9]", password):
        return "Password should have at least one digit"
    elif not re.search("[!@#$%^&*()_+=-{};:'><]", password):
        return "Password should have at least one special character"
    else:
        return "Strong password"

def send_email(email, password):
    message = Mail(
        from_email='dane.sandy@wasa.gov.tt',
        to_emails=email,
        subject='Welcome to project S.W.A.N!',
        html_content="<h1>System for WASA's Asset Nomenclature</h1> <br> <strong>Here are your credentials:</strong> <br> Email: " + email + '<br> Password: ' + password + '<br> Please change your password after your first login.'
        # You can also add a banner image using HTML img tag in html_content
    )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

def get_duplicate_status(letter):
    # Map letters to duplicate statuses
    duplicate_statuses = {
        'A': 'first duplicate',
        'B': 'second duplicate',
        'C': 'third duplicate',
        'D': 'fourth duplicate',
        'E': 'fifth duplicate',
        'F': 'sixth duplicate',
        'G': 'seventh duplicate',
        'H': 'eighth duplicate',
        'I': 'ninth duplicate',
        'J': 'tenth duplicate',
        # Add more mappings here as needed
    }

    # Return the corresponding duplicate status, or an empty string if the letter is unrecognized
    return duplicate_statuses.get(letter, '')