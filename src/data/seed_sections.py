from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.sections import SportSectionModel

DEFAULT_SECTIONS = [
    {
        'title': 'Общая физическая подготовка',
        'description': 'Комплексные тренировки для развития силы, выносливости и координации. Подходит начинающим и продолжающим.',
        'schedule': 'Пн, Ср, Пт — 18:00–19:30',
        'trainer': 'Иванов А.С.',
        'age_group': '16+',
        'price': '3 500 ₽ / мес.',
        'image_key': 'fitness',
    },
    {
        'title': 'Функциональный тренинг',
        'description': 'Интенсивные занятия с собственным весом и оборудованием. Укрепление корпуса и суставов.',
        'schedule': 'Вт, Чт — 19:00–20:15',
        'trainer': 'Петрова М.В.',
        'age_group': '18+',
        'price': '4 000 ₽ / мес.',
        'image_key': 'functional',
    },
    {
        'title': 'Детская спортивная группа',
        'description': 'Игровые и обучающие занятия для формирования двигательных навыков и здорового образа жизни.',
        'schedule': 'Сб — 10:00–11:30',
        'trainer': 'Сидоров К.П.',
        'age_group': '7–14 лет',
        'price': '2 800 ₽ / мес.',
        'image_key': 'kids',
    },
    {
        'title': 'Стретчинг и мобильность',
        'description': 'Растяжка, работа с фасциями и восстановление после нагрузок.',
        'schedule': 'Пн, Чт — 20:00–21:00',
        'trainer': 'Козлова Е.А.',
        'age_group': '14+',
        'price': '2 500 ₽ / мес.',
        'image_key': 'stretch',
    },
    {
        'title': 'Силовая подготовка',
        'description': 'Программа со штангой и гантелями под контролем тренера. Техника и прогрессия нагрузок.',
        'schedule': 'Вт, Пт — 17:30–19:00',
        'trainer': 'Иванов А.С.',
        'age_group': '18+',
        'price': '4 500 ₽ / мес.',
        'image_key': 'strength',
    },
]


async def seed_sections_if_empty(session: AsyncSession) -> None:
    result = await session.execute(select(SportSectionModel).limit(1))
    if result.scalar_one_or_none():
        return
    for item in DEFAULT_SECTIONS:
        session.add(SportSectionModel(**item))
    await session.commit()
