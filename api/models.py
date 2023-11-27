import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Course(Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(primary_key=True)
    exchange: Mapped[str]
    currency: Mapped[str]
    vs_currency: Mapped[str]
    rate: Mapped[float]
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self):
        return f"{self.exchange}:{self.currency}-{self.vs_currency}; {self.timestamp}"
