from datetime import datetime
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import EmailStr, ValidationError
from sqlalchemy import select

from database import SessionDep
from src.auth.passwords import hash_password, verify_password
from src.auth.session import get_current_user, login_user, logout_user
from src.models.models_for_courses import UsersModel
from src.schemas.forms import LoginFormSchema, SignupFormSchema
from src.web.helpers import today_iso, validation_errors_dict
from src.web.templates_ctx import templates

router = APIRouter(tags=['auth'])


def _signup_values(
    *,
    last_name: str = '',
    first_name: str = '',
    patronymic: str = '',
    phone_number: str = '',
    email: str = '',
    birth_date: str = '',
) -> dict:
    return {
        'last_name': last_name,
        'first_name': first_name,
        'patronymic': patronymic or '',
        'phone_number': phone_number,
        'email': email or '',
        'birth_date': birth_date,
    }


@router.get('/login', response_class=HTMLResponse)
async def login_page(
    request: Request,
    session: SessionDep,
    next: str = '/profile',
    error: str | None = None,
):
    user = await get_current_user(request, session)
    if user:
        return RedirectResponse(url=next or '/profile', status_code=303)
    form_error = None
    if error == 'validation':
        form_error = 'Проверьте формат телефона и пароль.'
    return templates.TemplateResponse(
        request,
        'login.html',
        {
            'page_title': 'Вход',
            'next': next,
            'field_errors': {},
            'form_error': form_error,
            'form_values': {'phone_number': '', 'password': ''},
            'current_user': None,
        },
    )


@router.post('/login', response_class=HTMLResponse)
async def login_submit(
    request: Request,
    session: SessionDep,
    phone_number: str = Form(...),
    password: str = Form(...),
    next: str = Form('/profile'),
):
    try:
        data = LoginFormSchema.model_validate(
            {'phone_number': phone_number, 'password': password}
        )
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            'login.html',
            {
                'page_title': 'Вход',
                'next': next,
                'field_errors': validation_errors_dict(exc),
                'form_error': 'Проверьте логин и пароль.',
                'form_values': {'phone_number': phone_number, 'password': ''},
                'current_user': None,
            },
            status_code=422,
        )

    result = await session.execute(
        select(UsersModel).where(
            UsersModel.phone_number == data.phone_number,
            UsersModel.is_deleted == False,
        )
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hash_pass):
        return templates.TemplateResponse(
            request,
            'login.html',
            {
                'page_title': 'Вход',
                'next': next,
                'field_errors': {},
                'form_error': 'Неверный телефон или пароль.',
                'form_values': {'phone_number': data.phone_number, 'password': ''},
                'current_user': None,
            },
            status_code=422,
        )

    login_user(request, user.id)
    return RedirectResponse(url=next or '/profile', status_code=303)


@router.get('/signup', response_class=HTMLResponse)
async def signup_page(request: Request, session: SessionDep):
    user = await get_current_user(request, session)
    if user:
        return RedirectResponse(url='/profile', status_code=303)
    return templates.TemplateResponse(
        request,
        'signup.html',
        {
            'page_title': 'Регистрация',
            'field_errors': {},
            'form_error': None,
            'form_values': _signup_values(),
            'current_user': None,
        },
    )


@router.post('/signup', response_class=HTMLResponse)
async def signup_submit(
    request: Request,
    session: SessionDep,
    email: Annotated[EmailStr, Form()],
    last_name: str = Form(...),
    first_name: str = Form(...),
    patronymic: str = Form(''),
    phone_number: str = Form(...),
    birth_date: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
):
    raw = _signup_values(
        last_name=last_name,
        first_name=first_name,
        patronymic=patronymic,
        phone_number=phone_number,
        email=email,
        birth_date=birth_date,
    )

    try:
        data = SignupFormSchema.model_validate(
            {
                'last_name': last_name,
                'first_name': first_name,
                'patronymic': patronymic,
                'phone_number': phone_number,
                'email': email or None,
                'birth_date': birth_date,
                'password': password,
                'password_confirm': password_confirm,
            }
        )
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            'signup.html',
            {
                'page_title': 'Регистрация',
                'field_errors': validation_errors_dict(exc),
                'form_error': 'Исправьте ошибки в форме.',
                'form_values': raw,
                'current_user': None,
            },
            status_code=422,
        )

    existing = await session.execute(
        select(UsersModel).where(UsersModel.phone_number == data.phone_number)
    )
    if existing.scalar_one_or_none():
        return templates.TemplateResponse(
            request,
            'signup.html',
            {
                'page_title': 'Регистрация',
                'field_errors': {'phone_number': 'Пользователь с таким телефоном уже зарегистрирован.'},
                'form_error': 'Войдите в аккаунт или укажите другой номер.',
                'form_values': raw,
                'current_user': None,
            },
            status_code=422,
        )

    if data.email:
        existing_email = await session.execute(
            select(UsersModel).where(UsersModel.email == data.email)
        )
        if existing_email.scalar_one_or_none():
            return templates.TemplateResponse(
                request,
                'signup.html',
                {
                    'page_title': 'Регистрация',
                    'field_errors': {'email': 'Этот email уже используется.'},
                    'form_error': 'Укажите другой email.',
                    'form_values': raw,
                    'current_user': None,
                },
                status_code=422,
            )

    user_id = uuid4()
    now = datetime.now().strftime('%d.%m.%Y %H:%M')
    user = UsersModel(
        id=user_id,
        last_name=data.last_name,
        first_name=data.first_name,
        patronymic=data.patronymic,
        phone_number=data.phone_number,
        email=data.email,
        birth_date=data.birth_date.isoformat(),
        hash_pass=hash_password(data.password),
        created_at=now,
        created_by=user_id,
        updated_by=user_id,
        updated_at=now,
        is_deleted=False,
    )
    session.add(user)
    await session.commit()

    login_user(request, user_id)
    return RedirectResponse(url='/profile?welcome=1', status_code=303)


@router.post('/logout', response_class=HTMLResponse)
async def logout(request: Request):
    logout_user(request)
    return RedirectResponse(url='/', status_code=303)
