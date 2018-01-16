#!/usr/bin/python
#coding:utf8

from sqlalchemy import (
    Column,
    JSON,
    Integer,
    String,
    DateTime
)

from database.base_db import Base, engine

class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True)
    company_size = Column(String(30))
    company_short_name = Column(String(100))
    company_full_name = Column(String(100))
    finance_stage = Column(String(20))
    company_label_list = Column(JSON)


class Position(Base):
    __tablename__ = 'position'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer)
    position_name = Column(String(30))
    work_year = Column(String(20))
    education = Column(String(10))
    job_nature = Column(String(10))
    create_time = Column(DateTime)
    city = Column(String(20))
    industry_field = Column(String(100))
    position_advantage = Column(String(100))
    salary = Column(String(50))
    position_lables = Column(JSON)
    industry_lables = Column(JSON)
    district = Column(String(20))
    first_type = Column(String(20))
    second_type = Column(String(20))

    job_advantage = Column(String(200))
    description = Column(JSON)
    location = Column(String(200))
    publisher_name = Column(String(50))
    tend_to_talk = Column(JSON)
    deal_resume = Column(JSON)
    active_time = Column(String(20))

if __name__ == "__main__":
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
