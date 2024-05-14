from sqlalchemy import Column

from db import db
from models.abstract import AbstractBaseModel


class SbpTerminal(AbstractBaseModel):
    __tablename__ = 'sbp_terminal'

    id = Column(db.String, primary_key=True)
