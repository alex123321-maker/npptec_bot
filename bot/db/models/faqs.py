from sqlalchemy import Column, Integer, String, Boolean, Text
from ..base import Base

class Faq(Base):
    __tablename__ = 'faqs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False)
    short_description = Column(String, nullable=False)
    document = Column(String, nullable=True)
    display_in_keyboard = Column(Boolean, default=False)