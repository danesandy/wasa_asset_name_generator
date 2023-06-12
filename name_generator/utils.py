import re

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
