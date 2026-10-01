from fastapi import FastAPI, HTTPException

from sqlalchemy import select
from sqlalchemy.orm import Session

#----------------------------------
from database import engine
from models import Student
from schemas import StudentCreate, StudentResponse, StudentUpdate
#----------------------------------

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Smart Lending API is running"}


#================ Student ==================================
@app.get(
    "/students",
    response_model=list[StudentResponse]
)
def get_students():

    with Session(engine) as session:

        students = session.scalars(
            select(Student)
        ).all()

        return students

@app.get(
        "/students/{student_id}",
        response_model=StudentResponse
        )
def get_stedents_byID(student_id:str):

    with Session(engine) as session:

        student = session.get(Student, student_id)

        if student is None:
            raise HTTPException(
                status_code=404,
                detail="Student not found"
            )

        return student
    
@app.post("/students")
def create_student(data: StudentCreate):

    with Session(engine) as session:

        student = Student(
            student_id=data.student_id,
            first_name=data.first_name,
            last_name=data.last_name,
            nfc_uid=data.nfc_uid
        )

        session.add(student)
        session.commit()
        session.refresh(student)

        return {
            "student_id": student.student_id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "nfc_uid": student.nfc_uid,
            "status": student.status
        }

@app.put(
    "/students/{student_id}",
    response_model=StudentResponse
)
def update_student(student_id: str, data: StudentUpdate):

    with Session(engine) as session:

        student = session.get(Student, student_id)

        if student is None:
            raise HTTPException(
                status_code=404,
                detail="Student not found"
            )

        student.first_name = data.first_name
        student.last_name = data.last_name
        student.nfc_uid = data.nfc_uid
        student.status = data.status

        session.commit()
        session.refresh(student)

        return student

#==========================================================
