# Database configuration

from datetime import datetime

from sqlalchemy import create_engine, String
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, validates, sessionmaker
from sqlalchemy_utils import create_database


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)

    @validates('title')
    def validate_title(self, key, title):
        if not title.isprintable():
            raise ValueError("Title must be a string with only printable symbols")
        return title

    @validates('description')
    def validate_description(self, key, description):
        if not description.replace('\r\n', ' ').isprintable():
            raise ValueError("Title must be a string with only printable symbols or CRLF")
        return description

    def __repr__(self):
        return '<Task %r>' % self.title

    def to_json(self):
        return {'id': self.id,
                'title': self.title,
                'description': self.description,
                'created_at': self.created_at,
                'updated_at': self.updated_at}


def create_new_database(url: str) -> None:
    """
    Creates empty base
    :param url: URL, where the base will be created
    :return: None
    """
    db = Base()
    engine = create_engine(url, echo=True)
    create_database(url)
    db.metadata.create_all(engine)
    Session = sessionmaker(engine)
    with Session() as session:
        session.commit()
    print('Base created at', url)
