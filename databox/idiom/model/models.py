from sqlalchemy import String, BigInteger, Text, func, DateTime, Boolean, INT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    create_time = mapped_column(DateTime, insert_default=func.now())
    update_time = mapped_column(DateTime, insert_default=func.now(), onupdate=func.now())
    is_deleted = mapped_column(Boolean, default=False)


class Idiom(Base):
    __tablename__ = "land_idiom"

    id: Mapped[int] = mapped_column(BigInteger)
    word = mapped_column(String(100))
    pinyin = mapped_column(String(100))
    emotion = mapped_column(INT)
    meaning = mapped_column(Text)
    origin = mapped_column(Text)
    usage = mapped_column(Text)
    example = mapped_column(Text)
    distinction = mapped_column(Text)
    story = mapped_column(Text)
    explanation = mapped_column(Text)
    example_sentences = mapped_column(Text)
    last_update_time = mapped_column(DateTime)
