from sqlalchemy import func

from db import db
from models.abstract import AbstractBaseModel


class GuestComment(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    text = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, default=func.localtimestamp())
    author_id = db.Column(db.Integer, db.ForeignKey("user.id", name="author_id"))

    author = db.relationship("User")

    @staticmethod
    def to_json(comment: "GuestComment"):
        return {
            "id": comment.id,
            "text": comment.text,
            "created_at": comment.created_at.strftime('%Y-%m-%dT%H:%M'),
            "author": comment.author.to_json(comment.author)["fullname"]
        }
