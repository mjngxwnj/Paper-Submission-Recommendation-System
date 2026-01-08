from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import Computed
from pgvector.sqlalchemy import Vector
from .base import Base

class Paper(Base):
    __tablename__ = "paper"
    __table_args__ = {"schema": "core"}

    doi: Mapped[str] = mapped_column(Text, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[str] = mapped_column(Text)
    abstract_link: Mapped[str] = mapped_column(Text)
    open_access: Mapped[bool] = mapped_column(Boolean)
    publication_day: Mapped[int] = mapped_column(Integer)
    publication_month: Mapped[int] = mapped_column(Integer)
    publication_year: Mapped[int] = mapped_column(Integer)
    venue_id: Mapped[int] = mapped_column(ForeignKey("core.venue.id"))
    #ingestion_source_id: Mapped[int] = mapped_column(ForeignKey("core.ingestion_source.id"))

    # For embedding / RCM
    combined_text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(768))
    tsv: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('english', coalesce(combined_text, ''))", persisted=True)
    )

    # Relationships
    venue = relationship("Venue", back_populates="papers")
    # author = relationship("Author", secondary="core.paper_author", back_populates="papers")
    # keyword = relationship("Keyword", secondary="core.paper_keyword", back_populates="papers")
    #ingestion_source: Mapped["IngestionSource"] = relationship("IngestionSource", back_populates="papers")
