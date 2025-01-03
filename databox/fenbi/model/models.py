from sqlalchemy import String, BigInteger, Text, func, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    create_time = mapped_column(DateTime, insert_default=func.now())
    update_time = mapped_column(DateTime, insert_default=func.now(), onupdate=func.now())
    is_deleted = mapped_column(Boolean, default=False)


class Paper(Base):
    __tablename__ = "fenbi_paper"

    paper_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(100))

    def __repr__(self) -> str:
        return f"Paper(paper_id={self.paper_id}, name={self.name})"


class Material(Base):
    __tablename__ = "fenbi_material"

    material_id: Mapped[int] = mapped_column(BigInteger)
    content: Mapped[str] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"Material(material_id={self.material_id}, content={self.content[:30]})"


class Question(Base):
    __tablename__ = "fenbi_question"

    question_id: Mapped[int] = mapped_column(BigInteger)
    content: Mapped[str] = mapped_column(Text)
    chapter_name: Mapped[str] = mapped_column(String(100))
    module: Mapped[str] = mapped_column(String(50))
    option_type: Mapped[int] = mapped_column()
    options: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    material_ids: Mapped[str] = mapped_column(Text)
    paper_id: Mapped[int] = mapped_column(BigInteger)

    def __repr__(self) -> str:
        return (
            f"Question(question_id={self.question_id}, content={self.content[:30]}, "
            f"chapter_name={self.chapter_name})"
        )
