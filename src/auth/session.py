from uuid import UUID

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models_for_courses import UsersModel

SESSION_USER_KEY = 'user_id'


def login_user(request: Request, user_id: UUID) -> None:
    request.session[SESSION_USER_KEY] = str(user_id)


def logout_user(request: Request) -> None:
    request.session.pop(SESSION_USER_KEY, None)


def get_session_user_id(request: Request) -> UUID | None:
    raw = request.session.get(SESSION_USER_KEY)
    if not raw:
        return None
    try:
        return UUID(str(raw))
    except ValueError:
        return None


async def get_current_user(
    request: Request,
    session: AsyncSession,
) -> UsersModel | None:
    user_id = get_session_user_id(request)
    if not user_id:
        return None
    result = await session.execute(
        select(UsersModel).where(
            UsersModel.id == user_id,
            UsersModel.is_deleted == False,
        )
    )
    return result.scalar_one_or_none()
