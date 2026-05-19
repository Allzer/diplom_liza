from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import relationship

from database import Base

__all__ = ['SportSectionModel', 'SectionRegistrationModel', 'ReviewModel']


class SportSectionModel(Base):
    __tablename__ = 'sport_sections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=False)
    schedule = Column(String(200), nullable=False)
    trainer = Column(String(120), nullable=False)
    age_group = Column(String(80), nullable=False)
    price = Column(String(60), nullable=False)
    image_key = Column(String(40), nullable=False, default='fitness')
    is_active = Column(Boolean, nullable=False, default=True)

    registrations = relationship('SectionRegistrationModel', back_populates='section')


class SectionRegistrationModel(Base):
    __tablename__ = 'section_registrations'

    id = Column(Uuid, primary_key=True)
    section_id = Column(Integer, ForeignKey('sport_sections.id'), nullable=False)
    last_name = Column(Text, nullable=False)
    first_name = Column(Text, nullable=False)
    patronymic = Column(Text, nullable=True)
    phone_number = Column(String(17), nullable=False)
    email = Column(String(80), nullable=True)
    birth_date = Column(String(20), nullable=False)
    comment = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default='new')
    created_at = Column(String(30), nullable=False)
    user_id = Column(Uuid, nullable=True)

    section = relationship('SportSectionModel', back_populates='registrations')


class ReviewModel(Base):
    __tablename__ = 'reviews'

    id = Column(Uuid, primary_key=True)
    author_name = Column(String(120), nullable=False)
    section_title = Column(String(120), nullable=True)
    rating = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(String(30), nullable=False)
    is_published = Column(Boolean, nullable=False, default=True)
