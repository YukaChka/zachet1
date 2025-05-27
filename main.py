import random
import json
import os
from colorama import init, Fore, Style
from translate import Translator
import pywhatkit as kit
import requests
import io
from duckduckgo_search import DDGS

init(autoreset=True)

# === ПЕРЕВОДЧИК НА MyMemory ===
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

# === ПОДГРУЗКА ЛОКАЛЬНЫХ JSON-ДАННЫХ ===
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

races_data = load_local_json("data/races.json")['race']
classes_data = load_all_class_files("data/class")
backgrounds_data = load_local_json("data/backgrounds.json")['background']

# === СЛУЧАЙНОЕ ИМЯ ===
funny_name_prefixes = ["Гр", "Бл", "Кр", "Тр", "Шн", "Фл", "Жу", "Хр", "Зл"]
funny_name_cores = ["ар", "ог", "ил", "уз", "эн", "ум", "аф", "ир", "эч"]
funny_name_suffixes = ["зик", "дыр", "макс", "ун", "чик", "боб", "лог", "шак"]

def generate_funny_name():
    return random.choice(funny_name_prefixes) + random.choice(funny_name_cores) + random.choice(funny_name_suffixes)

# === ASCII-КОНВЕРТАЦИЯ ИЗОБРАЖЕНИЯ ===
def show_ascii_portrait_by_prompt(prompt):
    try:
        print(f"[~] Поиск изображения для: {prompt}")
        with DDGS() as ddgs:
            results = ddgs.images(prompt, max_results=10, size='Small')
            if results:
                for res in results:
                    if 'image' in res:
                        image_url = res["image"]
                    break
            else:
                raise ValueError("Нет подходящих изображений")
            

        print(f"[+] Найдено изображение: {image_url}")
        response = requests.get(image_url, headers={"User-Agent": "Mozilla/5.0"})
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("image"):
            raise ValueError("Получен не графический файл")

        with open("portrait.png", "wb") as f:
            f.write(response.content)

        from PIL import Image, ImageEnhance

        # Повышаем контрастность
        image = Image.open("portrait.png").convert("RGB")
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)  # Увеличим контраст в 2 раза
        image.save("portrait_contrast.png")

        kit.image_to_ascii_art("portrait_contrast.png", "portrait_ascii")

        with open("portrait_ascii.txt", "r", encoding="utf-8") as f:
            print(f.read())

    except Exception as e:
        print(Fore.RED + f"[!] Ошибка при получении изображения: {e}")

# === ГЕНЕРАЦИЯ ХАРАКТЕРИСТИК ===
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
def generate_character():
    
    name = generate_funny_name()
    race = random.choice(races_data)
    cls = random.choice(classes_data)
    bg = random.choice(backgrounds_data)

    print(Fore.CYAN + Style.BRIGHT + f"\n===== ПЕРСОНАЖ: {name} =====\n")
    print(Fore.YELLOW + f"РАСА     : {translate(race['name'])}")
    print(Fore.YELLOW + f"КЛАСС    : {cls['name']}")
    print(Fore.YELLOW + f"ПРЕДЫСТОРИЯ: {translate(bg['name'])}\n")

    show_ascii_portrait_by_prompt(f"fantasy portrait of a {race['name']} {cls['name']}, close-up, simple background, DnD style")

    stats = generate_stats()
    print(Fore.WHITE + "=== ХАРАКТЕРИСТИКИ ===")
    for stat, value in stats.items():
        print(f" {stat}: {value}")

    print(Fore.GREEN + "=== ОПИСАНИЕ ===")
    print(f"{name} — {translate(race['name']).lower()}-{cls['name'].lower()} с предысторией {translate(bg['name']).lower()}.")

    if 'skillProficiencies' in cls:
        skill_info = cls['skillProficiencies'].get('choose', {})
        count = skill_info.get('count', 0)
        options = skill_info.get('from', [])
        selected_skills = random.sample(options, min(count, len(options)))

        print(Fore.BLUE + "\nНавыки от класса:")
        for skill in selected_skills:
            print(" -", translate(skill.title()))

    if 'classFeatures' in cls and cls['classFeatures']:
        print(Fore.MAGENTA + "\nУмения 1 уровня:")
        for feature in cls['classFeatures'][0]:
            print(" •", translate(feature['name']))

    subclasses = cls.get("subclasses", [])
    if subclasses:
        chosen_subclass = random.choice(subclasses)
        print(Fore.LIGHTCYAN_EX + f"\nПодкласс: {translate(chosen_subclass['name'])}")


    
if __name__ == "__main__":
    generate_character()
