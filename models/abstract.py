import json

from sqlalchemy import func

from db import db


class ChangeLogMixin:
    """Журнал изменений сущности: кто и когда поменял, снимки old/new в JSON"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=func.localtimestamp())
    author = db.Column(db.String)

    old = db.Column(db.Text)
    new = db.Column(db.Text)

    @staticmethod
    def to_json(log):
        return {
            "id": log.id,
            "created_at": log.created_at.strftime('%Y-%m-%dT%H:%M'),
            "author": log.author,
            "old": json.loads(log.old),
            "new": json.loads(log.new)
        }
