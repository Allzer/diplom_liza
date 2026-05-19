from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from database import SessionDep
from src.data.seed_sections import seed_sections_if_empty
from src.models.sections import ReviewModel, SectionRegistrationModel, SportSectionModel

BASE_DIR = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))

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


@router.get('/', response_class=HTMLResponse)
async def home(request: Request, session: SessionDep):
    sections = await _get_sections(session)
    reviews = (await _get_reviews(session))[:3]
    return templates.TemplateResponse(
        request,
        'index.html',
        {'page_title': 'Главная', 'sections': sections[:3], 'reviews': reviews},
    )


@router.get('/about', response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(request, 'about.html', {'page_title': 'О центре'})


@router.get('/sections', response_class=HTMLResponse)
async def sections_page(request: Request, session: SessionDep):
    sections = await _get_sections(session)
    return templates.TemplateResponse(
        request,
        'sections.html',
        {'page_title': 'Секции', 'sections': sections},
    )


@router.get('/gallery', response_class=HTMLResponse)
async def gallery(request: Request):
    return templates.TemplateResponse(
        request,
        'gallery.html',
        {'page_title': 'Галерея', 'gallery_items': GALLERY_ITEMS},
    )


@router.get('/reviews', response_class=HTMLResponse)
async def reviews_page(request: Request, session: SessionDep, success: str | None = None):
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
    rating = max(1, min(5, rating))
    session.add(
        ReviewModel(
            id=uuid4(),
            author_name=author_name.strip(),
            section_title=section_title.strip() or None,
            rating=rating,
            text=text.strip(),
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
    return templates.TemplateResponse(
        request,
        'register.html',
        {
            'page_title': 'Запись в секцию',
            'sections': sections,
            'selected_section_id': section_id,
            'success': success == '1',
            'error': error,
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
    section = await session.get(SportSectionModel, section_id)
    if not section or not section.is_active:
        return RedirectResponse(url='/register?error=section', status_code=303)

    session.add(
        SectionRegistrationModel(
            id=uuid4(),
            section_id=section_id,
            last_name=last_name.strip(),
            first_name=first_name.strip(),
            patronymic=patronymic.strip() or None,
            phone_number=phone_number.strip(),
            email=email.strip() or None,
            birth_date=birth_date.strip(),
            comment=comment.strip() or None,
            status='new',
            created_at=datetime.now().strftime('%d.%m.%Y %H:%M'),
        )
    )
    await session.commit()
    return RedirectResponse(url='/register?success=1', status_code=303)


@router.get('/contacts', response_class=HTMLResponse)
async def contacts(request: Request):
    return templates.TemplateResponse(request, 'contacts.html', {'page_title': 'Контакты'})
