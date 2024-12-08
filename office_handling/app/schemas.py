from pydantic import BaseModel, EmailStr, UUID4, Field


class OfficeBase(BaseModel):
    # id: UUID4 = Field(
    #     ...,
    #     example="123e4567-e89b-42d3-a456-426614174000",
    #     description="UUID версии 4 для уникальной идентификации спортсмена",
    # )
    federal_district: str = Field(..., example="Москва")
    region: str = Field(..., example="Москва")
    email: EmailStr = Field(..., example="ivan.ivanov@example.com")
    director_name: str = Field(..., example="Иван Иванов Иванович")


class OfficeCreate(OfficeBase):
    pass


class OfficeUpdate(BaseModel):
    id: UUID4 = Field(
        ...,
        example="123e4567-e89b-42d3-a456-426614174000",
        description="UUID версии 4 для уникальной идентификации спортсмена",
    )
    federal_district: str = Field(None, example="Москва")
    region: str = Field(None, example="Москва")
    email: EmailStr = Field(None, example="ivan.ivanov@example.com")
    director_name: str = Field(None, example="Иван Иванов Иванович")


class OfficeInDB(OfficeBase):
    class Config:
        from_attributes = True


class StatusResponse(BaseModel):
    status: str = Field(..., example="OK", description="Статус выполнения операции")
    id: UUID4 = Field(
        ...,
        example="123e4567-e89b-42d3-a456-426614174000",
        description="UUID созданного спортсмена",
    )


class OfficeDelete(BaseModel):
    id: UUID4 = Field(
        ...,
        example="123e4567-e89b-42d3-a456-426614174000",
        description="UUID атлета для удаления",
    )
