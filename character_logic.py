import random
import json
import os
from translate import Translator
from duckduckgo_search import DDGS
import requests
from PIL import Image, ImageEnhance
import pywhatkit as kit

# === ПЕРЕВОДЧИК ===
translator = Translator(from_lang="en", to_lang="ru")
translate_cache = {}

def translate(text):
    if text in translate_cache:
        return translate_cache[text]
    try:
        translated = translator.translate(text)
        translate_cache[text] = translated
        return translated
    except Exception:
        return text

# === ЗАГРУЗКА JSON ===
def load_local_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def load_all_class_files(folder):
    classes = []
    for filename in os.listdir(folder):
        if filename.startswith("class-") and filename.endswith(".json"):
            with open(os.path.join(folder, filename), encoding="utf-8") as f:
                data = json.load(f)
                if "class" in data:
                    classes.extend(data["class"])
    return classes

races_data = load_local_json("data/races.json")["race"]
classes_data = load_all_class_files("data/class")
backgrounds_data = load_local_json("data/backgrounds.json")["background"]

# === ИМЯ ===
funny_name_prefixes = ["Гр", "Бл", "Кр", "Тр", "Шн", "Фл", "Жу", "Хр", "Зл"]
funny_name_cores = ["ар", "ог", "ил", "уз", "эн", "ум", "аф", "ир", "эч"]
funny_name_suffixes = ["зик", "дыр", "макс", "ун", "чик", "боб", "лог", "шак"]

def generate_funny_name():
    return random.choice(funny_name_prefixes) + random.choice(funny_name_cores) + random.choice(funny_name_suffixes)

# === ASCII-ПОРТРЕТ ===
def get_ascii_portrait(prompt):
    try:
        with DDGS() as ddgs:
            results = ddgs.images(prompt, max_results=10, size='Small')
            image_url = None
            for res in results:
                if 'image' in res:
                    image_url = res["image"]
                    break

        if not image_url:
            raise ValueError("Нет изображения")

        response = requests.get(image_url, headers={"User-Agent": "Mozilla/5.0"})
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("image"):
            raise ValueError("Не изображение")

        with open("portrait.png", "wb") as f:
            f.write(response.content)

        image = Image.open("portrait.png").convert("RGB")
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        image.save("portrait_contrast.png")

        kit.image_to_ascii_art("portrait_contrast.png", "portrait_ascii")

        with open("portrait_ascii.txt", "r", encoding="utf-8") as f:
            return f.read()

    except Exception:
        return "[Не удалось загрузить портрет]"

# === ХАРАКТЕРИСТИКИ ===
def roll_stat():
    rolls = [random.randint(1, 6) for _ in range(4)]
    return sum(sorted(rolls)[1:])

def generate_stats():
    return {
        "Сила": roll_stat(),
        "Ловкость": roll_stat(),
        "Телосложение": roll_stat(),
        "Интеллект": roll_stat(),
        "Мудрость": roll_stat(),
        "Харизма": roll_stat()
    }

# === ГЕНЕРАЦИЯ ПЕРСОНАЖА ===
def generate_character_data():
    name = generate_funny_name()
    race = random.choice(races_data)
    cls = random.choice(classes_data)
    bg = random.choice(backgrounds_data)

    stats = generate_stats()

    # навыки
    selected_skills = []
    if 'skillProficiencies' in cls:
        skill_info = cls['skillProficiencies'].get('choose', {})
        count = skill_info.get('count', 0)
        options = skill_info.get('from', [])
        selected_skills = random.sample(options, min(count, len(options)))

    # умения
    features = [f["name"] for f in cls.get("classFeatures", [[]])[0]]

    # подкласс
    subclasses = cls.get("subclasses", [])
    chosen_subclass = random.choice(subclasses) if subclasses else {"name": "Без подкласса"}

    # портрет
    portrait = get_ascii_portrait(f"fantasy portrait of a {race['name']} {cls['name']}, close-up, DnD style")

    return {
        "name": name,
        "race": translate(race["name"]),
        "class": cls["name"],
        "background": translate(bg["name"]),
        "subclass": translate(chosen_subclass["name"]),
        "stats": stats,
        "portrait": portrait,
        "skills": [translate(s.title()) for s in selected_skills],
        "features": [translate(f) for f in features]
    }
