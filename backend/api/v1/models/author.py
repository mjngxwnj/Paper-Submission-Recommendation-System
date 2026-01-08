from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from .base import Base

class Author(Base):
    __tablename__ = "author"
    __table_args__ = {"schema": "core"}

    orcid: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # papers = relationship("Paper", secondary="core.paper_author", back_populates="authors")
