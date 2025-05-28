import psycopg2
import hashlib
from getpass import getpass
from db import get_connection
from character_logic import generate_character_data

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register():
    print("\n=== Регистрация ===")
    username = input("Придумайте логин: ")
    password = getpass("Придумайте пароль: ")

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                    (username, hash_password(password)))
        conn.commit()
        print("✅ Успешная регистрация!")
    except:
        print("❌ Пользователь уже существует.")
        return None
    finally:
        cur.close()
        conn.close()
    return login(username, password)

def login(existing_username=None, existing_password=None):
    print("\n=== Вход ===")
    username = existing_username or input("Логин: ")
    password = existing_password or getpass("Пароль: ")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and user[1] == hash_password(password):
        print(f"✅ Вход выполнен. Добро пожаловать, {username}!")
        return user[0]
    else:
        print("❌ Неверный логин или пароль.")
        return None

def save_character(character, user_id):
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

def list_characters(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM characters WHERE user_id = %s", (user_id,))
    characters = cur.fetchall()
    cur.close()
    conn.close()
    return characters

def get_character_by_id(char_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT name, race, class, background, subclass, strength, dexterity,
               constitution, intelligence, wisdom, charisma,
               portrait, skills, features
        FROM characters WHERE id = %s
    """, (char_id,))
    char = cur.fetchone()
    cur.close()
    conn.close()
    return char

def main_menu(user_id):
    while True:
        print("\n=== Главное меню ===")
        print("[1] Сгенерировать персонажа")
        print("[2] Посмотреть своих персонажей")
        print("[0] Выход")

        choice = input("Выбор: ")

        if choice == "1":
            character = generate_character_data()
            save_character(character, user_id)
            print(f"\n🧝 Сгенерирован персонаж: {character['name']}")
        elif choice == "2":
            chars = list_characters(user_id)
            if not chars:
                print("❌ У вас нет персонажей.")
                continue
            print("\nВаши персонажи:")
            for idx, (char_id, name) in enumerate(chars, start=1):
                print(f"[{idx}] {name}")
            selected = input("Выберите номер для просмотра (или 0 для выхода): ")
            if selected.isdigit() and 1 <= int(selected) <= len(chars):
                char_id = chars[int(selected) - 1][0]
                char = get_character_by_id(char_id)
                if char:
                    print("\n=== ПЕРСОНАЖ ===")
                    labels = ["Имя", "Раса", "Класс", "Предыстория", "Подкласс",
                              "Сила", "Ловкость", "Телосложение",
                              "Интеллект", "Мудрость", "Харизма",
                              "Портрет", "", "Умения"]
                    for label, val in zip(labels, char):
                        print(f"{label}: {val}")
        elif choice == "0":
            print("👋 До встречи!")
            break
        else:
            print("⚠️ Неверный выбор.")

if __name__ == "__main__":
    print("=== Добро пожаловать в DnD генератор персонажей ===")
    while True:
        print("\n[1] Войти")
        print("[2] Зарегистрироваться")
        print("[0] Выход")
        action = input("Выбор: ")

        if action == "1":
            uid = login()
            if uid:
                main_menu(uid)
        elif action == "2":
            uid = register()
            if uid:
                main_menu(uid)
        elif action == "0":
            break
        else:
            print("⚠️ Неверный выбор.")
