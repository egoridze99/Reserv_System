from db import db


class AbstractBaseModel(db.Model):
    __abstract__ = True
