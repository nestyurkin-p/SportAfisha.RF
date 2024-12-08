from pydantic import BaseModel, EmailStr, UUID4, Field
from datetime import date

class AthleteBase(BaseModel):
    id: UUID4 = Field(..., example="123e4567-e89b-42d3-a456-426614174000", description="UUID версии 4 для уникальной идентификации спортсмена")
    name: str = Field(..., example="Иван Иванов Иванович")
    location: str = Field(..., example="Москва")
    email: EmailStr = Field(..., example="ivan.ivanov@example.com")
    UIN: str = Field(..., example="GTO001")
    birth_date: date = Field(..., example="1990-05-20")
    phone_number: str = Field(..., example="+79001234567")

class AthleteCreate(AthleteBase):
    pass

class AthleteUpdate(BaseModel):
    id: UUID4 = Field(..., example="123e4567-e89b-42d3-a456-426614174000", description="UUID версии 4 для уникальной идентификации спортсмена")
    name: str = Field(None, example="Иван Иванов Иванович")
    # last_name: str = Field(None, example="Иванов")
    # patronymic: str = Field(None, example="Иванович")
    location: str = Field(None, example="Москва")
    email: EmailStr = Field(None, example="ivan.ivanov@example.com")
    UIN: str = Field(None, example="GTO001")
    birth_date: date = Field(None, example="1990-05-20")
    phone_number: str = Field(None, example="+79001234567")

class AthleteInDB(AthleteBase):
    class Config:
        from_attributes = True

class StatusResponse(BaseModel):
    status: str = Field(..., example="OK", description="Статус выполнения операции")
    id: UUID4 = Field(..., example="123e4567-e89b-42d3-a456-426614174000", description="UUID созданного спортсмена")