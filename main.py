from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import engine
from models import Student, Item, ItemCopy, Admin, Loan, LoanItem
from schemas import (
    StudentCreate, StudentUpdate, StudentResponse,
    ItemCreate, ItemUpdate, ItemResponse,
    ItemCopyCreate, ItemCopyUpdate, ItemCopyResponse,
    AdminCreate, AdminUpdate, AdminResponse,
    LoanCreate, LoanResponse, LoanItemResponse, ReturnRequest,StudentPasswordUpdate, StudentLogin
)

app = FastAPI(title="Smart Lending API - Simple")


# รองรับกรณีฐานข้อมูลพบข้อมูลซ้ำ หรือข้อมูลยังถูกอ้างอิงอยู่
@app.exception_handler(IntegrityError)
def database_conflict(request: Request, error: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={"detail": "Duplicate data or record is still referenced"},
    )


# นักศึกษา

@app.post("/students", response_model=StudentResponse, status_code=201, tags=["students"])
def create_student(data: StudentCreate):
    with Session(engine) as session:
        existing = session.get(Student, data.student_id)
        if existing is not None:
            raise HTTPException(status_code=409, detail="Student ID already exists")

        statement = select(Student).where(Student.nfc_uid == data.nfc_uid)
        existing_nfc = session.scalars(statement).first()
        if existing_nfc is not None:
            raise HTTPException(status_code=409, detail="NFC UID already exists")

        student = Student(
            student_id=data.student_id,
            first_name=data.first_name,
            last_name=data.last_name,
            nfc_uid=data.nfc_uid,
            status=data.status,
        )
        session.add(student)
        session.commit()
        session.refresh(student)
        return student


@app.get("/students", response_model=list[StudentResponse], tags=["students"])
def list_students():
    with Session(engine) as session:
        statement = select(Student).order_by(Student.student_id)
        return session.scalars(statement).all()


@app.get("/students/{student_id}", response_model=StudentResponse, tags=["students"])
def get_student(student_id: str):
    with Session(engine) as session:
        student = session.get(Student, student_id)
        if student is None:
            raise HTTPException(status_code=404, detail="Student not found")
        return student


@app.put("/students/{student_id}", response_model=StudentResponse, tags=["students"])
def update_student(student_id: str, data: StudentUpdate):
    with Session(engine) as session:
        student = session.get(Student, student_id, with_for_update=True)
        if student is None:
            raise HTTPException(status_code=404, detail="Student not found")

        statement = select(Student).where(Student.nfc_uid == data.nfc_uid)
        existing_nfc = session.scalars(statement).first()
        if existing_nfc is not None and existing_nfc.student_id != student_id:
            raise HTTPException(status_code=409, detail="NFC UID already exists")

        student.first_name = data.first_name
        student.last_name = data.last_name
        student.nfc_uid = data.nfc_uid
        student.status = data.status

        session.commit()
        session.refresh(student)
        return student


@app.delete("/students/{student_id}", status_code=204, tags=["students"])
def delete_student(student_id: str):
    with Session(engine) as session:
        student = session.get(Student, student_id, with_for_update=True)
        if student is None:
            raise HTTPException(status_code=404, detail="Student not found")

        statement = select(Loan).where(Loan.student_id == student_id)
        related_record = session.scalars(statement).first()
        if related_record is not None:
            raise HTTPException(status_code=409, detail="This record is still used by Loan")

        session.delete(student)
        session.commit()
        return Response(status_code=204)


# สิ่งของ

@app.post("/items", response_model=ItemResponse, status_code=201, tags=["items"])
def create_item(data: ItemCreate):
    with Session(engine) as session:
        existing = session.get(Item, data.item_id)
        if existing is not None:
            raise HTTPException(status_code=409, detail="Item ID already exists")

        item = Item(
            item_id=data.item_id,
            name=data.name,
            item_type=data.item_type,
            description=data.description,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


@app.get("/items", response_model=list[ItemResponse], tags=["items"])
def list_items():
    with Session(engine) as session:
        statement = select(Item).order_by(Item.item_id)
        return session.scalars(statement).all()


@app.get("/items/{item_id}", response_model=ItemResponse, tags=["items"])
def get_item(item_id: str):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return item


@app.put("/items/{item_id}", response_model=ItemResponse, tags=["items"])
def update_item(item_id: str, data: ItemUpdate):
    with Session(engine) as session:
        item = session.get(Item, item_id, with_for_update=True)
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")

        item.name = data.name
        item.item_type = data.item_type
        item.description = data.description

        session.commit()
        session.refresh(item)
        return item


@app.delete("/items/{item_id}", status_code=204, tags=["items"])
def delete_item(item_id: str):
    with Session(engine) as session:
        item = session.get(Item, item_id, with_for_update=True)
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")

        statement = select(ItemCopy).where(ItemCopy.item_id == item_id)
        related_record = session.scalars(statement).first()
        if related_record is not None:
            raise HTTPException(status_code=409, detail="This record is still used by ItemCopy")

        session.delete(item)
        session.commit()
        return Response(status_code=204)


# สิ่งของแต่ละชิ้น

@app.post("/item-copies", response_model=ItemCopyResponse, status_code=201, tags=["item_copies"])
def create_item_copy(data: ItemCopyCreate):
    with Session(engine) as session:
        existing = session.get(ItemCopy, data.item_copy_id)
        if existing is not None:
            raise HTTPException(status_code=409, detail="ItemCopy ID already exists")

        statement = select(ItemCopy).where(ItemCopy.nfc_uid == data.nfc_uid)
        existing_nfc = session.scalars(statement).first()
        if existing_nfc is not None:
            raise HTTPException(status_code=409, detail="NFC UID already exists")

        item = session.get(Item, data.item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")

        item_copy = ItemCopy(
            item_copy_id=data.item_copy_id,
            item_id=data.item_id,
            nfc_uid=data.nfc_uid,
            status=data.status,
        )
        session.add(item_copy)
        session.commit()
        session.refresh(item_copy)
        return item_copy


@app.get("/item-copies", response_model=list[ItemCopyResponse], tags=["item_copies"])
def list_item_copies():
    with Session(engine) as session:
        statement = select(ItemCopy).order_by(ItemCopy.item_copy_id)
        return session.scalars(statement).all()


@app.get("/item-copies/{item_copy_id}", response_model=ItemCopyResponse, tags=["item_copies"])
def get_item_copy(item_copy_id: str):
    with Session(engine) as session:
        item_copy = session.get(ItemCopy, item_copy_id)
        if item_copy is None:
            raise HTTPException(status_code=404, detail="ItemCopy not found")
        return item_copy


@app.put("/item-copies/{item_copy_id}", response_model=ItemCopyResponse, tags=["item_copies"])
def update_item_copy(item_copy_id: str, data: ItemCopyUpdate):
    with Session(engine) as session:
        item_copy = session.get(ItemCopy, item_copy_id, with_for_update=True)
        if item_copy is None:
            raise HTTPException(status_code=404, detail="ItemCopy not found")

        statement = select(LoanItem).where(
            LoanItem.item_copy_id == item_copy_id,
            LoanItem.returned_at.is_(None),
        )
        active_loan = session.scalars(statement).first()
        if item_copy.status == "BORROWED" or active_loan is not None:
            raise HTTPException(status_code=409, detail="Return this copy before editing it")

        statement = select(ItemCopy).where(ItemCopy.nfc_uid == data.nfc_uid)
        existing_nfc = session.scalars(statement).first()
        if existing_nfc is not None and existing_nfc.item_copy_id != item_copy_id:
            raise HTTPException(status_code=409, detail="NFC UID already exists")

        item_copy.nfc_uid = data.nfc_uid
        item_copy.status = data.status

        session.commit()
        session.refresh(item_copy)
        return item_copy


@app.delete("/item-copies/{item_copy_id}", status_code=204, tags=["item_copies"])
def delete_item_copy(item_copy_id: str):
    with Session(engine) as session:
        item_copy = session.get(ItemCopy, item_copy_id, with_for_update=True)
        if item_copy is None:
            raise HTTPException(status_code=404, detail="ItemCopy not found")

        statement = select(LoanItem).where(LoanItem.item_copy_id == item_copy_id)
        related_record = session.scalars(statement).first()
        if related_record is not None:
            raise HTTPException(status_code=409, detail="This record is still used by LoanItem")

        if item_copy.status == "BORROWED":
            raise HTTPException(status_code=409, detail="Cannot delete a borrowed copy")

        session.delete(item_copy)
        session.commit()
        return Response(status_code=204)


# ผู้ดูแล

@app.post("/admins", response_model=AdminResponse, status_code=201, tags=["admins"])
def create_admin(data: AdminCreate):
    with Session(engine) as session:
        existing = session.get(Admin, data.admin_id)
        if existing is not None:
            raise HTTPException(status_code=409, detail="Admin ID already exists")

        statement = select(Admin).where(Admin.nfc_uid == data.nfc_uid)
        existing_nfc = session.scalars(statement).first()
        if existing_nfc is not None:
            raise HTTPException(status_code=409, detail="NFC UID already exists")

        admin = Admin(
            admin_id=data.admin_id,
            first_name=data.first_name,
            last_name=data.last_name,
            nfc_uid=data.nfc_uid,
            status=data.status,
        )
        session.add(admin)
        session.commit()
        session.refresh(admin)
        return admin


@app.get("/admins", response_model=list[AdminResponse], tags=["admins"])
def list_admins():
    with Session(engine) as session:
        statement = select(Admin).order_by(Admin.admin_id)
        return session.scalars(statement).all()


@app.get("/admins/{admin_id}", response_model=AdminResponse, tags=["admins"])
def get_admin(admin_id: str):
    with Session(engine) as session:
        admin = session.get(Admin, admin_id)
        if admin is None:
            raise HTTPException(status_code=404, detail="Admin not found")
        return admin


@app.put("/admins/{admin_id}", response_model=AdminResponse, tags=["admins"])
def update_admin(admin_id: str, data: AdminUpdate):
    with Session(engine) as session:
        admin = session.get(Admin, admin_id, with_for_update=True)
        if admin is None:
            raise HTTPException(status_code=404, detail="Admin not found")

        statement = select(Admin).where(Admin.nfc_uid == data.nfc_uid)
        existing_nfc = session.scalars(statement).first()
        if existing_nfc is not None and existing_nfc.admin_id != admin_id:
            raise HTTPException(status_code=409, detail="NFC UID already exists")

        admin.first_name = data.first_name
        admin.last_name = data.last_name
        admin.nfc_uid = data.nfc_uid
        admin.status = data.status

        session.commit()
        session.refresh(admin)
        return admin


@app.delete("/admins/{admin_id}", status_code=204, tags=["admins"])
def delete_admin(admin_id: str):
    with Session(engine) as session:
        admin = session.get(Admin, admin_id, with_for_update=True)
        if admin is None:
            raise HTTPException(status_code=404, detail="Admin not found")

        session.delete(admin)
        session.commit()
        return Response(status_code=204)


# ยืมและคืน

# ระยะเวลายืมเป็นวัน แก้กติกาได้ตรงนี้
BORROW_DAYS = {"BOOK": 30, "BOARD_GAME": 7, "EQUIPMENT": 7}


@app.post("/loans", response_model=LoanResponse, status_code=201, tags=["loans"])
def create_loan(data: LoanCreate):
    with Session(engine) as session:
        # 1. ตรวจ ID และนักศึกษา
        if session.get(Loan, data.loan_id) is not None:
            raise HTTPException(status_code=409, detail="Loan ID already exists")

        student = session.get(Student, data.student_id, with_for_update=True)
        if student is None:
            raise HTTPException(status_code=404, detail="Student not found")
        if student.status != "ACTIVE":
            raise HTTPException(status_code=409, detail="Student must be ACTIVE")

        copy_ids = [entry.item_copy_id for entry in data.items]
        entry_ids = [entry.loan_item_id for entry in data.items]
        if len(copy_ids) != len(set(copy_ids)) or len(entry_ids) != len(set(entry_ids)):
            raise HTTPException(status_code=400, detail="Repeated copy or loan item ID")

        # 2. สร้างหัวรายการยืม ยังไม่ commit
        borrowed_at = datetime.now(timezone.utc)
        loan = Loan(
            loan_id=data.loan_id,
            student_id=data.student_id,
            borrowed_at=borrowed_at,
            photo_path=data.photo_path,
        )
        session.add(loan)
        session.flush()  # ส่งหัวรายการเข้า transaction ก่อนเพิ่มรายการย่อย

        # 3. ตรวจของแต่ละชิ้น แล้วเพิ่ม LoanItem
        # เรียงก่อนล็อก ป้องกันคำขอยืมหลายชิ้นพร้อมกันล็อกสลับลำดับ
        for entry in sorted(data.items, key=lambda row: row.item_copy_id):
            if session.get(LoanItem, entry.loan_item_id) is not None:
                raise HTTPException(status_code=409, detail="Loan item ID already exists")

            # with_for_update ให้คำขออื่นรอจนการแก้ไขชิ้นนี้เสร็จ
            copy = session.get(ItemCopy, entry.item_copy_id, with_for_update=True)
            if copy is None:
                raise HTTPException(status_code=404, detail="Item copy not found")
            if copy.status != "AVAILABLE":
                raise HTTPException(status_code=409, detail="Item copy is not AVAILABLE")

            statement = select(LoanItem).where(
                LoanItem.item_copy_id == copy.item_copy_id,
                LoanItem.returned_at.is_(None),
            )
            if session.scalars(statement).first() is not None:
                raise HTTPException(status_code=409, detail="Item copy already has an active loan")

            item = session.get(Item, copy.item_id)
            if item is None:
                raise HTTPException(status_code=404, detail="Item not found")
            if item.item_type not in BORROW_DAYS:
                raise HTTPException(status_code=400, detail="Unknown item type")

            loan_item = LoanItem(
                loan_item_id=entry.loan_item_id,
                loan_id=data.loan_id,
                item_copy_id=entry.item_copy_id,
                due_at=borrowed_at + timedelta(days=BORROW_DAYS[item.item_type]),
                returned_at=None,
            )
            session.add(loan_item)
            copy.status = "BORROWED"

        # 4. บันทึกทุกชิ้นพร้อมกัน ถ้าเกิด error ก่อนนี้ Session จะ rollback
        session.commit()
        session.refresh(loan)
        return loan


@app.get("/loans", response_model=list[LoanResponse], tags=["loans"])
def list_loans():
    with Session(engine) as session:
        statement = select(Loan).order_by(Loan.borrowed_at.desc())
        return session.scalars(statement).all()


@app.get("/loans/{loan_id}", response_model=LoanResponse, tags=["loans"])
def get_loan(loan_id: str):
    with Session(engine) as session:
        loan = session.get(Loan, loan_id)
        if loan is None:
            raise HTTPException(status_code=404, detail="Loan not found")
        return loan


@app.get("/loans/{loan_id}/items", response_model=list[LoanItemResponse], tags=["loans"])
def get_loan_items(loan_id: str):
    with Session(engine) as session:
        if session.get(Loan, loan_id) is None:
            raise HTTPException(status_code=404, detail="Loan not found")
        statement = select(LoanItem).where(LoanItem.loan_id == loan_id)
        return session.scalars(statement).all()


@app.post("/loan-items/{loan_item_id}/return", response_model=LoanItemResponse, tags=["loans"])
def return_item(loan_item_id: str, data: ReturnRequest):
    # Raspberry Pi ต้องเรียกหลังเซ็นเซอร์ยืนยันว่าคืนของจริงแล้ว
    if not data.sensor_confirmed:
        raise HTTPException(status_code=400, detail="Wait for sensor confirmation")

    with Session(engine) as session:
        loan_item = session.get(LoanItem, loan_item_id)
        if loan_item is None:
            raise HTTPException(status_code=404, detail="Loan item not found")

        copy = session.get(ItemCopy, loan_item.item_copy_id, with_for_update=True)
        if copy is None:
            raise HTTPException(status_code=404, detail="Item copy not found")
        session.refresh(loan_item)  # อ่านล่าสุด หลังรอคำขออื่นทำงานเสร็จ

        if loan_item.returned_at is not None:
            raise HTTPException(status_code=409, detail="Already returned")
        if copy.status != "BORROWED":
            raise HTTPException(status_code=409, detail="Item copy is not BORROWED")

        loan_item.returned_at = datetime.now(timezone.utc)
        copy.status = "AVAILABLE"

        session.commit()
        session.refresh(loan_item)
        return loan_item

@app.put("/students/{student_id}/password", response_model=StudentResponse, tags=["students"])
def set_student_password(student_id: str, data: StudentPasswordUpdate):
    with Session(engine) as session:
        student = session.get(Student, student_id)
        if student is None:
            raise HTTPException(status_code=404, detail="Student not found")

        student.password = data.password
        session.commit()
        session.refresh(student)
        return student


@app.post("/student/login", response_model=StudentResponse, tags=["students"])
def login_student(data: StudentLogin):
    with Session(engine) as session:
        student = session.get(Student, data.student_id)
        if student is None or student.password != data.password:
            raise HTTPException(status_code=401, detail="Invalid student ID or password")
        return student
