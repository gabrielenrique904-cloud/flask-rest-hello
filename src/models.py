import enum
from typing import List
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class MediaType(enum.Enum):
    IMAGE = "image"
    VIDEO = "video"


class Follower(db.Model):
    # user_from follows user_to
    user_from_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    user_to_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

    user_from: Mapped["User"] = relationship(foreign_keys=[user_from_id], back_populates="following")
    user_to: Mapped["User"] = relationship(foreign_keys=[user_to_id], back_populates="followers")

    def serialize(self):
        return {
            "user_from_id": self.user_from_id,
            "user_to_id": self.user_to_id,
        }


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    firstname: Mapped[str] = mapped_column(String(50), nullable=True)
    lastname: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    posts: Mapped[List["Post"]] = relationship(back_populates="user")
    comments: Mapped[List["Comment"]] = relationship(back_populates="author")
    likes: Mapped[List["Like"]] = relationship(back_populates="user")
    following: Mapped[List["Follower"]] = relationship(
        foreign_keys=[Follower.user_from_id], back_populates="user_from")
    followers: Mapped[List["Follower"]] = relationship(
        foreign_keys=[Follower.user_to_id], back_populates="user_to")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            # do not serialize the password, its a security breach
        }


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="posts")
    media: Mapped[List["Media"]] = relationship(back_populates="post")
    comments: Mapped[List["Comment"]] = relationship(back_populates="post")
    likes: Mapped[List["Like"]] = relationship(back_populates="post")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "likes": len(self.likes),
            "media": [m.serialize() for m in self.media],
        }


class Media(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[MediaType] = mapped_column(Enum(MediaType), nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), nullable=False)

    post: Mapped["Post"] = relationship(back_populates="media")

    def serialize(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "url": self.url,
            "post_id": self.post_id,
        }


class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), nullable=False)

    author: Mapped["User"] = relationship(back_populates="comments")
    post: Mapped["Post"] = relationship(back_populates="comments")

    def serialize(self):
        return {
            "id": self.id,
            "comment_text": self.comment_text,
            "author_id": self.author_id,
            "post_id": self.post_id,
        }


class Like(db.Model):
    # a user can like a post only once
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), primary_key=True)

    user: Mapped["User"] = relationship(back_populates="likes")
    post: Mapped["Post"] = relationship(back_populates="likes")

    def serialize(self):
        return {
            "user_id": self.user_id,
            "post_id": self.post_id,
        }


# Generate the UML diagram with: $ python src/models.py
if __name__ == "__main__":
    import os
    from eralchemy2 import render_er

    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "diagram.png")
    try:
        render_er(db.Model, output)
        print("Success! Check the diagram.png file")
    except Exception as e:
        print("There was a problem generating the diagram")
        raise e
