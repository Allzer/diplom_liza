import re
from datetime import date

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, Field, field_validator

PHONE_STORED_LEN = 12
PHONE_STORED_PATTERN = re.compile(r'^\+7\d{10}$')
EMAIL_MAX_LEN = 40
PASSWORD_MIN_LEN = 8
PASSWORD_MAX_LEN = 128

# Имя/фамилия: буквы (кириллица или латиница), дефис, пробел; без цифр
PERSON_NAME_PATTERN = re.compile(
    r'^[А-Яа-яЁёA-Za-z](?:[А-Яа-яЁёA-Za-z\-]*[А-Яа-яЁёA-Za-z])?$'
)


def normalize_phone_number(value: str) -> str:
    digits = re.sub(r'\D', '', value.strip())
    if digits.startswith('8') and len(digits) == 11:
        digits = '7' + digits[1:]
    if digits.startswith('7') and len(digits) == 11:
        normalized = f'+{digits}'
    elif value.strip().startswith('+7') and len(digits) == 11:
        normalized = f'+{digits}'
    else:
        normalized = ''

    if len(normalized) != PHONE_STORED_LEN or not PHONE_STORED_PATTERN.match(normalized):
        raise ValueError(
            'Укажите корректный номер: 10 цифр после +7 '
            '(например, +7 (999) 123-45-67 или +79991234567)'
        )
    return normalized


def validate_person_name(value: str, field_title: str) -> str:
    value = re.sub(r'\s+', ' ', value.strip())
    if len(value) < 2:
        raise ValueError(f'{field_title}: минимум 2 символа')
    if re.search(r'\d', value):
        raise ValueError(f'{field_title}: не должно содержать цифры')
    if not PERSON_NAME_PATTERN.match(value):
        raise ValueError(
            f'{field_title}: только буквы (русские или латинские), допускается дефис'
        )
    return value


def validate_email_strict(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError('Укажите email')

    if value.startswith('@') or value.count('@') != 1:
        raise ValueError('Укажите email в формате name@example.com')

    local, domain = value.split('@', 1)
    if not local:
        raise ValueError('Укажите имя почты до символа @ (например, ivan@mail.ru)')
    if '..' in local or '..' in domain:
        raise ValueError('Email не может содержать две точки подряд')
    if local.startswith('.') or local.endswith('.'):
        raise ValueError('Некорректная часть email до @')

    if len(value) > EMAIL_MAX_LEN:
        raise ValueError(f'Email не длиннее {EMAIL_MAX_LEN} символов')

    try:
        result = validate_email(value, check_deliverability=False)
    except EmailNotValidError:
        raise ValueError(
            'Некорректный email. Пример: ivan@mail.ru'
        ) from None

    normalized = result.normalized
    if len(normalized) > EMAIL_MAX_LEN:
        raise ValueError(f'Email не длиннее {EMAIL_MAX_LEN} символов')
    return normalized


class RegistrationFormSchema(BaseModel):
    section_id: int = Field(gt=0, description='ID секции')
    last_name: str = Field(min_length=2, max_length=100)
    first_name: str = Field(min_length=2, max_length=100)
    patronymic: str | None = Field(default=None, max_length=100)
    phone_number: str = Field(min_length=1, max_length=18)
    email: str | None = None
    birth_date: date
    comment: str | None = Field(default=None, max_length=500)

    @field_validator('last_name')
    @classmethod
    def check_last_name(cls, value: str) -> str:
        return validate_person_name(value, 'Фамилия')

    @field_validator('first_name')
    @classmethod
    def check_first_name(cls, value: str) -> str:
        return validate_person_name(value, 'Имя')

    @field_validator('patronymic', mode='before')
    @classmethod
    def empty_patronymic(cls, value: str | None) -> str | None:
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return value.strip() if isinstance(value, str) else value

    @field_validator('patronymic')
    @classmethod
    def check_patronymic(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_person_name(value, 'Отчество')

    @field_validator('phone_number')
    @classmethod
    def check_phone(cls, value: str) -> str:
        return normalize_phone_number(value)

    @field_validator('comment', mode='before')
    @classmethod
    def empty_comment(cls, value: str | None) -> str | None:
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return value.strip() if isinstance(value, str) else value

    @field_validator('email', mode='before')
    @classmethod
    def empty_email_to_none(cls, value: str | None) -> str | None:
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return value.strip() if isinstance(value, str) else value

    @field_validator('email')
    @classmethod
    def check_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_email_strict(value)

    @field_validator('birth_date')
    @classmethod
    def birth_not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError('Дата рождения не может быть в будущем')
        return value


class ReviewFormSchema(BaseModel):
    author_name: str = Field(min_length=2, max_length=120)
    rating: int = Field(ge=1, le=5)
    text: str = Field(min_length=10, max_length=2000)
    section_title: str | None = Field(default=None, max_length=120)

    @field_validator('author_name')
    @classmethod
    def check_author_name(cls, value: str) -> str:
        return validate_person_name(value, 'Имя')

    @field_validator('section_title', mode='before')
    @classmethod
    def empty_section_to_none(cls, value: str | None) -> str | None:
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return value.strip() if isinstance(value, str) else value


class SignupFormSchema(BaseModel):
    last_name: str = Field(min_length=2, max_length=100)
    first_name: str = Field(min_length=2, max_length=100)
    patronymic: str | None = Field(default=None, max_length=100)
    phone_number: str = Field(min_length=1, max_length=18)
    email: str | None = None
    birth_date: date
    password: str = Field(min_length=PASSWORD_MIN_LEN, max_length=PASSWORD_MAX_LEN)
    password_confirm: str = Field(min_length=PASSWORD_MIN_LEN, max_length=PASSWORD_MAX_LEN)

    @field_validator('last_name')
    @classmethod
    def check_last_name(cls, value: str) -> str:
        return validate_person_name(value, 'Фамилия')

    @field_validator('first_name')
    @classmethod
    def check_first_name(cls, value: str) -> str:
        return validate_person_name(value, 'Имя')

    @field_validator('patronymic', mode='before')
    @classmethod
    def empty_patronymic(cls, value: str | None) -> str | None:
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return value.strip() if isinstance(value, str) else value

    @field_validator('patronymic')
    @classmethod
    def check_patronymic(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_person_name(value, 'Отчество')

    @field_validator('phone_number')
    @classmethod
    def check_phone(cls, value: str) -> str:
        return normalize_phone_number(value)

    @field_validator('email', mode='before')
    @classmethod
    def empty_email_to_none(cls, value: str | None) -> str | None:
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return value.strip() if isinstance(value, str) else value

    @field_validator('email')
    @classmethod
    def check_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_email_strict(value)

    @field_validator('birth_date')
    @classmethod
    def birth_not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError('Дата рождения не может быть в будущем')
        return value

    @field_validator('password_confirm')
    @classmethod
    def passwords_match(cls, value: str, info) -> str:
        password = info.data.get('password')
        if password is not None and value != password:
            raise ValueError('Пароли не совпадают')
        return value


class LoginFormSchema(BaseModel):
    phone_number: str = Field(min_length=1, max_length=18)
    password: str = Field(min_length=1, max_length=PASSWORD_MAX_LEN)

    @field_validator('phone_number')
    @classmethod
    def check_phone(cls, value: str) -> str:
        return normalize_phone_number(value)
