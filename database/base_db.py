#!/usr/bin/python
#coding:utf8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = create_engine('mysql+pymysql://root:1432@127.0.0.1/jobsdb?charset=utf8', echo=False)

Session = sessionmaker(bind=engine, autoflush=False)