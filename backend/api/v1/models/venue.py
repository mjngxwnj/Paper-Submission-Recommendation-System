from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from api.v1.models.base import Base

class Venue(Base):
    __tablename__ = "venue"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)

    papers = relationship("Paper", back_populates="venue")
