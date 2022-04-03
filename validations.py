from wtforms.validators import ValidationError
import re
import string


def advisorEmail_validations(email):
    emailParts = email.split('@')

    if len(emailParts) != 2:
        raise ValidationError('Not a Valid Email')

    if emailParts[1] != 'upm.edu.sa':
        raise ValidationError('Not a Valid UPM Email')

    regex = re.match('^[a-zA-Z]\.[A-Za-z\-]{4,20}$', emailParts[0])
    if not regex:
        raise ValidationError('The address is not valid for UPM staff email')


def password_validation(password):
    valid = False
    for letter in password:
        if letter in string.ascii_uppercase:  # contains at least one uppercase
            valid = True
            break
    if not valid:
        raise ValidationError('Password must contain uppercase letters')

    valid = False
    for letter in password:
        if letter in string.ascii_lowercase:  # contains at least one lower case
            valid = True
            break

    if not valid:
        raise ValidationError('Password must contain lowercase letters')

    valid = False
    for letter in password:
        if letter in string.digits:  # contains at least one digit
            valid = True
            break
    if not valid:
        raise ValidationError('Password must contain digits')

    symbols = '!#$%&*+-.=?@^_|~'
    valid = False
    for letter in password:
        if letter in symbols:  # contains at least one symbols
            valid = True
            break
    if not valid:
        raise ValidationError('Password must contain one of these symbols: ' + symbols)

    forbiddenSymbols = '"\'(),/;<>[\\]`{}~'  # doesn't contains any illegal symbol
    for letter in password:
        if letter in forbiddenSymbols:
            raise ValidationError('Password must not contain one of these symbols: ' + forbiddenSymbols)


def studentID_validation(studentID):
    regex = re.match('^((3[5-9])|(4[0-2]))[12]0[0-3][0-9]{2}$', studentID)
    if not regex:
        raise ValidationError('Invalid Student ID')


def name_validation(name):
    regex = re.match('^[A-Za-z]{4,20}$', name)

    if not regex:
        raise ValidationError('Names should only contain letters, with the length being from 4 to 20')


def level_validation(level):
    if not str(level).isnumeric():
        raise ValidationError("level must be an integer between 1 and 8.")

    if not (0 < int(str(level)) < 9):
        raise ValidationError("level must be between 1 and 8.")


def credits_validations(credits):
    if not str(credits).isnumeric():
        raise ValidationError("credits must be an integer between 0 and 100.")

    if not (0 < int(str(credits)) < 100):
        raise ValidationError("credits must be between 0 and 100.")
