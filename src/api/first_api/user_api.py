from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from src.models.models_for_courses import UsersModel
from database import SessionDep

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/clients",
    tags=["clients"]
)

@router.get('/')
async def get_user(session : SessionDep):
    try:
        result_list = []
        query = select(UsersModel).where(UsersModel.is_deleted == False)
        query = await session.execute(query)
        query = query.scalars().all()
        for i in query:
            result = {
                'id': i.id,
                'last_name': i.last_name,
                'first_name': i.first_name,
                'patronymic': i.patronymic,
                'phone_number': i.phone_number,
                'email': i.email,
                'birth_date': i.birth_date,
            }
            result_list.append(result)
        return result_list
    except Exception as er:
        print(er)
        logger.exception('Не удалось выполнить чтение из БД: %s', str(er))
        raise HTTPException(status_code=500, detail='Ошибка ответа сервера')