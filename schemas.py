from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool


class StudentCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    student_id: str = Field(min_length=1, max_length=20)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    nfc_uid: str = Field(min_length=1, max_length=32)
    status: Literal["ACTIVE", "INACTIVE", "SUSPENDED"] = "ACTIVE"


class StudentUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    nfc_uid: str = Field(min_length=1, max_length=32)
    status: Literal["ACTIVE", "INACTIVE", "SUSPENDED"]


class StudentResponse(StudentCreate):
    model_config = ConfigDict(from_attributes=True)


class AdminCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    admin_id: str = Field(min_length=1, max_length=20)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    nfc_uid: str = Field(min_length=1, max_length=32)
    status: Literal["ACTIVE", "INACTIVE", "SUSPENDED"] = "ACTIVE"


class AdminUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    nfc_uid: str = Field(min_length=1, max_length=32)
    status: Literal["ACTIVE", "INACTIVE", "SUSPENDED"]


class AdminResponse(AdminCreate):
    model_config = ConfigDict(from_attributes=True)


class ItemCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    item_id: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=150)
    item_type: Literal["BOOK", "BOARD_GAME", "EQUIPMENT"]
    description: str | None = None


class ItemUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=1, max_length=150)
    item_type: Literal["BOOK", "BOARD_GAME", "EQUIPMENT"]
    description: str | None = None


class ItemResponse(ItemCreate):
    model_config = ConfigDict(from_attributes=True)


class ItemCopyCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    item_copy_id: str = Field(min_length=1, max_length=30)
    item_id: str = Field(min_length=1, max_length=20)
    nfc_uid: str = Field(min_length=1, max_length=32)
    status: Literal["AVAILABLE", "MAINTENANCE"] = "AVAILABLE"


class ItemCopyUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    nfc_uid: str = Field(min_length=1, max_length=32)
    status: Literal["AVAILABLE", "MAINTENANCE"]


class ItemCopyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_copy_id: str
    item_id: str
    nfc_uid: str
    status: Literal["AVAILABLE", "BORROWED", "MAINTENANCE"]


class LoanItemCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    loan_item_id: str = Field(min_length=1, max_length=30)
    item_copy_id: str = Field(min_length=1, max_length=30)


class LoanCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    loan_id: str = Field(min_length=1, max_length=30)
    student_id: str = Field(min_length=1, max_length=20)
    photo_path: str = Field(min_length=1)
    items: list[LoanItemCreate] = Field(min_length=1)


class LoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    loan_id: str
    student_id: str
    borrowed_at: datetime
    photo_path: str


class LoanItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    loan_item_id: str
    loan_id: str
    item_copy_id: str
    due_at: datetime
    returned_at: datetime | None


class ReturnRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sensor_confirmed: StrictBool
