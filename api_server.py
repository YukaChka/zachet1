from fastapi import FastAPI, HTTPException
from db import get_connection
from models import UserRegister, UserLogin, CharacterOut
import hashlib
from character_logic import generate_character_data

app = FastAPI()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/register")
def register(user: UserRegister):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (user.username, hash_password(user.password))
        )
        conn.commit()
    except Exception:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    finally:
        cur.close()
        conn.close()
    return {"message": "Регистрация успешна"}

@app.post("/login")
def login(user: UserLogin):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (user.username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row or row[1] != hash_password(user.password):
        raise HTTPException(status_code=401, detail="Неверные данные")
    return {"message": "Успешный вход", "user_id": row[0]}

@app.post("/generate-character/{user_id}")
def generate_character(user_id: int):
    character = generate_character_data()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO characters (
            name, race, class, background, subclass,
            strength, dexterity, constitution, intelligence, wisdom, charisma,
            user_id, portrait, skills, features
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        character["name"],
        character["race"],
        character["class"],
        character["background"],
        character["subclass"],
        character["stats"]["Сила"],
        character["stats"]["Ловкость"],
        character["stats"]["Телосложение"],
        character["stats"]["Интеллект"],
        character["stats"]["Мудрость"],
        character["stats"]["Харизма"],
        user_id,
        character.get("portrait", ""),
        "\n".join(character.get("skills", [])),
        "\n".join(character.get("features", []))
    ))
    conn.commit()
    cur.close()
    conn.close()
    return character

@app.get("/characters/{user_id}", response_model=list[CharacterOut])
def get_characters(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT name, race, class, background, subclass,
               strength, dexterity, constitution, intelligence, wisdom, charisma,
               portrait, skills, features
        FROM characters WHERE user_id = %s
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [CharacterOut(
        name=row[0],
        race=row[1],
        class_=row[2],
        background=row[3],
        subclass=row[4],
        strength=row[5],
        dexterity=row[6],
        constitution=row[7],
        intelligence=row[8],
        wisdom=row[9],
        charisma=row[10],
        portrait=row[11],
        skills=row[12],
        features=row[13]
    ) for row in rows]
