from pydantic import BaseModel, ConfigDict

#------ Student ------------------------------------------
class StudentCreate(BaseModel):
    student_id: str
    first_name: str
    last_name: str
    nfc_uid: str

class StudentResponse(BaseModel):
    student_id: str
    first_name: str
    last_name: str
    nfc_uid: str
    status: str

    model_config = ConfigDict(from_attributes=True)

class StudentUpdate(BaseModel):
    first_name: str
    last_name: str
    nfc_uid: str
    status: str
#-----------------------------------------------------