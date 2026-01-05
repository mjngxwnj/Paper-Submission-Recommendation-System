from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from .base import Base

class Keyword(Base):
    __tablename__ = "keyword"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # Relationship back to papers is defined in Paper model
    # papers = relationship("Paper", secondary="core.paper_keyword", back_populates="keywords")
