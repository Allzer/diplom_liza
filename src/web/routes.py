from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import SessionDep
from src.auth.session import get_current_user
from src.data.seed_sections import seed_sections_if_empty
from src.models.sections import ReviewModel, SectionRegistrationModel, SportSectionModel
from src.schemas.forms import RegistrationFormSchema, ReviewFormSchema
from src.web.helpers import validation_errors_dict
from src.web.templates_ctx import templates

router = APIRouter(tags=['web'])

GALLERY_ITEMS = [
    {'title': 'Разминка перед тренировкой', 'category': 'ОФП', 'image_key': 'warmup'},
    {'title': 'Функциональная станция', 'category': 'Функциональный', 'image_key': 'functional'},
    {'title': 'Детская группа', 'category': 'Дети', 'image_key': 'kids'},
    {'title': 'Силовой зал', 'category': 'Силовая', 'image_key': 'strength'},
    {'title': 'Стретчинг', 'category': 'Восстановление', 'image_key': 'stretch'},
    {'title': 'Командная работа', 'category': 'ОФП', 'image_key': 'team'},
]


async def _get_sections(session: SessionDep) -> list[SportSectionModel]:
    await seed_sections_if_empty(session)
    result = await session.execute(
        select(SportSectionModel).where(SportSectionModel.is_active == True).order_by(SportSectionModel.id)
    )
    return list(result.scalars().all())


async def _get_reviews(session: SessionDep) -> list[ReviewModel]:
    result = await session.execute(
        select(ReviewModel)
        .where(ReviewModel.is_published == True)
        .order_by(ReviewModel.created_at.desc())
        .limit(20)
    )
    return list(result.scalars().all())


async def _get_registrations_by_phone(
    session: SessionDep,
    phone_number: str,
) -> list[SectionRegistrationModel]:
    result = await session.execute(
        select(SectionRegistrationModel)
        .options(selectinload(SectionRegistrationModel.section))
        .where(
            SectionRegistrationModel.phone_number == phone_number,
            SectionRegistrationModel.status != 'cancelled',
        )
        .order_by(SectionRegistrationModel.created_at.desc())
    )
    return list(result.scalars().all())


async def _get_user_registration(
    session: SessionDep,
    registration_id: UUID,
    user_id: UUID,
    phone_number: str,
) -> SectionRegistrationModel | None:
    result = await session.execute(
        select(SectionRegistrationModel).where(
            SectionRegistrationModel.id == registration_id,
            SectionRegistrationModel.phone_number == phone_number,
            SectionRegistrationModel.user_id == user_id,
            SectionRegistrationModel.status != 'cancelled',
        )
    )
    return result.scalar_one_or_none()


def _form_values(
    *,
    section_id: int | str | None = None,
    last_name: str = '',
    first_name: str = '',
    patronymic: str = '',
    phone_number: str = '',
    email: str = '',
    birth_date: str = '',
    comment: str = '',
    author_name: str = '',
    rating: int | str = 5,
    text: str = '',
    section_title: str = '',
) -> dict:
    return {
        'section_id': section_id,
        'last_name': last_name,
        'first_name': first_name,
        'patronymic': patronymic or '',
        'phone_number': phone_number,
        'email': email or '',
        'birth_date': birth_date,
        'comment': comment or '',
        'author_name': author_name,
        'rating': rating,
        'text': text,
        'section_title': section_title or '',
    }


@router.get('/', response_class=HTMLResponse)
async def home(request: Request, session: SessionDep):
    sections = await _get_sections(session)
    reviews = (await _get_reviews(session))[:3]
    current_user = await get_current_user(request, session)
    return templates.TemplateResponse(
        request,
        'index.html',
        {
            'page_title': 'Главная',
            'sections': sections[:3],
            'reviews': reviews,
            'current_user': current_user,
        },
    )


@router.get('/about', response_class=HTMLResponse)
async def about(request: Request, session: SessionDep):
    return templates.TemplateResponse(
        request,
        'about.html',
        {'page_title': 'О центре', 'current_user': await get_current_user(request, session)},
    )


@router.get('/sections', response_class=HTMLResponse)
async def sections_page(request: Request, session: SessionDep):
    sections = await _get_sections(session)
    return templates.TemplateResponse(
        request,
        'sections.html',
        {'page_title': 'Секции', 'sections': sections, 'current_user': await get_current_user(request, session)},
    )


@router.get('/gallery', response_class=HTMLResponse)
async def gallery(request: Request, session: SessionDep):
    return templates.TemplateResponse(
        request,
        'gallery.html',
        {
            'page_title': 'Галерея',
            'gallery_items': GALLERY_ITEMS,
            'current_user': await get_current_user(request, session),
        },
    )


@router.get('/reviews', response_class=HTMLResponse)
async def reviews_page(
    request: Request,
    session: SessionDep,
    success: str | None = None,
):
    reviews = await _get_reviews(session)
    sections = await _get_sections(session)
    return templates.TemplateResponse(
        request,
        'reviews.html',
        {
            'page_title': 'Отзывы',
            'reviews': reviews,
            'sections': sections,
            'success': success == '1',
            'field_errors': {},
            'form_error': None,
            'form_values': _form_values(),
            'current_user': await get_current_user(request, session),
        },
    )


@router.post('/reviews', response_class=HTMLResponse)
async def add_review(
    request: Request,
    session: SessionDep,
    author_name: str = Form(...),
    rating: int = Form(...),
    text: str = Form(...),
    section_title: str = Form(''),
):
    sections = await _get_sections(session)
    raw = _form_values(author_name=author_name, rating=rating, text=text, section_title=section_title)

    try:
        data = ReviewFormSchema.model_validate(
            {
                'author_name': author_name,
                'rating': rating,
                'text': text,
                'section_title': section_title,
            }
        )
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            'reviews.html',
            {
                'page_title': 'Отзывы',
                'reviews': await _get_reviews(session),
                'sections': sections,
                'success': False,
                'field_errors': validation_errors_dict(exc),
                'form_error': 'Исправьте ошибки в форме и отправьте снова.',
                'form_values': raw,
                'current_user': await get_current_user(request, session),
            },
            status_code=422,
        )

    session.add(
        ReviewModel(
            id=uuid4(),
            author_name=data.author_name,
            section_title=data.section_title,
            rating=data.rating,
            text=data.text,
            created_at=datetime.now().strftime('%d.%m.%Y %H:%M'),
            is_published=True,
        )
    )
    await session.commit()
    return RedirectResponse(url='/reviews?success=1', status_code=303)


@router.get('/register', response_class=HTMLResponse)
async def register_form(
    request: Request,
    session: SessionDep,
    section_id: int | None = None,
    success: str | None = None,
    error: str | None = None,
):
    sections = await _get_sections(session)
    user = await get_current_user(request, session)
    error_messages = {
        'section': 'Выбранная секция не найдена или недоступна.',
        'validation': 'Некорректные данные формы. Проверьте поля и попробуйте снова.',
        'auth': 'Войдите в аккаунт, чтобы записаться в секцию.',
    }
    defaults = _form_values(section_id=section_id or '')
    if user:
        defaults.update(
            {
                'last_name': user.last_name,
                'first_name': user.first_name,
                'patronymic': user.patronymic or '',
                'phone_number': user.phone_number,
                'email': user.email or '',
                'birth_date': user.birth_date,
            }
        )
    return templates.TemplateResponse(
        request,
        'register.html',
        {
            'page_title': 'Запись в секцию',
            'sections': sections,
            'selected_section_id': section_id,
            'success': success == '1',
            'form_error': error_messages.get(error) if error else None,
            'field_errors': {},
            'form_values': defaults,
            'current_user': user,
            'phone_readonly': user is not None,
        },
    )


@router.post('/register', response_class=HTMLResponse)
async def register_submit(
    request: Request,
    session: SessionDep,
    section_id: int = Form(...),
    last_name: str = Form(...),
    first_name: str = Form(...),
    patronymic: str = Form(''),
    phone_number: str = Form(...),
    email: str = Form(''),
    birth_date: str = Form(...),
    comment: str = Form(''),
):
    user = await get_current_user(request, session)
    if not user:
        return RedirectResponse(url='/login?next=/register', status_code=303)

    sections = await _get_sections(session)
    raw = _form_values(
        section_id=section_id,
        last_name=last_name,
        first_name=first_name,
        patronymic=patronymic,
        phone_number=user.phone_number,
        email=email,
        birth_date=birth_date,
        comment=comment,
    )

    try:
        data = RegistrationFormSchema.model_validate(
            {
                'section_id': section_id,
                'last_name': last_name,
                'first_name': first_name,
                'patronymic': patronymic,
                'phone_number': user.phone_number,
                'email': email or None,
                'birth_date': birth_date,
                'comment': comment,
            }
        )
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            'register.html',
            {
                'page_title': 'Запись в секцию',
                'sections': sections,
                'selected_section_id': section_id,
                'success': False,
                'field_errors': validation_errors_dict(exc),
                'form_error': 'Исправьте ошибки в форме и отправьте снова.',
                'form_values': raw,
                'current_user': user,
                'phone_readonly': True,
            },
            status_code=422,
        )

    section = await session.get(SportSectionModel, data.section_id)
    if not section or not section.is_active:
        return templates.TemplateResponse(
            request,
            'register.html',
            {
                'page_title': 'Запись в секцию',
                'sections': sections,
                'selected_section_id': data.section_id,
                'success': False,
                'field_errors': {'section_id': 'Секция не найдена или закрыта для записи.'},
                'form_error': 'Выбранная секция недоступна.',
                'form_values': raw,
                'current_user': user,
                'phone_readonly': True,
            },
            status_code=422,
        )

    session.add(
        SectionRegistrationModel(
            id=uuid4(),
            section_id=data.section_id,
            last_name=data.last_name,
            first_name=data.first_name,
            patronymic=data.patronymic,
            phone_number=data.phone_number,
            email=data.email,
            birth_date=data.birth_date.isoformat(),
            comment=data.comment,
            status='new',
            created_at=datetime.now().strftime('%d.%m.%Y %H:%M'),
            user_id=user.id,
        )
    )
    await session.commit()
    return RedirectResponse(url='/profile?registered=1', status_code=303)


@router.get('/profile', response_class=HTMLResponse)
async def profile_page(
    request: Request,
    session: SessionDep,
    registered: str | None = None,
    welcome: str | None = None,
    cancelled: str | None = None,
    error: str | None = None,
):
    user = await get_current_user(request, session)
    if not user:
        return RedirectResponse(url='/login?next=/profile', status_code=303)

    registrations = await _get_registrations_by_phone(session, user.phone_number)
    error_messages = {
        'not_found': 'Запись не найдена или уже отменена.',
    }
    return templates.TemplateResponse(
        request,
        'profile.html',
        {
            'page_title': 'Мой профиль',
            'user': user,
            'registrations': registrations,
            'registered': registered == '1',
            'welcome': welcome == '1',
            'cancelled': cancelled == '1',
            'form_error': error_messages.get(error) if error else None,
            'current_user': user,
        },
    )


@router.post('/profile/registrations/{registration_id}/cancel', response_class=HTMLResponse)
async def cancel_registration(
    request: Request,
    session: SessionDep,
    registration_id: UUID,
):
    user = await get_current_user(request, session)
    if not user:
        return RedirectResponse(url='/login?next=/profile', status_code=303)

    registration = await _get_user_registration(
        session, registration_id, user.id, user.phone_number
    )
    if not registration:
        return RedirectResponse(url='/profile?error=not_found', status_code=303)

    registration.status = 'cancelled'
    await session.commit()
    return RedirectResponse(url='/profile?cancelled=1', status_code=303)


@router.get('/contacts', response_class=HTMLResponse)
async def contacts(request: Request, session: SessionDep):
    return templates.TemplateResponse(
        request,
        'contacts.html',
        {'page_title': 'Контакты', 'current_user': await get_current_user(request, session)},
    )
