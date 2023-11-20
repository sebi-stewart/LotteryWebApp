import re


# Valid Email address format as per Wikipedia's requirements https://en.wikipedia.org/wiki/Email_address
def check_email(email: str):
    email = email.lower().strip()

    # Makes sure there isn't any whitespace in the email
    if not not re.search("\s+", email):
        return None

    try:
        local_part, domain = email.split("@")

        if not local_part or not domain:
            return None

        # Checking local_part
        # Checking for ASCII characters
        for letter in local_part:
            if ((not re.search("\w", letter)) and
                    (not re.search("[!#$%&'*+-/=?^_`{|}~.]", letter))):
                return None

        # Checking there isn't double . or starts/ends with .
        if ((not not re.search("^[.]|[.]$", local_part)) or
                (not not re.search("[.]{2}", local_part))):
            return None

        # Checking domain
        # Checking latin letters
        if not re.search("[a-z]+", domain):
            return None

        # Checking there isn't double . or starts/ends with .
        if ((not not re.search("^[.]|[.]$", domain)) or
                (not not re.search("[.]{2}", domain))):
            return None

        # Checking there isn't double . or starts/ends with .
        if not not re.search("^-|-$", domain):
            return None

        # Remove hyphens and dots to stop false trigger on non word line
        domain = domain.replace(".", "")
        domain = domain.replace("-", "")

        # Checking for non word characters including underscore _
        if ((not not re.search("\W", domain)) or
                (not not re.search("_", domain))):
            return None

        return email

    except ValueError as er:
        print(er)
        return None


# Checks name doesn't have special characters
def check_name(name: str):
    if not not re.search("[*?!'^+%&/()=}\]\[{$#@<>]", name):
        return None
    return name.strip()


# Checks phone number is in correct format
def check_phone(phone: str):
    # Remove whitespace and dashes
    # phone = phone.replace(" ", "")
    # phone = phone.replace("-", "")

    if not re.search("^[0-9]{4}-[0-9]{3}-[0-9]{4}$", phone):
        return None
    return phone


# Checks password meets requirements
def check_password(password: str):
    # Checks for digit, lowercase, uppercase, special character
    if not re.search("[0-9]", password):
        return None
    if not re.search("[a-z]", password):
        return None
    if not re.search("[A-Z]", password):
        return None
    if not re.search("[^a-zA-Z\d\s]", password):
        return None

    # Return none if it contains whitespace
    if not not re.search("\s", password):
        return None

    # Make sure password is between 6-12 characters
    if len(password) < 6 or len(password) > 12:
        return None

    return password


# Check that confirm_password is the same as password
def verify_password(password, confirm):
    return password == confirm


# Checks that the DOB is in format DD/MM/YYYY
def check_date_of_birth(date_of_birth: str):
    print(date_of_birth)
    # Checks it only contains digits and slashes
    if not not re.search('[^0-9/]', date_of_birth):
        return None

    # Checks format
    if not re.search('^[0-9]{2}/[0-9]{2}/[0-9]{4}$', date_of_birth):
        return None

    return date_of_birth


# Checks that the postcode is in format (X=Uppercase letter, Y=Digit)
# 1: XY YXX
# 2: XYY YXX
# 3: XXY YXX
def check_postcode(postcode: str):
    # Check that there are no lowercase letters
    if not not re.search('[a-z]', postcode):
        return None

    # Check that there aren't special characters
    if not not re.search("[*?!'^+%&/()=}\]\[{$#@<>]", postcode):
        return None

    # Check for the format 1
    if not not re.search('(^[A-Z]{1}[0-9]{1} [0-9]{1}[A-Z]{2}$)', postcode):
        return postcode

    # Check for the format 2
    if not not re.search('(^[A-Z]{1}[0-9]{2} [0-9]{1}[A-Z]{2}$)', postcode):
        return postcode

    # Check for the format 3
    if not not re.search('(^[A-Z]{2}[0-9]{1} [0-9]{1}[A-Z]{2}$)', postcode):
        return postcode

    # Returns None if it doesn't match any of the above formats
    return None


# Test cases for email/name/etc
if __name__ == "__main__":
    print(check_email("123@gm.123x-xx"))
    print(check_name("Hey"))
    print(check_name("Seb "))
    print(check_phone("0772-199 1238"))
    print(check_password("123abcABC@@"))
