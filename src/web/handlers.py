from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError

from src.web.helpers import today_iso

HTML_FORM_PATHS = {'/register', '/reviews', '/login', '/signup'}


def register_exception_handlers(app, templates: Jinja2Templates) -> None:
    templates.env.globals['today_iso'] = today_iso

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        path = request.url.path
        if path not in HTML_FORM_PATHS:
            return JSONResponse(status_code=422, content={'detail': exc.errors()})

        if path == '/register':
            return RedirectResponse(url='/register?error=validation', status_code=303)

        if path == '/login':
            return RedirectResponse(url='/login?error=validation', status_code=303)

        if path == '/signup':
            return RedirectResponse(url='/signup?error=validation', status_code=303)

        if path == '/reviews':
            return templates.TemplateResponse(
                request,
                'reviews.html',
                {
                    'page_title': 'Отзывы',
                    'reviews': [],
                    'sections': [],
                    'field_errors': {},
                    'form_error': 'Проверьте правильность заполнения формы.',
                    'form_values': {},
                    'current_user': None,
                },
                status_code=422,
            )

        return JSONResponse(status_code=422, content={'detail': exc.errors()})

    @app.exception_handler(SQLAlchemyError)
    async def database_error_handler(request: Request, exc: SQLAlchemyError):
        if request.url.path.startswith('/clients'):
            return JSONResponse(
                status_code=503,
                content={'detail': 'Временная ошибка базы данных. Попробуйте позже.'},
            )

        if request.url.path in HTML_FORM_PATHS:
            return templates.TemplateResponse(
                request,
                'error.html',
                {
                    'page_title': 'Ошибка',
                    'message': 'Не удалось сохранить данные. Проверьте подключение к базе и повторите попытку.',
                    'current_user': None,
                },
                status_code=503,
            )

        return HTMLResponse(
            content='<h1>Сервис временно недоступен</h1>',
            status_code=503,
        )
