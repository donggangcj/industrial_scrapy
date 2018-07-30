# -*- coding: utf-8 -*-

from .base import Base
import time
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship


class Industrial(Base):
    __tablename__ = "industrial"
    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String(1024))
    url = Column(String(255))
    area = Column(String(255))
    nature = Column(String(255))
    origin = Column(String(255))
    time = Column(Integer,default=time.time())
    keyword = Column(String(255))
    # data = Column(Text)

