"""Mappings to existing tables. No migrations or automatic table creation."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Student(Base):
    __tablename__ = "students"

    student_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    nfc_uid: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'ACTIVE'"))
    password: Mapped[str | None] = mapped_column(Text, nullable=True)


class Item(Base):
    __tablename__ = "items"

    item_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    item_type: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class ItemCopy(Base):
    __tablename__ = "item_copies"

    item_copy_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    item_id: Mapped[str] = mapped_column(String(20), ForeignKey("items.item_id"), nullable=False)
    nfc_uid: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'AVAILABLE'"))


class Loan(Base):
    __tablename__ = "loans"

    loan_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    student_id: Mapped[str] = mapped_column(String(20), ForeignKey("students.student_id"), nullable=False)
    borrowed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    photo_path: Mapped[str] = mapped_column(Text, nullable=False)



class LoanItem(Base):
    __tablename__ = "loan_items"
    __table_args__ = (UniqueConstraint("loan_id", "item_copy_id"),)

    loan_item_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    loan_id: Mapped[str] = mapped_column(String(30), ForeignKey("loans.loan_id"), nullable=False)
    item_copy_id: Mapped[str] = mapped_column(String(30), ForeignKey("item_copies.item_copy_id"), nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Admin(Base):
    __tablename__ = "admins"

    admin_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    nfc_uid: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'ACTIVE'"))
