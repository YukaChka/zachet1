from pydantic import BaseModel, Field

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class CharacterOut(BaseModel):
    name: str
    race: str
    class_: str = Field(..., alias="class")  # alias нужен для правильного маппинга поля class
    background: str
    subclass: str
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    portrait: str | None = None
    skills: str | None = None
    features: str | None = None

    class Config:
        allow_population_by_field_name = True  # Позволяет использовать class_ при возврате
