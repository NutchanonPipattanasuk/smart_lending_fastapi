from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Student(Base):
    __tablename__ = "students"

    student_id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    nfc_uid: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'ACTIVE'")
    )