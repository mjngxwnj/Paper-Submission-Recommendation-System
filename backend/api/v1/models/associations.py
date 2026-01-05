# from .base import Base
# from sqlalchemy import Table, Column, ForeignKey, Integer, String

# paper_author = Table(
#     "paper_author",
#     Base.metadata,
#     Column("paper_doi", String, ForeignKey("core.paper.doi"), primary_key=True),
#     Column("author_orcid", String, ForeignKey("core.author.orcid"), primary_key=True),
#     schema="core"
# )

# paper_keyword = Table(
#     "paper_keyword",
#     Base.metadata,
#     Column("paper_doi", String, ForeignKey("core.paper.doi"), primary_key=True),
#     Column("keyword_id", Integer, ForeignKey("core.keyword.id"), primary_key=True),
#     schema="core"
# )
