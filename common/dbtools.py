# -*- coding: utf-8 -*-

import os
from sqlalchemy import create_engine, text
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from job.models.base import Base

MYSQL_HOST = os.getenv("MYSQL_HOST", "117.50.19.70")
MYSQL_DBNAME = os.getenv("MYSQL_DBNAME", "industrial-internet")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWD = os.getenv("MYSQL_PASSWD", "root")
MYSQL_PORT = os.getenv("MYSQL_PORT", 30071)

DATABASE_URL = "mysql+pymysql://{}:{}@{}:{}/{}".format(MYSQL_USER,
                                                       MYSQL_PASSWD,
                                                       MYSQL_HOST,
                                                       MYSQL_PORT,
                                                       MYSQL_DBNAME
                                                       )
engine = create_engine(DATABASE_URL,
                       encoding="utf8",
                       connect_args={'charset': 'utf8'})


#上下文管理装饰器
@contextmanager
def sqlalchemy_session():
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.expunge_all()
        session.close()


def orm_session_control(orm_func):
    """控制SQLAlchemy session的动态创建"""

    def decorator(*args, **kwargs):
        with sqlalchemy_session() as session:
            kwargs["session"] = session
            return orm_func(*args, **kwargs)

    return decorator


class DatabaseAgent():
    """封装SQLAlchemy的逻辑做一些db CRUD的工作"""

    orm_model = None

    #查询函数
    @orm_session_control
    def get(self, filter_kwargs={}, just_first=True, orm_model=None, session=None):
        query_result = session.query(orm_model).filter_by(**filter_kwargs)
        if just_first:
            return query_result.first()
        else:
            return query_result.all()

    #条件范围查询
    @orm_session_control
    def get_by_range(self,orm_model=None, session=None,filter_sql={}):
        query_result = session.query(orm_model).filter_by(text(filter_sql)).all()
        return query_result

    #增加操作
    @orm_session_control
    def add(self, kwargs, orm_model=None, session=None):
        new_orm = orm_model(**kwargs)
        session.add(new_orm)
        session.commit()
        return new_orm

    #更新操作
    @orm_session_control
    def update(self, filter_kwargs, method_kwargs,
               need_commit=True, orm_model=None, session=None):
        orm_model = orm_model if orm_model is not None else self.orm_model
        session.query(orm_model).filter_by(**filter_kwargs).update(method_kwargs)
        if need_commit:
            session.commit()


def create_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)


def drop_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.drop_all(engine)
