import json
from pathlib import Path


def load_config(app_name=None, config_path="config.json"):
    """
    Завантажує конфігурацію. Якщо задано app_name — об’єднує глобальні, спільні та конкретні налаштування.

    :param app_name: Назва піддодатку, наприклад "fb2_to_mp3"
    :param config_path: Шлях до JSON-конфігурації
    :return: dict з конфігом для app або повна конфігурація
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Конфігураційний файл не знайдено: {config_path}")

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    if app_name is None:
        return config  # повертаємо повний конфіг

    result = {}

    # Глобальні
    global_config = config.get("global", {})
    result.update(global_config)

    # Спільні налаштування
    shared_config = config.get("shared", {})
    for key, entry in shared_config.items():
        apps = entry.get("apps", [])
        if app_name in apps:
            result[key] = entry.get("value")

    # Налаштування конкретного додатку
    app_specific = config.get("apps", {}).get(app_name, {})
    result.update(app_specific)

    return result

# приклад використання
# settings = load_config("fb2_to_mp3")
# print(settings)
# print(settings['language'])
