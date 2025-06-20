import json
from pathlib import Path
from datetime import datetime

class AppContext:
    def __init__(self):
        config_directory = Path("config")
        self.config_path = config_directory / "config.json"
        self.translates_path = config_directory / "translates.json"
        self.languages_path = config_directory / "languages.json"

        self.ffmpeg_installed = None
        self.logs = []

        self.config_raw = {}
        self.translates_raw = {}
        self.languages_raw = {}

        self.listener_manager = ListenerManager()

        self._load_config()
        self._load_translations()
        self._load_languages()

    # ---------- CONFIG ----------

    def _load_config(self):
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config_raw = json.load(f)
        else:
            self.config_raw = {
                "global": {},
                "shared": {},
                "apps": {}
            }

    def get_config(self, app_name=None):
        if app_name is None:
            return self.config_raw

        result = {}
        global_config = self.config_raw.get("global", {})
        shared_config = self.config_raw.get("shared", {})
        app_specific = self.config_raw.get("apps", {}).get(app_name, {})

        result.update(global_config)

        for key, entry in shared_config.items():
            apps = entry.get("apps", [])
            if app_name in apps:
                result[key] = entry.get("value")

        result.update(app_specific)

        return result

    def update_global_config(self, updates: dict):
        if "global" not in self.config_raw:
            self.config_raw["global"] = {}

        self.config_raw["global"].update(updates)
        self.save_config()

        # Якщо змінилась мова — повідомляємо слухачів
        if "language" in updates:
            self.listener_manager.notify_listeners('language')

    def update_app_config(self, app_name, updates: dict):
        if "apps" not in self.config_raw:
            self.config_raw["apps"] = {}
        if app_name not in self.config_raw["apps"]:
            self.config_raw["apps"][app_name] = {}

        self.config_raw["apps"][app_name].update(updates)
        self.save_config()

        self.listener_manager.notify_listeners('config', app_name)

    def save_config(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config_raw, f, indent=2, ensure_ascii=False)

    # ---------- TRANSLATIONS ----------

    def _load_translations(self):
        if self.translates_path.exists():
            with open(self.translates_path, "r", encoding="utf-8") as f:
                self.translates_raw = json.load(f)
        else:
            self.translates_raw = {}

    def get_translate(self, lang, app, group, key, default=""):
        """
        Повертає переклад для:
        - мови `lang`
        - програми `app` (наприклад, "FB2ToMP3App")
        - групи елементів `group` (label, button, ...)
        - ключа `key` (внутрішній id перекладного тексту)
        """
        return (
            self.translates_raw.get(lang, {})
            .get(app, {})
            .get(group, {})
            .get(key, default)
        )

    # ---------- LANGUAGES ----------

    def _load_languages(self):
        if self.languages_path.exists():
            with open(self.languages_path, "r", encoding="utf-8") as f:
                self.languages_raw = json.load(f)
        else:
            self.languages_raw = {}


    def get_languages(self) -> dict:
        """
        Повертає словник усіх мов, наприклад: { "uk": { "name": "Українська" }, "en": { "name": "Англійська" } }
        """
        return self.languages_raw

    def get_language_name(self, code: str, default="") -> str:
        """
        Повертає назву мови за кодом (наприклад "uk" → "Українська")
        """
        return self.languages_raw.get(code, {}).get("name", default or code)

    # @property
    def get_current_language(self) -> str:
        return self.config_raw.get("global", {}).get("language", "uk")

    # ---------- LOGS ----------

    def add_log(self, message: str):
        """
        Додає повідомлення до логів та сповіщає слухачів.
        """
        self.logs.append(message)
        self.listener_manager.notify_listeners('logs')

    def write_log_file(self, filename=None):
        """
        Записує всі логи у файл. Якщо filename не вказано — створює з поточною датою.
        """
        if not self.logs:
            print("[ℹ️] Логи порожні. Немає чого записувати.")
            return

        if filename is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"logs/log_{timestamp}.txt"

        # Створення директорії, якщо вона відсутня
        log_path = Path(filename)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("\n".join(self.logs))
            print(f"[✅] Логи збережено у файл: {log_path}")
        except Exception as e:
            print(f"[❌] Не вдалося зберегти логи: {e}")


class ListenerManager:
    def __init__(self):
        self._listeners = {
            'language': [],
            'config': [],
            'logs': []
        }

    def register_listener(self, callback: callable, listener_type: str):
        if listener_type not in self._listeners:
            raise ValueError("Invalid listener type. Use 'language' or 'config'.")

        if callback not in self._listeners[listener_type]:
            self._listeners[listener_type].append(callback)

    def notify_listeners(self, listener_type: str, *args):
        if listener_type not in self._listeners:
            raise ValueError("Invalid listener type. Use 'language' or 'config'.")

        for callback in self._listeners[listener_type]:
            try:
                callback(*args)
            except Exception as e:
                print(f"[⚠️] {listener_type.capitalize()} listener error: {e}")